"""
tests/test_voice_agent.py - Test Suite for Voice AI Agent Stack.

Verifies:
1. EnergyVAD: Speech frame detection and turn completion on silence.
2. MicrophoneStream & AudioPlayer: Buffer queuing and WAV serialization.
3. VocalAudioRenderer: Biophysical glottal waveform generation and formant filtering across scenarios.
4. VoiceAgentOrchestrator: Intent matching, 0-ns AMSV memory synchronization, and end-to-end processing.
"""

import os
import sys
import pytest
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine.brain.Analysis.vocal_cord_frequency_engine import (
    SituationalScenario,
    SpeakerRegisterCohort,
)
from voice_agent.audio_io import AudioConfig, EnergyVAD, MicrophoneStream, AudioPlayer
from voice_agent.vocal_audio_renderer import VocalAudioRenderer
from voice_agent.agent_orchestrator import VoiceAgentOrchestrator


def test_energy_vad_speech_and_turn_boundary():
    config = AudioConfig(sample_rate=16000, frame_duration_ms=30, silence_threshold_ms=150, energy_threshold_rms=200.0)
    vad = EnergyVAD(config=config)
    frame_samples = vad.frame_samples

    # 1. Create a silence frame
    silence_pcm = np.zeros(frame_samples, dtype=np.int16).tobytes()
    is_speech, is_turn_done, audio = vad.process_frame(silence_pcm)
    assert is_speech is False
    assert is_turn_done is False
    assert audio is None

    # 2. Create loud speech frames
    t = np.linspace(0, 0.03, frame_samples)
    speech_wave = (np.sin(2 * np.pi * 220 * t) * 8000.0).astype(np.int16)
    speech_pcm = speech_wave.tobytes()

    for _ in range(3):
        is_speech, is_turn_done, _ = vad.process_frame(speech_pcm)
        assert is_speech is True
        assert is_turn_done is False

    # 3. Deliver consecutive silence frames to trigger turn boundary
    # silence_frames_limit = 150ms / 30ms = 5 frames
    for _ in range(4):
        is_speech, is_turn_done, _ = vad.process_frame(silence_pcm)
        assert is_turn_done is False

    is_speech, is_turn_done, complete_audio = vad.process_frame(silence_pcm)
    assert is_turn_done is True
    assert complete_audio is not None
    assert len(complete_audio) > 0


def test_microphone_stream_and_audio_player():
    stream = MicrophoneStream()
    test_pcm = np.ones(480, dtype=np.int16).tobytes()

    stream.push_frame(test_pcm)
    read_frame = stream.read_frame(timeout=0.2)
    assert read_frame == test_pcm

    # WAV serialization
    wav_bytes = AudioPlayer.pcm_to_wav_bytes(test_pcm, sample_rate=16000)
    assert len(wav_bytes) > len(test_pcm)
    assert wav_bytes[:4] == b"RIFF"


def test_vocal_audio_renderer_waveforms():
    amsv = AMSVEmbeddedView()
    orchestrator = VoiceAgentOrchestrator(amsv_view=amsv)
    renderer = VocalAudioRenderer(sample_rate=16000)

    # Test rendering CALM_REASSURANCE
    tuning = orchestrator.vocal_engine.synthesize_vocal_tuning(
        text="It is completely okay.",
        scenario=SituationalScenario.CALM_REASSURANCE,
        speaker_cohort=SpeakerRegisterCohort.MEDIUM_REGISTER
    )
    pcm_bytes, meta = renderer.render_tuning_result(tuning, include_calibrated_silence=True)

    assert len(pcm_bytes) > 0
    assert meta["sample_rate"] == 16000
    assert meta["post_pause_ms"] == 518
    assert meta["duration_total_ms"] > 500

    # Test rendering WHISPER_SECRECY (Aperiodic noise, F0 = 0 Hz)
    tuning_whisper = orchestrator.vocal_engine.synthesize_vocal_tuning(
        text="Keep this completely secret.",
        scenario=SituationalScenario.WHISPER_SECRECY,
        speaker_cohort=SpeakerRegisterCohort.MEDIUM_REGISTER
    )
    pcm_whisper, meta_w = renderer.render_tuning_result(tuning_whisper)
    assert len(pcm_whisper) > 0
    assert meta_w["f0_mean_hz"] == 0.0


def test_voice_agent_orchestrator_end_to_end():
    amsv = AMSVEmbeddedView()
    agent = VoiceAgentOrchestrator(amsv_view=amsv)

    # Inbound directive query
    result = agent.process_utterance("Report status immediately.")

    assert result["matched_intent"] == "DIRECTIVE_ACKNOWLEDGMENT"
    assert any(tok in result["response_text"].lower() for tok in ["directive", "acknowledged", "instructions received", "understood"])
    assert result["calibrated_gap_ms"] == 518
    assert result["audio_pcm_bytes_len"] > 0
    assert result["agent_processing_latency_ms"] < 500.0  # Real-time sub-second execution

    # Verify zero-bridge AMSV synchronization
    assert amsv._view[22] == 0x24  # Directive intent register byte
    assert amsv.get_prosody_state() > 0
    assert amsv.get_prosody_fluency() > 0.0

    # Test streaming transcription hook (AssemblyAI-ready)
    partial_res = agent.process_streaming_transcription("Report status", is_final=False)
    assert partial_res is None  # Does not trigger on partial unfinalized speech

    final_res = agent.process_streaming_transcription("Report status immediately.", is_final=True)
    assert final_res is not None
    assert final_res["matched_intent"] == "DIRECTIVE_ACKNOWLEDGMENT"
