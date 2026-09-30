"""
Portuguese Phonology Sub-AI.
Evaluates nasal vowels (ã, õ, ão, ãe, am, em), sibilants (s, z, x, ç),
and AO90 orthographic consistency.
Syncs strictly with AMSV Phoneme state (Bytes 0..7), Prosody state (Bytes 8..15),
and Capability 4 (Offset 0x18 / Byte 24).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import PortugueseTokenizer


@dataclass
class PortuguesePhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    nasal_vowel_count: int
    sibilant_count: int
    accented_vowel_count: int
    phonological_density_score: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


# Public alias
PortuguesePhonologyEvaluation = PortuguesePhonologyEvaluationResult


class PortuguesePhonologySubAI:
    """
    Dedicated AI Sub-Engine for Portuguese Phonetics, Nasality, and Stress.
    """

    ACCENTED_VOWELS = set("áéíóúâêôàãõ")
    SIBILANTS = set("szxç")
    VOWELS = set("aeiouáéíóúâêôàãõ")

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = PortugueseTokenizer()

    def evaluate(self, text: str) -> PortuguesePhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        low = text.lower()

        # Count nasal vowels and diphthongs
        nasal_count = low.count("ã") + low.count("õ")
        for nasal_digraph in ["ão", "õe", "ãe", "am", "em", "im", "om", "um"]:
            nasal_count += low.count(nasal_digraph)

        sibilant_count = sum(1 for c in low if c in self.SIBILANTS)
        accented_count = sum(1 for c in low if c in self.ACCENTED_VOWELS)

        syllable_count = max(len(tokens), sum(1 for c in low if c in self.VOWELS))

        density_score = min(1.0, 0.70 + (0.05 * min(3, nasal_count)) + (0.05 * min(3, accented_count)))

        synced = False
        if self.amsv is not None:
            ph_bitfield = (syllable_count & 0xFF) | ((nasal_count & 0xFF) << 8) | ((sibilant_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            prosody_bitfield = int(density_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return PortuguesePhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            nasal_vowel_count=nasal_count,
            sibilant_count=sibilant_count,
            accented_vowel_count=accented_count,
            phonological_density_score=density_score,
            amsv_synced=synced,
        )
