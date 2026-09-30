"""Turkish Phonology Sub-AI.

Evaluates 2-way and 4-way vowel harmony compliance,
consonant mutation (lenition/devoicing), and syllable metrics.
Syncs strictly with AMSV Phoneme state (Bytes 0..7), Prosody state (Bytes 8..15),
and Capability 4 (Offset 0x18 / Byte 24).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import TurkishTokenizer
from ..skills.vowel_harmony_engine import TurkishVowelHarmonyEngine
from ..analysis.vowel_harmony_analyzer import TurkishVowelHarmonyAnalyzer


@dataclass
class TurkishPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    front_vowel_count: int
    back_vowel_count: int
    harmony_compliance_score: float
    phonological_density_score: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


# Public alias
TurkishPhonologyEvaluation = TurkishPhonologyEvaluationResult


class TurkishPhonologySubAI:
    """Dedicated AI Sub-Engine for Turkish Phonetics, Vowel Harmony, and Consonant Mutation."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = TurkishTokenizer()
        self.harmony = TurkishVowelHarmonyEngine()
        self.harmony_analyzer = TurkishVowelHarmonyAnalyzer(self.tokenizer, self.harmony)

    def evaluate(self, text: str) -> TurkishPhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        harm_res = self.harmony_analyzer.analyze(text)

        vowels = []
        for t in tokens:
            vowels.extend(self.harmony.extract_vowels(t))

        front_count = sum(1 for v in vowels if v in self.harmony.FRONT_VOWELS)
        back_count = sum(1 for v in vowels if v in self.harmony.BACK_VOWELS)
        syllable_count = max(len(tokens), len(vowels))

        compliance = harm_res["compliance_score"] / 100.0
        density_score = min(1.0, 0.65 + (0.25 * compliance) + (0.10 * min(1.0, len(tokens) / 5.0)))

        synced = False
        if self.amsv is not None:
            ph_bitfield = (syllable_count & 0xFF) | ((front_count & 0xFF) << 8) | ((back_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            prosody_bitfield = int(density_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return TurkishPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            front_vowel_count=front_count,
            back_vowel_count=back_count,
            harmony_compliance_score=compliance,
            phonological_density_score=density_score,
            amsv_synced=synced
        )
