"""Turkish Syntax Sub-AI.

Evaluates head-final SOV constituent ordering, postpositional attachment,
and clausal case agreement.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18)
and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import TurkishTokenizer
from ..skills.parsing import TurkishDependencyParser
from ..analysis.case_postposition_analyzer import TurkishCasePostpositionAnalyzer


@dataclass
class TurkishSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_canonical_sov: bool
    has_verb: bool
    has_subject: bool
    case_diversity_count: int
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
TurkishSyntaxEvaluation = TurkishSyntaxEvaluationResult


class TurkishSyntaxSubAI:
    """Dedicated AI Sub-Engine for Turkish Syntactic Invariants and SOV Clausal Alignment."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = TurkishTokenizer()
        self.parser = TurkishDependencyParser()
        self.case_analyzer = TurkishCasePostpositionAnalyzer()

    def evaluate(self, text: str) -> TurkishSyntaxEvaluationResult:
        parsed = self.parser.parse(text)
        case_res = self.case_analyzer.analyze(text)

        has_verb = any(n["deprel"] == "root" and n["pos"] == "VERB" for n in parsed["nodes"])
        has_subject = any(n["deprel"] == "nsubj" for n in parsed["nodes"])

        # SOV checking: finite verb should be sentence-final (or last content word)
        is_sov = False
        if len(parsed["nodes"]) > 0:
            last_content_idx = -1
            for n in reversed(parsed["nodes"]):
                if n["pos"] != "PUNCT":
                    last_content_idx = n["id"]
                    break
            is_sov = (parsed["root_index"] == last_content_idx)

        score = 0.65
        if has_verb:
            score += 0.15
        if has_subject:
            score += 0.10
        if is_sov:
            score += 0.05
        if case_res["is_valid"]:
            score += 0.05

        score = min(1.0, score)
        is_valid = has_verb and is_sov

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return TurkishSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=score,
            is_canonical_sov=is_sov,
            has_verb=has_verb,
            has_subject=has_subject,
            case_diversity_count=case_res["case_count"],
            amsv_synced=synced
        )
