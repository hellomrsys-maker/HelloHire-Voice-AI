"""Russian Syntax Sub-AI.

Evaluates SVO constituent ordering, case concord validity,
animacy splits, and clausal dependency alignment.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18)
and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import RussianTokenizer
from ..skills.parsing import RussianDependencyParser
from ..analysis.case_government_analyzer import RussianCaseGovernmentAnalyzer


@dataclass
class RussianSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_canonical_svo: bool
    has_verb: bool
    has_subject: bool
    case_diversity_count: int
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
RussianSyntaxEvaluation = RussianSyntaxEvaluationResult


class RussianSyntaxSubAI:
    """Dedicated AI Sub-Engine for Russian Syntactic Invariants and Clausal Alignment."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = RussianTokenizer()
        self.parser = RussianDependencyParser()
        self.case_analyzer = RussianCaseGovernmentAnalyzer()

    def evaluate(self, text: str) -> RussianSyntaxEvaluationResult:
        parsed = self.parser.parse(text)
        case_res = self.case_analyzer.analyze(text)

        has_verb = any(n["deprel"] == "root" and n["pos"] == "VERB" for n in parsed["nodes"])
        has_subject = any(n["deprel"] == "nsubj" for n in parsed["nodes"])
        has_obj = any(n["deprel"] == "obj" for n in parsed["nodes"])

        # Determine SVO ordering
        is_svo = False
        if has_verb:
            subj_idx = next((n["id"] for n in parsed["nodes"] if n["deprel"] == "nsubj"), -1)
            verb_idx = parsed["root_index"]
            obj_idx = next((n["id"] for n in parsed["nodes"] if n["deprel"] == "obj"), -1)

            if subj_idx != -1 and obj_idx != -1:
                is_svo = (subj_idx < verb_idx < obj_idx)
            elif subj_idx != -1:
                is_svo = (subj_idx < verb_idx)
            else:
                is_svo = True

        score = 0.60
        if has_verb:
            score += 0.20
        if has_subject:
            score += 0.10
        if is_svo:
            score += 0.05
        if case_res["is_valid"]:
            score += 0.05

        score = min(1.0, score)
        is_valid = has_verb

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return RussianSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=score,
            is_canonical_svo=is_svo,
            has_verb=has_verb,
            has_subject=has_subject,
            case_diversity_count=case_res["case_count"],
            amsv_synced=synced
        )
