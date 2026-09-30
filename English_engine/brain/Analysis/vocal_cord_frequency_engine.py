"""
vocal_cord_frequency_engine.py - Vocal Cord Biophysics & Situational Frequency Modulation Engine.

Grounds voice generation in the human larynx's myoelastic-aerodynamic principles:
1. Multi-Record Statistical Frequency Envelopes:
   - min_f0_floor, average_f0_mean, max_f0_nominal, absolute_peak_ceiling.
   - Demographic Speaker Cohorts (Low register ~110Hz, Medium register ~188Hz, High register ~240Hz).
   - Relative Situational Multipliers (0.68x to 1.85x) that adapt to any individual human baseline.
2. Cricothyroid Muscle Tension & Thyroarytenoid Dynamics (F0 pitch tuning: High, Low, Medium).
3. Subglottal Pressure (Ps) & Glottal Collision Force (Vocal roughness, rashness, violence).
4. Vocal Fold Open Quotient (Oq) & Glottal Closure Modes (Smooth breathiness, chest resonance, vocal fry).
5. Zero-Bridge 64-Byte AMSV Memory Synchronization.
"""

from __future__ import annotations
import os
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from amsv.python.amsv_embedded import AMSVEmbeddedView


class SituationalScenario(str, Enum):
    CALM_REASSURANCE = "CALM_REASSURANCE"
    CONFIDENCE_AUTHORITY = "CONFIDENCE_AUTHORITY"
    AGGRESSIVE_VIOLENCE = "AGGRESSIVE_VIOLENCE"
    EMOTIONAL_VULNERABILITY = "EMOTIONAL_VULNERABILITY"
    DEEP_MELANCHOLY = "DEEP_MELANCHOLY"
    WHISPER_SECRECY = "WHISPER_SECRECY"


class SpeakerRegisterCohort(str, Enum):
    LOW_REGISTER = "low_register_cohort"       # Deep baritone / bass (baseline ~95-110 Hz)
    MEDIUM_REGISTER = "medium_register_cohort" # Neutral / tenor (baseline ~170-190 Hz)
    HIGH_REGISTER = "high_register_cohort"     # High / alto / soprano (baseline ~220-250 Hz)


# Convenience alias
SpeakerCohort = SpeakerRegisterCohort


@dataclass
class WordAcousticTrajectory:
    word: str
    duration_ms: int
    start_f0_hz: float
    peak_f0_hz: float
    end_f0_hz: float
    open_quotient_oq: float
    glottal_roughness: float
    is_focal_stress: bool


@dataclass
class SituationalVocalModulationResult:
    text: str
    scenario: str
    display_name: str
    tuning_register: str
    mean_f0_hz: float
    frequency_envelope_hz: Dict[str, float]
    speaker_cohort_used: str
    speaker_scaled_f0_hz: float
    relative_multiplier: float
    pitch_contour: str
    post_utterance_pause_ms: int
    words: List[WordAcousticTrajectory]
    vocal_cord_biomechanics: Dict[str, Any]
    glottal_roughness_envelope: Dict[str, float]
    acoustic_tuning: Dict[str, float]
    scientific_justification: str
    amsv_synced: bool
    amsv_scenario_byte: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "scenario": self.scenario,
            "display_name": self.display_name,
            "tuning_register": self.tuning_register,
            "mean_f0_hz": self.mean_f0_hz,
            "frequency_envelope_hz": self.frequency_envelope_hz,
            "speaker_cohort_used": self.speaker_cohort_used,
            "speaker_scaled_f0_hz": self.speaker_scaled_f0_hz,
            "relative_multiplier": self.relative_multiplier,
            "pitch_contour": self.pitch_contour,
            "post_utterance_pause_ms": self.post_utterance_pause_ms,
            "vocal_cord_biomechanics": self.vocal_cord_biomechanics,
            "glottal_roughness_envelope": self.glottal_roughness_envelope,
            "acoustic_tuning": self.acoustic_tuning,
            "scientific_justification": self.scientific_justification,
            "amsv_scenario_byte": hex(self.amsv_scenario_byte),
            "words": [
                {
                    "word": w.word,
                    "duration_ms": w.duration_ms,
                    "f0_trajectory_hz": [w.start_f0_hz, w.peak_f0_hz, w.end_f0_hz],
                    "open_quotient_oq": w.open_quotient_oq,
                    "glottal_roughness": w.glottal_roughness,
                    "focal_stress": w.is_focal_stress
                }
                for w in self.words
            ]
        }

    @property
    def utterance(self) -> str:
        return self.text

    @property
    def word_trajectories(self) -> List[WordAcousticTrajectory]:
        return self.words

    @property
    def amsv_register_byte(self) -> int:
        return self.amsv_scenario_byte


