"""
Tagalog parity grammar check task. Runs the shared English-parity pipeline
and reports syntax / agreement style issues derived from the Tagalog profile.
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from engine_common.base_orchestrator import BaseEngineOrchestrator
from engine_common.language_profile import get_profile


class TagalogParityGrammarChecker:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        self.profile = get_profile("Tagalog_engine")
        self.orch = BaseEngineOrchestrator(profile=self.profile, amsv_view=amsv_view)

    def check(self, text: str) -> Dict[str, Any]:
        out = self.orch.process(text)
        issues = []
        if out.syntax_sub_ai.score < 0.6:
            issues.append({"type": "syntax", "detail": "low syntactic integrity"})
        if not any(text.strip().endswith(t) for t in self.profile.sentence_terminators):
            issues.append({"type": "punctuation", "detail": "missing terminal punctuation"})
        return {
            "language": self.profile.language_name,
            "text": text,
            "english_projection": out.english_pivot.english_projection,
            "syntax_score": out.syntax_sub_ai.score,
            "overall_score": out.overall_linguistic_score,
            "issues": issues,
            "is_valid": len(issues) == 0,
        }
