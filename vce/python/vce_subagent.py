"""
Verbal Communication Sub-Agent (Python Intelligence Core).

Operates exclusively within the Verbal Communication domain.
Holds full domain knowledge of phonetics, articulatory geometry, prosodic contours,
and fluency dynamics. Synchronizes state with MAIO via AMSV.
"""

from typing import Dict, List, Any, Optional
import math
import sys
import os

# Import AMSV embedded view
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from amsv.python.amsv_embedded import AMSVEmbeddedView


class VerbalCommunicationSubAgent:
    """
    Domain-specialized AI agent for verbal communication competence.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.phonetic_inventory: Dict[str, Dict[str, Any]] = self._init_phonetic_inventory()
        self.prosodic_benchmarks: Dict[str, float] = {
            "target_speech_rate_syl_sec": 4.5,
            "target_phonation_ratio": 0.80,
            "max_tolerated_pause_sec": 1.2,
            "f0_std_dev_threshold": 24.0,  # Semitone expressive variability
        }
        self.learner_history: List[Dict[str, float]] = []

    def _init_phonetic_inventory(self) -> Dict[str, Dict[str, Any]]:
        return {
            "i": {"name": "Close Front Unrounded", "f1_hz": 280, "f2_hz": 2250, "manner": "vowel"},
            "u": {"name": "Close Back Rounded", "f1_hz": 310, "f2_hz": 870, "manner": "vowel"},
            "a": {"name": "Open Front Unrounded", "f1_hz": 750, "f2_hz": 1700, "manner": "vowel"},
            "s": {"name": "Voiceless Alveolar Fricative", "spectral_peak_hz": 6500, "manner": "fricative"},
            "t": {"name": "Voiceless Alveolar Plosive", "burst_duration_ms": 18, "manner": "plosive"},
            "m": {"name": "Voiced Bilabial Nasal", "f1_hz": 250, "manner": "nasal"},
        }

    def evaluate_utterance(
        self,
        formant_f1: float,
        formant_f2: float,
        f0_hz: float,
        speech_rate: float,
        phonation_ratio: float,
        filled_pause_count: int
    ) -> Dict[str, Any]:
        """
        Evaluate candidate verbal communication against domain benchmarks
        and update AMSV state vector in real time.
        """
        # 1. Articulation Accuracy Calculation
        vowel_dispersion = math.sqrt((formant_f1 - 500.0) ** 2 + (formant_f2 - 1500.0) ** 2) / 1000.0
        articulation_accuracy = max(0.0, min(1.0, 1.0 - abs(vowel_dispersion - 0.75)))

        # 2. Fluency Score Derivation
        rate_diff = abs(speech_rate - self.prosodic_benchmarks["target_speech_rate_syl_sec"])
        rate_score = max(0.0, 1.0 - (rate_diff / 3.0))
        ratio_score = min(1.0, phonation_ratio / self.prosodic_benchmarks["target_phonation_ratio"])
        pause_penalty = filled_pause_count * 0.15

        fluency_score = max(0.0, min(1.0, 0.4 * rate_score + 0.4 * ratio_score + 0.2 - pause_penalty))

        # 3. Prosodic Dynamic Expressiveness
        prosody_expressiveness = max(0.0, min(1.0, f0_hz / 200.0))

        # 4. Zero-Bridge Synchronization to AMSV
        phoneme_packed = (int(articulation_accuracy * 65535.0) << 16) | 0x0001
        self.amsv.set_phoneme_state(phoneme_packed)

        f0_fixed = int(min(500.0, max(50.0, f0_hz)) * 64.0)
        fl_fixed = int(fluency_score * 65535.0)
        prosody_packed = (fl_fixed << 32) | f0_fixed
        self.amsv.set_prosody_state(prosody_packed)

        result = {
            "articulation_accuracy": round(articulation_accuracy, 3),
            "fluency_score": round(fluency_score, 3),
            "prosody_expressiveness": round(prosody_expressiveness, 3),
            "speech_rate_syl_per_sec": speech_rate,
            "phonation_ratio": phonation_ratio,
            "filled_pauses": filled_pause_count,
            "feedback": self._generate_diagnostic_feedback(articulation_accuracy, fluency_score)
        }

        self.learner_history.append({"acc": articulation_accuracy, "fl": fluency_score})
        return result

    def evaluate_text_utterance(
        self,
        text: str,
        pitch_contour: Optional[List[float]] = None,
        duration_sec: float = 3.0,
        speech_wpm: float = 135.0
    ) -> Dict[str, Any]:
        """
        Evaluates candidate speech from text representation and pitch contour.
        """
        words = text.split()
        num_words = len(words)
        effective_wpm = (num_words / max(0.5, duration_sec)) * 60.0 if duration_sec > 0 else speech_wpm
        speech_rate_syl = (effective_wpm / 60.0) * 1.5

        f0_mean = sum(pitch_contour) / len(pitch_contour) if pitch_contour else 130.0
        
        # Calculate phonetic precision based on word complexity
        avg_word_len = sum(len(w) for w in words) / max(1, num_words)
        phoneme_acc = min(1.0, max(0.5, avg_word_len / 7.0 + 0.3))

        # Check pauses
        hesitations = sum(1 for w in words if w.lower() in ("um", "uh", "er", "ah"))

        eval_dict = self.evaluate_utterance(
            formant_f1=500.0,
            formant_f2=1500.0,
            f0_hz=f0_mean,
            speech_rate=speech_rate_syl,
            phonation_ratio=0.85,
            filled_pause_count=hesitations
        )
        eval_dict["phoneme_accuracy"] = phoneme_acc
        eval_dict["f0_mean_hz"] = f0_mean
        eval_dict["wpm"] = effective_wpm
        return eval_dict

    def _generate_diagnostic_feedback(self, articulation: float, fluency: float) -> str:
        feedback = []
        if articulation < 0.70:
            feedback.append("Vowel space area is compressed. Articulate front vowels with greater tongue advancement.")
        else:
            feedback.append("Clear acoustic vowel distinction and resonant formant separation.")

        if fluency < 0.65:
            feedback.append("Fluency disrupted by hesitation intervals. Aim for longer breath group runs.")
        else:
            feedback.append("Optimal rhythm and sustained speech rate maintained across phrases.")

        return " ".join(feedback)

    def export_subagent_knowledge_state(self) -> Dict[str, Any]:
        """Expose current subagent knowledge state to the MAIO."""
        return {
            "domain": "Verbal Communication",
            "historical_evaluations": len(self.learner_history),
            "benchmarks": self.prosodic_benchmarks,
            "active_amsv_phoneme": self.amsv.get_phoneme_state(),
            "active_amsv_prosody": self.amsv.get_prosody_state()
        }


# Alias for MAIO / System integration
VceSubAgent = VerbalCommunicationSubAgent
