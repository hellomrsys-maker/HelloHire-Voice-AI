"""
Bengali Phonology Sub-AI.
Evaluates retroflex consonants (ট, ঠ, ড, ঢ, ড়, ঢ়), aspirated consonants (খ, ঘ, ছ, ঝ, ঠ, ঢ, থ, ধ, ফ, ভ),
and phonemic nasalization (ঁ, ং).
Syncs strictly with AMSV Phoneme state (Bytes 0..7), Prosody state (Bytes 8..15),
and Capability 4 (Offset 0x18 / Byte 24).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import BengaliTokenizer


@dataclass
class BengaliPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    retroflex_count: int
    aspirated_count: int
    nasalized_count: int
    phonological_density_score: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


# Public alias
BengaliPhonologyEvaluation = BengaliPhonologyEvaluationResult


class BengaliPhonologySubAI:
    """
    Dedicated AI Sub-Engine for Bengali Phonetics, Retroflexion, and Nasalization.
    """

    RETROFLEX_GLYPHS = set("টঠডঢড়ঢ়ণ")
    ASPIRATED_GLYPHS = set("খঘছঝঠঢথধফভ")
    NASAL_GLYPHS = set("ঁংঙঞণনম")
    VOWEL_SIGNS = set("অআইঈউঊঋএঐওঔািীুূৃেৈোৌ")

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = BengaliTokenizer()

    def evaluate(self, text: str) -> BengaliPhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)

        retro_count = sum(1 for c in text if c in self.RETROFLEX_GLYPHS)
        asp_count = sum(1 for c in text if c in self.ASPIRATED_GLYPHS)
        nasal_count = sum(1 for c in text if c in self.NASAL_GLYPHS)

        # Approximate syllables by vowel markers or token count
        syllable_count = max(len(tokens), sum(1 for c in text if c in self.VOWEL_SIGNS))

        density_score = min(1.0, 0.70 + (0.05 * min(3, retro_count)) + (0.05 * min(3, asp_count)))

        synced = False
        if self.amsv is not None:
            ph_bitfield = (syllable_count & 0xFF) | ((retro_count & 0xFF) << 8) | ((asp_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            prosody_bitfield = int(density_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return BengaliPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            retroflex_count=retro_count,
            aspirated_count=asp_count,
            nasalized_count=nasal_count,
            phonological_density_score=density_score,
            amsv_synced=synced,
        )
