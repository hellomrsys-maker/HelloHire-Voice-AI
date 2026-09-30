"""
Polish Phonology Sub-AI — AMSV Resonance Protocol Upgrade
=========================================================
Upgrade: This Sub-AI now reads the Pragmatic Sub-AI's register (byte 0x16) and
honorific score (byte 0x15) BEFORE computing its orthography score.

Resonance Rules Applied:
  1. If Pragmatic Sub-AI wrote pragmatic_register = 2 (formal Pan/Pani) →
     Phonology Sub-AI applies stricter sibilant orthography expectations:
     formal text has lower tolerance for homophone confusion.
  2. If Pragmatic Sub-AI wrote honorific_score < 60 →
     Phonology Sub-AI notes this as a compounding factor in its score
     (poor honorific concord often co-occurs with phonological register errors).
"""

from typing import Dict, Any
from ..skills.tokenization import PolishTokenizer
from ..skills.phonology_sibilant_engine import PolishPhonologySibilantEngine


class PolishPhonologySubAI:
    def __init__(self):
        self.tokenizer = PolishTokenizer()
        self.engine = PolishPhonologySibilantEngine()

    def execute(self, text: str, amsv_buffer: bytearray = None) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        res = self.engine.check_orthography(tokens)

        orthography_score = res["orthography_score"]
        warnings = list(res["warnings"])

        # ── AMSV Resonance Protocol ──────────────────────────────────────────
        # Read Pragmatic Sub-AI's register and honorific score written earlier
        # in the same processing cycle.
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            pragmatic_register = amsv_buffer[0x16]
            honorific_score    = amsv_buffer[0x15]

            # Rule 1: Formal register demands stricter orthographic standards.
            # Under formal Pan/Pani context, any homophone confusion is amplified.
            if pragmatic_register == 2 and len(warnings) > 0:
                orthography_score = max(40, orthography_score - 20)
                warnings.append(
                    "Resonance Amplification: Homophone confusion is particularly "
                    "serious in formal (Pan/Pani) register — orthography penalty increased."
                )

            # Rule 2: Low honorific score + any orthographic warning = likely
            # systemic register confusion (not just isolated spelling error).
            if honorific_score < 60 and len(warnings) > 0:
                warnings.append(
                    "Resonance Signal: Low honorific concord score co-occurring with "
                    "orthographic warnings suggests systemic register confusion."
                )

        # ── Zero-Bridge AMSV Memory Writes ──────────────────────────────────
        # Byte 0x14: orthography_score (resonance-modulated)
        # Byte 0x35: sub_ai_phonology execution bitmask (0x02)
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[0x14] = max(0, min(100, orthography_score))
            amsv_buffer[0x35] = 0x02  # Phonology Sub-AI executed

        return {
            "sub_ai": "PhonologySubAI",
            "orthography_score": orthography_score,
            "has_nasal_vowels": res["has_nasal_vowels"],
            "has_sibilants": res["has_sibilants"],
            "warnings": warnings,
            "is_valid": len(warnings) == 0,
            "resonance_protocol": "active"
        }
