"""
Polish Editorial Sub-AI — AMSV Resonance Protocol Upgrade
=========================================================
Upgrade: This Sub-AI now reads what the Syntax Sub-AI wrote to the AMSV buffer
BEFORE computing its own scores. This implements the AMSV Resonance Protocol:
the 64 bytes become a live cross-agent communication channel within a single
processing cycle, not a static per-agent clipboard.

Resonance Rules Applied:
  1. If Syntax Sub-AI wrote genitive_neg_flag = 0 (byte 0x10) →
     Editorial Sub-AI BOOSTS case_score penalty (byte 0x13 reduced)
     and increments neg_concord_count (byte 0x18).
  2. If Pragmatic Sub-AI wrote a mixed register flag (register_code=1 AND
     honorific_score < 80, byte 0x16 = 1 AND 0x15 < 80) →
     Editorial Sub-AI sets vocative_flag to 0 (byte 0x19) to suppress
     false-positive vocative detection in mixed-register text.
"""

from typing import Dict, Any
from ..analysis.aspect_tense_analyzer import PolishAspectTenseAnalyzer
from ..skills.tokenization import PolishTokenizer


class PolishEditorialSubAI:
    def __init__(self):
        self.aspect_analyzer = PolishAspectTenseAnalyzer()
        self.tokenizer = PolishTokenizer()

    def execute(self, text: str, amsv_buffer: bytearray = None) -> Dict[str, Any]:
        asp_res = self.aspect_analyzer.analyze(text)
        tokens = self.tokenizer.tokenize(text)
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]

        # Count negative concord items
        neg_concord_items = [t for t in low_tokens if t in {
            "nikt", "nic", "nigdy", "nigdzie", "żaden", "żadna", "żadne"
        }]
        neg_cnt = min(255, len(neg_concord_items))

        # Vocative detection
        has_vocative = any(t in {
            "panie", "pani", "profesorze", "doktorze", "dyrektorze", "mamo", "tato"
        } for t in low_tokens[:3])

        # ── AMSV Resonance Protocol ──────────────────────────────────────────
        # Read Syntax Sub-AI's result (0x10: genitive_neg_flag) and
        # Pragmatic Sub-AI's result (0x15: honorific_score, 0x16: register_code)
        # to modulate Editorial scores before writing.
        case_score = 100
        resonance_conflict = False

        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            genitive_neg_flag  = amsv_buffer[0x10]
            syntax_score       = amsv_buffer[0x12]
            honorific_score    = amsv_buffer[0x15]
            pragmatic_register = amsv_buffer[0x16]

            # Rule 1: Syntax sub-AI detected genitive of negation violation
            # → Editorial amplifies the case score penalty
            if genitive_neg_flag == 0:
                case_score = max(0, 50 - (10 * neg_cnt))  # Harder penalty
                neg_cnt = min(255, neg_cnt + 1)            # Resonance increment

            # Rule 2: Pragmatic register is informal (1) but syntax_score is high (>85)
            # → Possible register mismatch: formal syntax with informal address
            # → Flag as resonance conflict, suppress false positive vocative
            if pragmatic_register == 1 and syntax_score > 85:
                resonance_conflict = True
                has_vocative = False  # Vocative is unlikely in genuinely informal text

            # Rule 3: If honorific_score is critically low (<60) under formal register
            # → Case score also takes a moderate hit (honorific failure IS a case of
            #   syntactic address concord failure)
            if pragmatic_register == 2 and honorific_score < 60:
                case_score = max(0, case_score - 20)

        # ── Zero-Bridge AMSV Memory Writes ──────────────────────────────────
        # Byte 0x11: aspect_type (0=neutral, 1=impf, 2=pf)
        # Byte 0x13: case_score (resonance-modulated)
        # Byte 0x18: neg_concord_count (resonance-incremented if needed)
        # Byte 0x19: vocative_flag
        # Byte 0x37: sub_ai_editorial execution bitmask (0x08)
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[0x11] = asp_res["aspect_code"]
            amsv_buffer[0x13] = max(0, min(100, case_score))
            amsv_buffer[0x18] = neg_cnt
            amsv_buffer[0x19] = 1 if has_vocative else 0
            amsv_buffer[0x37] = 0x08  # Editorial Sub-AI executed

        return {
            "sub_ai": "EditorialSubAI",
            "dominant_aspect": asp_res["dominant_aspect"],
            "aspect_code": asp_res["aspect_code"],
            "negative_concord_count": neg_cnt,
            "vocative_detected": has_vocative,
            "case_score": case_score,
            "resonance_conflict": resonance_conflict,
            "resonance_protocol": "active"
        }
