"""
voice_agent/vocal_audio_renderer.py - Biophysical Vocal Waveform Synthesizer & Audio Renderer.

Converts VocalCordFrequencyEngine tuning results into physical audible waveforms:
1. Glottal Pulse Generator: Simulates laryngeal airflow under subglottal pressure (P_s)
2. Frequency Modulation: Tracks dynamic word-level F0 trajectories (pitch contours)
3. Open Quotient & Glottal Texture:
   - High O_q (e.g., Calm/Whisper) -> Soft breathiness and turbulent aspiration
   - Low O_q (e.g., Aggressive)   -> Sharp vocal fold collision and rash glottal attacks
4. Formant Resonance Filter: Applies vocal tract resonances (F1, F2, F3) for human timbre
5. Post-Utterance Latency: Appends calibrated conversational silence (e.g., 518 ms)
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from English_engine.brain.Analysis.vocal_cord_frequency_engine import (
    VocalTuningResult,
    WordAcousticTrajectory,
    SituationalScenario,
)


class VocalAudioRenderer:
    """
    Renders biophysically modulated audio waveforms from laryngeal acoustic parameters.
    Outputs 16kHz, 16-bit mono PCM bytes ready for speakers or WAV serialization.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def _generate_glottal_pulse(
        self,
        f0: float,
        duration_sec: float,
        open_quotient: float,
        subglottal_pressure_cmh2o: float,
        roughness: float
    ) -> np.ndarray:
        """
        Generates glottal volume velocity waveform with turbulent aspiration and laryngeal roughness.
        """
        total_samples = int(self.sample_rate * duration_sec)
        if total_samples <= 0:
            return np.zeros(0, dtype=np.float32)

        # Handle whisper / aperiodic aspiration (F0 = 0 Hz)
        if f0 <= 10.0:
            noise = np.random.randn(total_samples).astype(np.float32)
            # Amplitude proportional to subglottal airflow
            amp = min(1.0, subglottal_pressure_cmh2o / 12.0) * 0.4
            return noise * amp

        # Fundamental phase accumulation with jitter
        t = np.arange(total_samples, dtype=np.float32) / self.sample_rate
        # Add micro-perturbation (jitter) based on roughness
        jitter = (np.random.randn(total_samples) * (roughness * 0.04)).astype(np.float32)
        instantaneous_freq = np.maximum(50.0, f0 * (1.0 + jitter))
        phase = 2.0 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate

        # Asymmetric glottal pulse (Rosenberg / Liljencrants-Fant approximation)
        cycle_phase = np.mod(phase, 2.0 * np.pi) / (2.0 * np.pi)
        oq = max(0.2, min(0.95, open_quotient))

        # Pulse is active during opening and closing phases (0 to oq)
        pulse = np.zeros(total_samples, dtype=np.float32)
        opening_mask = cycle_phase < oq
        pulse[opening_mask] = 0.5 * (1.0 - np.cos(np.pi * cycle_phase[opening_mask] / oq))

        # Sharp closure (glottal collision) creates high frequency harmonics
        closing_mask = (cycle_phase >= (oq * 0.8)) & (cycle_phase < oq)
        pulse[closing_mask] *= (1.0 + roughness * 0.5)

        # Amplitude scaling from subglottal pressure (8 cmH2O nominal = 1.0)
        pressure_gain = min(1.5, subglottal_pressure_cmh2o / 8.0)
        pulse *= pressure_gain

        # Add turbulent aspiration noise when open quotient is elevated (breathiness)
        if oq > 0.6:
            aspiration_level = (oq - 0.6) * 0.5
            aspiration = np.random.randn(total_samples).astype(np.float32) * aspiration_level
            pulse = (pulse * 0.85) + aspiration

        return pulse

    def _apply_vocal_tract_filter(self, signal: np.ndarray, scenario: SituationalScenario) -> np.ndarray:
        """
        Applies 3-formant vocal tract resonance filter modeling oral/pharyngeal acoustics.
        """
        if len(signal) == 0:
            return signal

        # Scenario-specific formant tunings (F1, F2, F3 in Hz)
        sc_key = scenario.value if hasattr(scenario, "value") else str(scenario)
        formants_map = {
            "CALM_REASSURANCE": (550.0, 1600.0, 2600.0),
            "CONFIDENCE_AUTHORITY": (500.0, 1400.0, 2400.0),
            "AGGRESSIVE_VIOLENCE": (700.0, 1900.0, 3100.0),
            "EMOTIONAL_VULNERABILITY": (600.0, 1750.0, 2800.0),
            "DEEP_MELANCHOLY": (420.0, 1250.0, 2200.0),
            "WHISPER_SECRECY": (650.0, 1800.0, 2900.0),
        }
        formants = formants_map.get(sc_key, (550.0, 1600.0, 2600.0))

        # Simple 2nd-order resonator IIR filters
        filtered = signal.copy()
        for fc in formants:
            bw = fc / 10.0  # Bandwidth Q = 10
            r = math.exp(-math.pi * bw / self.sample_rate)
            theta = 2.0 * math.pi * fc / self.sample_rate
            a1 = -2.0 * r * math.cos(theta)
            a2 = r * r
            b0 = 1.0 - r

            # Apply difference equation: y[n] = b0*x[n] - a1*y[n-1] - a2*y[n-2]
            y = np.zeros_like(filtered)
            y1, y2 = 0.0, 0.0
            for i in range(len(filtered)):
                val = b0 * filtered[i] - a1 * y1 - a2 * y2
                y[i] = val
                y2 = y1
                y1 = val
            filtered = (filtered * 0.4) + (y * 0.6)

        return filtered

    def render_tuning_result(
        self,
        tuning: VocalTuningResult,
        include_calibrated_silence: bool = True
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Renders complete audible PCM wave audio from VocalTuningResult.
        Returns:
            (pcm_16bit_bytes, acoustic_metadata)
        """
        word_segments: List[np.ndarray] = []
        sub_p = tuning.vocal_cord_biomechanics.get("subglottal_pressure_cmh2o", 8.0)
        oq = tuning.vocal_cord_biomechanics.get("open_quotient_oq", 0.5)

        for w_traj in tuning.word_trajectories:
            dur_sec = max(0.05, w_traj.duration_ms / 1000.0)
            avg_f0 = (w_traj.start_f0_hz + w_traj.peak_f0_hz + w_traj.end_f0_hz) / 3.0
            glottal = self._generate_glottal_pulse(
                f0=avg_f0,
                duration_sec=dur_sec,
                open_quotient=w_traj.open_quotient_oq or oq,
                subglottal_pressure_cmh2o=sub_p,
                roughness=w_traj.glottal_roughness
            )

            # Apply smooth window envelope to eliminate inter-word clicks
            if len(glottal) > 32:
                ramp_len = min(64, len(glottal) // 4)
                window = np.ones(len(glottal), dtype=np.float32)
                window[:ramp_len] = np.linspace(0.0, 1.0, ramp_len)
                window[-ramp_len:] = np.linspace(1.0, 0.0, ramp_len)
                glottal *= window

            word_segments.append(glottal)
            # Brief 25ms inter-word gap
            gap_samples = int(self.sample_rate * 0.025)
            word_segments.append(np.zeros(gap_samples, dtype=np.float32))

        # Combine all word segments
        if word_segments:
            combined = np.concatenate(word_segments)
        else:
            combined = np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)

        # Apply vocal tract formant shaping
        shaped = self._apply_vocal_tract_filter(combined, scenario=tuning.scenario)

        # Append calibrated turn-taking pause (e.g. 518 ms)
        if include_calibrated_silence and tuning.post_utterance_pause_ms > 0:
            silence_samples = int(self.sample_rate * (tuning.post_utterance_pause_ms / 1000.0))
            shaped = np.concatenate([shaped, np.zeros(silence_samples, dtype=np.float32)])

        # Normalize and convert to 16-bit PCM
        peak = np.max(np.abs(shaped))
        if peak > 1e-4:
            normalized = shaped / peak * 0.85
        else:
            normalized = shaped

        int16_samples = (normalized * 32767.0).astype(np.int16)
        pcm_bytes = int16_samples.tobytes()

        metadata = {
            "utterance": tuning.utterance,
            "scenario": tuning.scenario.value if hasattr(tuning.scenario, "value") else str(tuning.scenario),
            "sample_rate": self.sample_rate,
            "duration_total_ms": int((len(int16_samples) / self.sample_rate) * 1000),
            "post_pause_ms": tuning.post_utterance_pause_ms,
            "f0_mean_hz": round(tuning.mean_f0_hz, 1),
            "subglottal_pressure_cmh2o": sub_p,
            "open_quotient_oq": oq,
            "amsv_register_byte": hex(tuning.amsv_register_byte),
            "total_bytes": len(pcm_bytes),
        }
        return pcm_bytes, metadata
