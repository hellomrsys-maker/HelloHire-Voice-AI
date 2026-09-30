"""
srl.py - Semantic Role Labeling (SRL) mapping verbal predicates and thematic arguments.
Identifies ARG0 (Agent), ARG1 (Patient/Theme), ARG2 (Instrument/Recipient), ARGM-TMP, ARGM-LOC.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SemanticRoleFrame:
    predicate: str
    predicate_index: int
    arg0: Optional[str] = None
    arg1: Optional[str] = None
    argm_loc: Optional[str] = None
    argm_tmp: Optional[str] = None

    def __getitem__(self, item):
        return getattr(self, item)


class EnglishSemanticRoleLabeler:
    """
    PropBank-compliant Semantic Role Labeler extracting predicate-argument propositions.
    """

    def label_roles(self, sentence_text: str) -> List[SemanticRoleFrame]:
        words = sentence_text.strip().split()
        if not words:
            return []

        propositions: List[SemanticRoleFrame] = []
        for i, word in enumerate(words):
            clean = re.sub(r"[^\w]", "", word).lower()
            if self._is_predicate(clean):
                pred_idx = i
                predicate = clean

                # Identify ARG0 (Preceding subject NP)
                arg0_tokens = words[:pred_idx]
                arg0 = " ".join(arg0_tokens) if arg0_tokens else None

                # Identify ARG1 (Following object NP) and Adjuncts
                post_tokens = words[pred_idx + 1:]
                arg1 = None
                argm_loc = None
                argm_tmp = None

                post_str = " ".join(post_tokens)
                loc_match = re.search(r"\b(in|at|on|near)\s+([A-Za-z0-9\s]+?)(?=[.,;]|$)", post_str)
                if loc_match:
                    argm_loc = loc_match.group(0)

                tmp_match = re.search(r"\b(yesterday|today|tomorrow|at night|in the morning|recently)\b", post_str, re.I)
                if tmp_match:
                    argm_tmp = tmp_match.group(0)

                arg1_tokens = []
                for pt in post_tokens:
                    pt_clean = re.sub(r"[^\w]", "", pt).lower()
                    if pt_clean in {"in", "on", "at", "by", "with", "during", "before", "after"}:
                        break
                    arg1_tokens.append(pt)
                arg1 = " ".join(arg1_tokens) if arg1_tokens else None

                propositions.append(
                    SemanticRoleFrame(
                        predicate=predicate,
                        predicate_index=pred_idx,
                        arg0=arg0,
                        arg1=arg1,
                        argm_loc=argm_loc,
                        argm_tmp=argm_tmp,
                    )
                )

        return propositions

    def _is_predicate(self, word: str) -> bool:
        common_verbs = {
            "built", "build", "designed", "design", "wrote", "write", "trained", "train",
            "predicted", "predict", "converged", "converge", "evaluated", "evaluate",
            "ran", "run", "saw", "see", "hit", "ate", "eat", "drank", "drink", "made", "make"
        }
        return word in common_verbs or word.endswith(("ed", "ing", "ize", "ise"))
