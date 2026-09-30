"""
ethos_credibility_ai.py — Credibility & Expertise Anchoring Sub-AI (PMCE)
"""
from __future__ import annotations
from typing import Dict, Any

class EthosAI:
    CREDENTIAL_CUES = [
        "in my experience", "as a", "having led", "when i architected", "my track record",
        "based on my work", "i've successfully", "i have delivered", "i managed", "i built",
        "throughout my career", "in production environments"
    ]
    EXPERT_VOCAB_CUES = [
        "roi", "kpi", "okr", "p99 latency", "consensus protocol", "systematic review",
        "differential diagnosis", "monte carlo", "regression analysis", "stakeholder",
        "fault tolerance", "distributed system", "throughput", "concurrency"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        cred = sum(1 for c in self.CREDENTIAL_CUES if c in l)
        expert = sum(1 for e in self.EXPERT_VOCAB_CUES if e in l)
        credential_score = min(1.0, cred * 0.25)
        expertise_score = min(1.0, expert * 0.18)
        composite = credential_score * 0.55 + expertise_score * 0.45
        return {
            "sub_ai": "ethos",
            "credential_signals": cred,
            "expertise_markers": expert,
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
