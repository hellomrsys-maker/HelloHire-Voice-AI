"""
voice_agent/audio_io.py - Real-Time Audio Capture, VAD, and Playback Subsystem.

Provides:
1. MicrophoneStream: Real-time 16kHz 16-bit mono PCM capture via sounddevice.
2. EnergyVAD: Voice Activity Detector with adaptive energy and silence-turn boundary tracking.
3. AudioPlayer: Low-latency playback and WAV buffer serialization for synthesized waveforms.
"""

from __future__ import annotations
import io
import wave
import time
import queue
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Generator, List, Tuple

import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception:
    SOUNDDEVICE_AVAILABLE = False


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    dtype: str = "int16"
    frame_duration_ms: int = 30  # 30 ms frame = 480 samples at 16kHz
    silence_threshold_ms: int = 500  # End of speech detection threshold
    energy_threshold_rms: float = 300.0  # RMS amplitude threshold for speech


class EnergyVAD:
    """Voice Activity Detector tracking speech frames and turn boundaries."""

    def __init__(self, config: AudioConfig = AudioConfig()):
        self.config = config
        self.frame_samples = int(config.sample_rate * (config.frame_duration_ms / 1000.0))
        self.silence_frames_limit = int(config.silence_threshold_ms / config.frame_duration_ms)
        self.consecutive_silence = 0
        self.in_speech = False
        self.speech_frames: List[bytes] = []

    def is_speech_frame(self, frame_bytes: bytes) -> bool:
        samples = np.frombuffer(frame_bytes, dtype=np.int16)
        if len(samples) == 0:
            return False
        rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
        return rms >= self.config.energy_threshold_rms

    def process_frame(self, frame_bytes: bytes) -> Tuple[bool, bool, Optional[bytes]]:
        """
        Processes a single audio frame.
        Returns:
            (is_speech, is_turn_completed, complete_utterance_bytes)
        """
        is_speech = self.is_speech_frame(frame_bytes)

        if is_speech:
            self.in_speech = True
            self.consecutive_silence = 0
            self.speech_frames.append(frame_bytes)
            return (True, False, None)

        if self.in_speech:
            self.consecutive_silence += 1
            self.speech_frames.append(frame_bytes)
            if self.consecutive_silence >= self.silence_frames_limit:
                # Turn ended!
                complete_audio = b"".join(self.speech_frames)
                self.reset()
                return (False, True, complete_audio)

        return (False, False, None)

    def reset(self) -> None:
        self.in_speech = False
        self.consecutive_silence = 0
        self.speech_frames.clear()


class MicrophoneStream:
    """Streams 16kHz 16-bit mono PCM chunks from hardware microphone or test buffer."""

    def __init__(self, config: AudioConfig = AudioConfig()):
        self.config = config
        self.queue: queue.Queue[bytes] = queue.Queue()
        self.is_running = False
        self._stream: Optional[sd.InputStream] = None
        self.frame_size = int(config.sample_rate * (config.frame_duration_ms / 1000.0))

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        self.queue.put(bytes(indata))

    def start(self) -> bool:
        if self.is_running:
            return True
        self.is_running = True
        if SOUNDDEVICE_AVAILABLE:
            try:
                self._stream = sd.InputStream(
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    dtype=self.config.dtype,
                    blocksize=self.frame_size,
                    callback=self._audio_callback
                )
                self._stream.start()
                return True
            except Exception as e:
                # Headless or device unavailable; stream remains open for synthetic feed
                self._stream = None
                return False
        return False

    def push_frame(self, frame_bytes: bytes) -> None:
        """Manually injects PCM audio frame (useful for automated testing or pipeline piping)."""
        self.queue.put(frame_bytes)

    def read_frame(self, timeout: float = 0.1) -> Optional[bytes]:
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self) -> None:
        self.is_running = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None


class AudioPlayer:
    """Plays synthesized PCM waveforms or serializes to WAV format."""

    @staticmethod
    def play_pcm(pcm_bytes: bytes, sample_rate: int = 16000, blocking: bool = False) -> bool:
        if not SOUNDDEVICE_AVAILABLE:
            return False
        try:
            samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            sd.play(samples, samplerate=sample_rate)
            if blocking:
                sd.wait()
            return True
        except Exception:
            return False

    @staticmethod
    def pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()

    @staticmethod
    def save_wav(pcm_bytes: bytes, filepath: str, sample_rate: int = 16000) -> None:
        wav_bytes = AudioPlayer.pcm_to_wav_bytes(pcm_bytes, sample_rate=sample_rate)
        with open(filepath, "wb") as f:
            f.write(wav_bytes)
