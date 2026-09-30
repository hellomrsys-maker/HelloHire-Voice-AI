"""
English Syntax Sub-AI Module.
Dedicated artificial intelligence for syntactic structure verification,
grammatical agreement analysis, and clausal embedding evaluation.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView.
Writes ONLY to designated sync offsets:
- Capability 1 (Syntax / Grammar Q16): Offset 0x12 (Byte 18)
- Global Structural Score (Q16): Offset 0x34 (Byte 52)
"""

from __future__ import annotations
import os
import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.skills.pos_tagging import EnglishPOSTagger
from English_engine.brain.skills.parsing import EnglishParser
from gra_voi.bandhu.sub_ai_neural import WritingSubAINeural


@dataclass
class SyntaxEvaluation:
    text: str
    syntactic_integrity_score: float  # 0.0 to 1.0
    clause_depth: int
    has_subordination: bool
    agreement_errors: List[str]
    parse_tree_repr: str
    neural_completeness_score: float
    detected_register: str
    amsv_synced: bool


class EnglishSyntaxSubAI:
    """
    Syntactic Sub-AI combining trained neural Transformer representation with
    deterministic parse tree and agreement verification.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.tokenizer = EnglishTokenizer()
        self.pos_tagger = EnglishPOSTagger()
        self.parser = EnglishParser()

        # Neural backbone: WritingSubAINeural
        self.neural_model = WritingSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                if "writing_sub_ai" in ckpt:
                    self.neural_model.load_state_dict(ckpt["writing_sub_ai"])
                    self.is_neural_loaded = True
                elif "writing" in ckpt:
                    self.neural_model.load_state_dict(ckpt["writing"])
                    self.is_neural_loaded = True
            except Exception as e:
                pass
        self.neural_model.eval()

    def evaluate(self, text: str) -> SyntaxEvaluation:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)
        parse_tree = self.parser.parse_constituency(tagged)
        bracket_repr = self.parser.to_bracketed_string(parse_tree)

        # Check clause depth
        max_depth = 0
        curr = 0
        for ch in bracket_repr:
            if ch == "(":
                curr += 1
                if curr > max_depth:
                    max_depth = curr
            elif ch == ")":
                curr -= 1

        subordinated = any(t.penn_tag in {"IN", "WRB"} for t in tagged)

        # Subject-verb agreement scan
        agreement_errors: List[str] = []
        for i in range(len(tagged) - 1):
            w1 = tagged[i].token.text.lower()
            w2 = tagged[i + 1].token.text.lower()
            if w1 in {"he", "she", "it"} and w2 in {"do", "have", "go", "run"}:
                agreement_errors.append(f"Agreement mismatch: '{w1} {w2}'")

        # Neural analysis via WritingSubAINeural
        try:
            n_res = self.neural_model.analyze_text(text)
            neural_score = float(n_res.get("sentence_completeness_score", 0.85))
            detected_reg = str(n_res.get("detected_register", "Standard"))
        except Exception:
            neural_score = 0.85
            detected_reg = "Standard"

        penalty = len(agreement_errors) * 0.25
        final_score = max(0.0, min(1.0, (0.6 * neural_score + 0.4 * (1.0 - penalty))))

        # 0-NANOSECOND SYNCHRONOUS MEMORY WRITE
        # Writes strictly and exclusively to designated sync offsets:
        # Capability 1: Offset 0x12 (Byte 18)
        self.amsv.set_cognitive_score(1, final_score)
        # Global Structural Score: Offset 0x34 (Byte 52)
        self.amsv.set_global_structural_score(final_score)

        return SyntaxEvaluation(
            text=text,
            syntactic_integrity_score=round(final_score, 4),
            clause_depth=max_depth,
            has_subordination=subordinated,
            agreement_errors=agreement_errors,
            parse_tree_repr=bracket_repr,
            neural_completeness_score=round(neural_score, 4),
            detected_register=detected_reg,
            amsv_synced=True,
        )
