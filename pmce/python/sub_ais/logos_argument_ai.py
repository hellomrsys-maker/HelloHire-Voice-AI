"""
logos_argument_ai.py — Logical Argumentation, Evidence Chain & Syllogism Sub-AI (PMCE)
"""
from __future__ import annotations
import re
from typing import Dict, Any

class LogosAI:
    LOGICAL_CONNECTORS = [
        "because", "therefore", "consequently", "hence", "it follows that", "given that",
        "evidence suggests", "data shows", "studies indicate", "specifically", "in contrast",
        "firstly", "secondly", "in order to", "as a result"
    ]
    FALLACY_CUES = [
        "everyone knows", "it's obvious", "always", "never", "you can't deny",
        "obviously", "clearly without doubt", "no question about it"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        logic_hits = sum(1 for c in self.LOGICAL_CONNECTORS if c in l)
        fallacy_hits = sum(1 for f in self.FALLACY_CUES if f in l)
        has_data = bool(re.search(r'\d+\s*%|\$\d+|\d+x\b|p-value|\bROI\b|\bbenchmarks?\b', text))
        logic_score = min(1.0, 0.30 + logic_hits * 0.14 + (0.20 if has_data else 0.0))
        fallacy_penalty = min(0.40, fallacy_hits * 0.15)
        composite = max(0.0, min(1.0, logic_score - fallacy_penalty))
        return {
            "sub_ai": "logos",
            "logic_connectors": logic_hits,
            "fallacy_count": fallacy_hits,
            "data_backed": has_data,
            "composite_score": round(composite, 3)
        }
