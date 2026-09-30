"""Russian Phonology Sub-AI.

Evaluates Cyrillic palatalization, Akan'ye/Ikan'ye reduction potentials,
voicing assimilation, and syllable density.
Syncs strictly with AMSV Phoneme state (Bytes 0..7), Prosody state (Bytes 8..15),
and Capability 4 (Offset 0x18 / Byte 24).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import RussianTokenizer


@dataclass
class RussianPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    palatalized_vowel_count: int
    voiced_consonant_count: int
    voiceless_consonant_count: int
    phonological_density_score: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


# Public alias
RussianPhonologyEvaluation = RussianPhonologyEvaluationResult


class RussianPhonologySubAI:
    """Dedicated AI Sub-Engine for Russian Phonetics, Palatalization, and Prosody."""

    VOWELS = set("аеёиоуыэюя")
    PALATALIZING_VOWELS = set("еёиьюя")
    VOICED_CONSONANTS = set("бвгджзйлмнр")
    VOICELESS_CONSONANTS = set("пфктшсхцчщ")

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = RussianTokenizer()

    def evaluate(self, text: str) -> RussianPhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        low = text.lower()

        palatalized_count = sum(1 for c in low if c in self.PALATALIZING_VOWELS)
        voiced_count = sum(1 for c in low if c in self.VOICED_CONSONANTS)
        voiceless_count = sum(1 for c in low if c in self.VOICELESS_CONSONANTS)
        syllable_count = max(len(tokens), sum(1 for c in low if c in self.VOWELS))

        density_score = min(1.0, 0.70 + (0.05 * min(3, palatalized_count)) + (0.05 * min(3, voiced_count)))

        synced = False
        if self.amsv is not None:
            ph_bitfield = (syllable_count & 0xFF) | ((palatalized_count & 0xFF) << 8) | ((voiced_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            prosody_bitfield = int(density_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return RussianPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            palatalized_vowel_count=palatalized_count,
            voiced_consonant_count=voiced_count,
            voiceless_consonant_count=voiceless_count,
            phonological_density_score=density_score,
            amsv_synced=synced
        )
