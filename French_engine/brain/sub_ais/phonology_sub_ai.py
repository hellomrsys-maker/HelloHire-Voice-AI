"""
French Phonology Sub-AI.
Evaluates French syllable counts, nasal vowels, elisions, and liaison boundaries.
Syncs strictly with AMSV Phoneme state (Bytes 0..7), Prosody state (Bytes 8..15),
and Capability 4 (Offset 0x18 / Byte 24).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import FrenchTokenizer
from ..skills.liaison_elision_engine import LiaisonElisionEngine


@dataclass
class FrenchPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    nasal_vowel_count: int
    liaison_detected_count: int
    phonological_harmony_score: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_harmony_score


# Public alias
FrenchPhonologyEvaluation = FrenchPhonologyEvaluationResult


class FrenchPhonologySubAI:
    """
    Dedicated AI Sub-Engine for French Phonetics, Elision, and Liaison.
    """

    NASAL_SPELLINGS = ["an", "am", "en", "em", "in", "im", "ain", "aim", "ein", "on", "om", "un", "um"]
    VOWELS = set("aeiouyéèêëàâîïôûù")

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = FrenchTokenizer()
        self.elision_engine = LiaisonElisionEngine()

    def evaluate(self, text: str) -> FrenchPhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        low = text.lower()

        # Count nasal digraphs
        nasal_count = 0
        for n in self.NASAL_SPELLINGS:
            nasal_count += low.count(n)

        # Estimate syllables by vowel nuclei
        syllable_count = 0
        for tok in tokens:
            cleaned = tok.lower().strip(".,;:!?«»'\"-")
            if not cleaned:
                continue
            # Basic vowel sequence count
            c_syll = sum(1 for c in cleaned if c in self.VOWELS)
            # Adjust mute final 'e'
            if cleaned.endswith("e") and len(cleaned) > 2 and not cleaned.endswith(("ée", "le", "re")):
                c_syll = max(1, c_syll - 1)
            syllable_count += max(1, c_syll)

        # Count liaisons
        liaison_count = 0
        for i in range(len(tokens) - 1):
            l_res = self.elision_engine.evaluate_liaison(tokens[i], tokens[i + 1])
            if l_res.get("has_liaison"):
                liaison_count += 1

        harmony_score = min(1.0, 0.70 + (0.05 * min(4, liaison_count)) + (0.05 * min(2, nasal_count)))

        synced = False
        if self.amsv is not None:
            # Sync to Phonemes (Bytes 0..7) and Prosody (Bytes 8..15)
            ph_bitfield = (syllable_count & 0xFF) | ((nasal_count & 0xFF) << 8) | ((liaison_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            prosody_bitfield = int(harmony_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            # Capability 4 (Byte 24 / 0x18)
            self.amsv.set_cognitive_score(4, harmony_score)
            synced = True

        return FrenchPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            nasal_vowel_count=nasal_count,
            liaison_detected_count=liaison_count,
            phonological_harmony_score=harmony_score,
            amsv_synced=synced,
        )
