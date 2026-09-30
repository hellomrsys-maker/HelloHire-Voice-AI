"""
English Editorial Sub-AI Module.
Dedicated artificial intelligence for stylistic polish, readability optimization,
cadence and rhythm, error taxonomy classification, and proactive editorial suggestions.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView.
Writes ONLY to designated sync offsets:
- Capability 2 (Discourse / Structure / Cohesion Q16): Offset 0x14 (Byte 20)
- Capability 5 (Critical Review / Error Analysis Q16): Offset 0x1A (Byte 26)
"""

from __future__ import annotations
import os
import re
import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.rules.rules_engine import RulesEngine, RuleViolation
from gra_voi.bandhu.sub_ai_neural import ReviewingSubAINeural, BookWritingSubAINeural


@dataclass
class EditorialEvaluation:
    text: str
    readability_score: float  # Flesch-Kincaid grade
    style_violations: List[RuleViolation]
    word_count: int
    sentence_count: int
    lexical_diversity: float
    editorial_grade: str  # "A", "B", "C", "D"
    dominant_error_tier: str
    hedging_score: float
    tense_collision_risk: float
    current_editing_stage: str
    amsv_synced: bool


class EnglishEditorialSubAI:
    """
    Editorial Sub-AI managing stylistic elegance, readability, 4-tier error taxonomy,
    and narrative tense consistency via rule-based and trained neural heads.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.tokenizer = EnglishTokenizer()
        self.rules_engine = RulesEngine()

        # Neural backbones: ReviewingSubAINeural + BookWritingSubAINeural
        self.reviewing_model = ReviewingSubAINeural()
        self.book_writing_model = BookWritingSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                if "reviewing_sub_ai" in ckpt:
                    self.reviewing_model.load_state_dict(ckpt["reviewing_sub_ai"])
                elif "reviewing" in ckpt:
                    self.reviewing_model.load_state_dict(ckpt["reviewing"])

                if "book_writing_sub_ai" in ckpt:
                    self.book_writing_model.load_state_dict(ckpt["book_writing_sub_ai"])
                elif "book_writing" in ckpt:
                    self.book_writing_model.load_state_dict(ckpt["book_writing"])

                self.is_neural_loaded = True
            except Exception:
                pass

        self.reviewing_model.eval()
        self.book_writing_model.eval()

    def evaluate(self, text: str) -> EditorialEvaluation:
        tokens = self.tokenizer.tokenize(text)
        words = [t.text.lower() for t in tokens if t.is_word]
        sentences = self.tokenizer.split_sentences(text)
        violations = self.rules_engine.check_text(text)
        reg = self.rules_engine.detect_register(text)

        total_words = len(words)
        total_sents = max(1, len(sentences))
        unique_words = len(set(words))
        ttr = unique_words / max(1, total_words)

        style_violations = [v for v in violations if v.category == "style"]

        # Neural analysis via ReviewingSubAINeural & BookWritingSubAINeural
        try:
            rev_res = self.reviewing_model.analyze_text(text)
            dominant_err = str(rev_res.get("dominant_error_tier", "None"))
            hedging = float(rev_res.get("hedging_score", 0.50))
        except Exception:
            dominant_err = "None"
            hedging = 0.50

        try:
            bk_res = self.book_writing_model.analyze_text(text)
            tense_risk = float(bk_res.get("tense_collision_risk", 0.05))
            stage = str(bk_res.get("current_editing_stage", "Line"))
            consistency = float(bk_res.get("consistency_score", 0.90))
        except Exception:
            tense_risk = 0.05
            stage = "Line"
            consistency = 0.90

        # Grade assignment
        if len(violations) == 0 and ttr > 0.5 and tense_risk < 0.2:
            grade = "A"
            quality_num = 0.95
        elif len(violations) <= 2:
            grade = "B"
            quality_num = 0.80
        elif len(violations) <= 5:
            grade = "C"
            quality_num = 0.65
        else:
            grade = "D"
            quality_num = 0.45

        # ZERO-BRIDGE SYNCHRONOUS MEMORY WRITE
        # Writes strictly and exclusively to designated sync offsets:
        # 1. Capability 2 (Discourse / Structure / Cohesion Q16): Offset 0x14 (Byte 20)
        discourse_score = round(max(0.0, min(1.0, 0.5 * quality_num + 0.5 * consistency)), 4)
        self.amsv.set_cognitive_score(2, discourse_score)

        # 2. Capability 5 (Critical Review / Error Analysis Q16): Offset 0x1A (Byte 26)
        reviewing_score = round(max(0.0, min(1.0, 1.0 - (len(violations) * 0.15))), 4)
        self.amsv.set_cognitive_score(5, reviewing_score)

        return EditorialEvaluation(
            text=text,
            readability_score=reg.readability_grade,
            style_violations=style_violations,
            word_count=total_words,
            sentence_count=total_sents,
            lexical_diversity=round(ttr, 3),
            editorial_grade=grade,
            dominant_error_tier=dominant_err,
            hedging_score=round(hedging, 4),
            tense_collision_risk=round(tense_risk, 4),
            current_editing_stage=stage,
            amsv_synced=True,
        )
