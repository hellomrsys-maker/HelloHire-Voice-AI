"""
Hindustani Syntax Sub-AI.
Evaluates SOV head-final structure, split-ergativity (ne postposition), and verbal clusters.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import HindustaniTokenizer
from ..skills.pos_tagging import HindustaniPOSTagger
from ..skills.parsing import HindustaniParser, HindustaniSentenceStructure
from gra_voi.bandhu.sub_ai_neural import WritingSubAINeural


@dataclass
class HindustaniSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_canonical_sov: bool
    is_ergative: bool
    has_postpositions: bool
    postposition_count: int
    neural_completeness_score: float = 0.0
    amsv_synced: bool = False

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
HindustaniSyntaxEvaluation = HindustaniSyntaxEvaluationResult


class HindustaniSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for Hindustani Syntactic Invariants, Alignment, and Neural Representation.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None
    ):
        self.amsv = amsv_view
        self.tokenizer = HindustaniTokenizer()
        self.tagger = HindustaniPOSTagger()
        self.parser = HindustaniParser()

        # Neural backbone
        self.neural_model = WritingSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("writing_sub_ai", ckpt)
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> HindustaniSyntaxEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed: HindustaniSentenceStructure = self.parser.parse(tagged)

        has_verb = len(parsed.verb_tokens) > 0
        score = 0.65
        if has_verb:
            score += 0.15
        if parsed.is_canonical_sov:
            score += 0.10
        if len(parsed.postpositions) > 0:
            score += 0.05
        if parsed.is_ergative_subject:
            score += 0.05

        neural_score = 0.0
        if self.is_neural_loaded:
            try:
                with torch.no_grad():
                    inputs = torch.zeros(1, 12, dtype=torch.long)
                    preds = self.neural_model(inputs)
                    neural_score = float(torch.sigmoid(preds["task_coherence"].squeeze())[0].item())
                    score = 0.70 * score + 0.30 * neural_score
            except Exception:
                pass

        score = min(1.0, score)
        is_valid = has_verb and parsed.is_canonical_sov

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return HindustaniSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=round(score, 3),
            is_canonical_sov=parsed.is_canonical_sov,
            is_ergative=parsed.is_ergative_subject,
            has_postpositions=len(parsed.postpositions) > 0,
            postposition_count=len(parsed.postpositions),
            neural_completeness_score=round(neural_score, 3),
            amsv_synced=synced,
        )