VocalTuningResult = SituationalVocalModulationResult


class VocalCordFrequencyEngine:
    """Computes vocal cord frequency modulation across communicative scenarios and speaker cohorts."""

    def __init__(self, matrix_path: Optional[str] = None, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

        if matrix_path is None:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            matrix_path = os.path.join(root, "data", "situational_vocal_frequency_matrix.json")

        self.matrix_data = self._load_matrix(matrix_path)

    def _load_matrix(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"scenarios": {}}

    def modulate_phrase(
        self,
        text: str = "",
        scenario: SituationalScenario | str = SituationalScenario.CALM_REASSURANCE,
        speaker_cohort: SpeakerRegisterCohort = SpeakerRegisterCohort.MEDIUM_REGISTER,
        custom_baseline_f0_hz: Optional[float] = None,
        utterance: Optional[str] = None
    ) -> SituationalVocalModulationResult:
        if utterance is not None:
            text = utterance
        scenario_key = scenario.value if isinstance(scenario, SituationalScenario) else str(scenario)
        sc_data = self.matrix_data.get("scenarios", {}).get(scenario_key)

        if not sc_data:
            sc_data = self.matrix_data.get("scenarios", {}).get("CALM_REASSURANCE", {})

        freq_env = sc_data.get("frequency_envelope_hz", {
            "min_f0_floor": 140.0,
            "average_f0_mean": 188.0,
            "max_f0_nominal": 215.0,
            "absolute_peak_ceiling": 260.0
        })

        cohort_key = speaker_cohort.value if isinstance(speaker_cohort, SpeakerRegisterCohort) else str(speaker_cohort)
        cohort_dict = sc_data.get("speaker_cohort_baselines_hz", {}).get(cohort_key, {})
        cohort_average = cohort_dict.get("average", freq_env["average_f0_mean"])

        multiplier = sc_data.get("relative_modulation_multiplier", 1.0)

        # Compute speaker-specific scaled F0
        if custom_baseline_f0_hz is not None:
            raw_scaled_f0 = custom_baseline_f0_hz * multiplier
            min_floor = 50.0  # Absolute human physiological floor
            max_ceiling = freq_env.get("absolute_peak_ceiling", 550.0)
        else:
            raw_scaled_f0 = cohort_average
            min_floor = cohort_dict.get("min", freq_env.get("min_f0_floor", 0.0))
            max_ceiling = freq_env.get("absolute_peak_ceiling", 520.0)

        if multiplier == 0.0:
            scaled_f0 = 0.0
        else:
            scaled_f0 = max(min_floor, min(max_ceiling, raw_scaled_f0))

        mean_f0 = round(scaled_f0, 1)
        roughness = sc_data.get("acoustic_tuning", {}).get("roughness", 0.5)
        sps = max(1.0, sc_data.get("acoustic_tuning", {}).get("speech_rate_sps", 3.2))
        oq = sc_data.get("vocal_cord_biomechanics", {}).get("open_quotient_oq", 0.5)

        tokens = [t for t in re.split(r"\s+", text.strip()) if t]
        if not tokens:
            tokens = ["..."]

        word_trajectories: List[WordAcousticTrajectory] = []
        num_words = len(tokens)
        base_word_duration = int(1000 / sps)
        contour = sc_data.get("pitch_contour", "STEADY")

        for i, word in enumerate(tokens):
            clean = re.sub(r"[^a-zA-Z0-9']", "", word).lower()
            is_last = (i == num_words - 1)
            is_focal = is_last or (len(clean) >= 4 and i > 0)

            if multiplier == 0.0:
                start_f = peak_f = end_f = 0.0
            elif contour == "GENTLE_FALLING_GLISSANDO":
                start_f = mean_f0 + 15.0 - (i * 10.0)
                peak_f = max(start_f, mean_f0 + 8.0)
                end_f = max(min_floor, mean_f0 - 18.0 - (i * 8.0))
            elif contour == "SHARP_EXPLOSIVE_ATTACK_FALL":
                start_f = min(max_ceiling, mean_f0 + 25.0)
                peak_f = min(max_ceiling, mean_f0 + 40.0)
                end_f = max(min_floor, mean_f0 - 10.0)
            elif contour == "FRACTURED_MICRO_TREMOR":
                jitter_delta = ((i % 2) * 2 - 1) * 16.0
                start_f = mean_f0 + jitter_delta
                peak_f = mean_f0 + 22.0
                end_f = mean_f0 - jitter_delta
            elif contour == "FLAT_MONOTONIC_CREEP":
                start_f = mean_f0 + 1.5
                peak_f = mean_f0 + 2.5
                end_f = mean_f0 - 1.5
            else:
                start_f = mean_f0 - 3.0
                peak_f = mean_f0 + 4.0
                end_f = mean_f0

            duration = base_word_duration + (60 if is_focal else -20)
            duration = max(100, min(800, duration))

            word_trajectories.append(WordAcousticTrajectory(
                word=word,
                duration_ms=duration,
                start_f0_hz=round(start_f, 1),
                peak_f0_hz=round(peak_f, 1),
                end_f0_hz=round(end_f, 1),
                open_quotient_oq=round(oq, 2),
                glottal_roughness=round(roughness, 2),
                is_focal_stress=is_focal
            ))

        scenario_byte = sc_data.get("amsv_scenario_byte", 0x20)
        self.amsv._view[8] = int(min(255, max(0, mean_f0 / 2.0)))
        self.amsv._view[12] = int(min(255, max(0, sps * 25.0)))
        self.amsv._view[16] = int(min(255, max(0, roughness * 255.0)))
        self.amsv._view[20] = scenario_byte

        return SituationalVocalModulationResult(
            text=text,
            scenario=scenario_key,
            display_name=sc_data.get("display_name", scenario_key),
            tuning_register=sc_data.get("tuning_register", "BALANCED"),
            mean_f0_hz=freq_env["average_f0_mean"],
            frequency_envelope_hz=freq_env,
            speaker_cohort_used=cohort_key,
            speaker_scaled_f0_hz=mean_f0,
            relative_multiplier=multiplier,
            pitch_contour=contour,
            post_utterance_pause_ms=sc_data.get("post_utterance_pause_ms", 518),
            words=word_trajectories,
            vocal_cord_biomechanics=sc_data.get("vocal_cord_biomechanics", {}),
            glottal_roughness_envelope=sc_data.get("glottal_roughness_envelope", {}),
            acoustic_tuning=sc_data.get("acoustic_tuning", {}),
            scientific_justification=sc_data.get("scientific_justification", ""),
            amsv_synced=True,
            amsv_scenario_byte=scenario_byte
        )

    def analyze_benchmark_phrase_all_scenarios(
        self,
        phrase: str = "It's okay",
        speaker_cohort: SpeakerRegisterCohort = SpeakerRegisterCohort.MEDIUM_REGISTER
    ) -> Dict[str, Any]:
        """Analyzes a phrase across all scenarios with multi-record statistical envelopes."""
        results = {}
        for sc in SituationalScenario:
            res = self.modulate_phrase(phrase, sc, speaker_cohort=speaker_cohort)
            results[sc.value] = res.to_dict()
        return {
            "phrase": phrase,
            "speaker_cohort": speaker_cohort.value,
            "total_scenarios": len(results),
            "scenarios_breakdown": results
        }

    # Method alias for pedagogical / training convenience
    synthesize_vocal_tuning = modulate_phrase
