"""
Ukrainian parity summarizer. Extractive sentence ranking scored through the
English-parity pipeline so the summary spine is understood in English first.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from engine_common.base_orchestrator import BaseEngineOrchestrator
from engine_common.language_profile import get_profile


class UkrainianParitySummarizer:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        self.profile = get_profile("Ukrainian_engine")
        self.orch = BaseEngineOrchestrator(profile=self.profile, amsv_view=amsv_view)

    def _split_sentences(self, text: str) -> List[str]:
        buf, out = "", []
        for ch in text:
            buf += ch
            if ch in self.profile.sentence_terminators:
                out.append(buf.strip()); buf = ""
        if buf.strip():
            out.append(buf.strip())
        return [s for s in out if s]

    def summarize(self, text: str, max_sentences: int = 2) -> Dict[str, Any]:
        sentences = self._split_sentences(text)
        scored = []
        for s in sentences:
            out = self.orch.process(s)
            scored.append((out.overall_linguistic_score, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        summary = " ".join(s for _, s in scored[:max_sentences])
        return {
            "language": self.profile.language_name,
            "sentence_count": len(sentences),
            "summary": summary or text,
            "selected": [s for _, s in scored[:max_sentences]],
        }
