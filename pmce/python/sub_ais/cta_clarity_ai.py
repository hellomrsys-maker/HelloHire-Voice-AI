"""
cta_clarity_ai.py — Call to Action & Decisive Closure Sub-AI (PMCE)
"""
from __future__ import annotations
from typing import Dict, Any

class CallToActionAI:
    STRONG_CTA = [
        "recommend", "propose", "suggest", "we should move forward with",
        "the next step is", "let's agree on", "i plan to", "i urge"
    ]
    WEAK_ENDINGS = [
        "i think maybe", "could potentially", "might possibly",
        "something like that", "kind of approach possibly", "i'm not sure"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        strong_hits = sum(1 for c in self.STRONG_CTA if c in l)
        weak_hits = sum(1 for w in self.WEAK_ENDINGS if w in l)

        cta_base = 0.20 if strong_hits == 0 else min(1.0, 0.40 + strong_hits * 0.25)
        weak_penalty = min(0.40, weak_hits * 0.18)
        composite = max(0.0, min(1.0, cta_base - weak_penalty))

        # Check closing sentence
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        last_sentence = sentences[-1].lower() if sentences else ""
        closing_cta = any(v in last_sentence for v in self.STRONG_CTA)

        return {
            "sub_ai": "cta",
            "strong_cta_signals": strong_hits,
            "weak_ending_count": weak_hits,
            "closing_cta_present": closing_cta,
            "composite_score": round(composite, 3)
        }
