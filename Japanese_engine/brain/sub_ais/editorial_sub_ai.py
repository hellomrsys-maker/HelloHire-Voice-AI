"""
Japanese Editorial Sub-AI Module
================================
Dedicated artificial intelligence for Japanese stylistic polish, readability optimization,
kanji density balancing, and detection of stylistic flaws (ら抜き・さ入れ・重言・文体のねじれ).
Synchronously maps to physical memory addresses in AMSV (offset 0x38).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.rules.rules_engine import JapaneseRulesEngine, JapaneseRuleViolation


@dataclass
class JapaneseEditorialEvaluation:
    text: str
    kanji_density: float
    style_violations: List[JapaneseRuleViolation]
    token_count: int
    editorial_grade: str  # "S", "A", "B", "C"
    quality_score: float
    amsv_synced: bool


class JapaneseEditorialSubAI:
    """
    Editorial Sub-AI ensuring Japanese orthographic elegance, kanji readability, and stylistic purity.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.tokenizer = JapaneseTokenizer()
        self.rules_engine = JapaneseRulesEngine()

    def evaluate(self, text: str) -> JapaneseEditorialEvaluation:
        tokens = self.tokenizer.tokenize(text)
        violations = self.rules_engine.check_text(text)
        reg = self.rules_engine.detect_register(text)

        total_chars = len(text)
        kanji_chars = len(re.findall(r"[\u4e00-\u9faf]", text))
        kanji_ratio = round(kanji_chars / max(1, total_chars), 3)

        style_violations = [v for v in violations if v.category in {"style", "keigo"}]

        # Quality scoring
        # Optimal Japanese kanji ratio in general writing is 0.25 to 0.40
        density_penalty = 0.0
        if kanji_ratio > 0.50:
            density_penalty = (kanji_ratio - 0.50) * 0.5
        elif kanji_ratio < 0.10 and total_chars > 20:
            density_penalty = (0.10 - kanji_ratio) * 0.5

        error_penalty = len(style_violations) * 0.15
        quality = max(0.0, min(1.0, 1.0 - density_penalty - error_penalty))

        # Grade assignment
        if quality >= 0.90 and len(style_violations) == 0:
            grade = "S"
        elif quality >= 0.78:
            grade = "A"
        elif quality >= 0.60:
            grade = "B"
        else:
            grade = "C"

        # ZERO-BRIDGE SYNCHRONOUS MEMORY WRITE
        # Direct physical memory write to AMSV Offset 0x38 (Attention State & Cognitive index 3)
        focus_mask = (len(style_violations) & 0xFF) | (int(quality * 255) << 8)
        self.amsv.set_attention_state(focus_mask)
        self.amsv.set_cognitive_score(3, quality)  # Capability 3: Style/Editorial

        return JapaneseEditorialEvaluation(
            text=text,
            kanji_density=kanji_ratio,
            style_violations=style_violations,
            token_count=len(tokens),
            editorial_grade=grade,
            quality_score=round(quality, 3),
            amsv_synced=True,
        )
