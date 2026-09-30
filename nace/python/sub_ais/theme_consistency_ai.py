"""
theme_consistency_ai.py — Evaluates candidate professional identity and core thesis stability.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional

THEME_KEYWORDS = {
    "systems_infrastructure": [
        "architecture", "distributed", "scalability", "latency", "storage",
        "database", "reliability", "infrastructure", "backend", "concurrency"
    ],
    "product_user_experience": [
        "user", "customer", "ux", "ui", "retention", "engagement",
        "conversion", "feature", "frontend", "interface"
    ],
    "data_ai_ml": [
        "model", "dataset", "training", "inference", "pipeline",
        "feature engineering", "accuracy", "analytics", "bigquery", "tensor"
    ],
    "engineering_leadership": [
        "mentorship", "hiring", "roadmap", "stakeholders", "team",
        "culture", "delivery", "process", "cross-functional", "velocity"
    ]
}


class ThemeConsistencyAI:
    """
    Tracks theme progression across turns to measure stability of professional identity.
    """

    def __init__(self):
        self.theme_history: List[str] = []

    def evaluate(self, current_text: str) -> Dict[str, Any]:
        cleaned = current_text.lower()
        words = set(re.findall(r"\b[a-z0-9\-]+\b", cleaned))

        theme_counts: Dict[str, int] = {}
        for theme, kws in THEME_KEYWORDS.items():
            count = sum(1 for kw in kws if kw in words or ((" " in kw) and (kw in cleaned)))
            theme_counts[theme] = count

        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        top_theme, top_count = sorted_themes[0]

        if top_count == 0:
            dominant_theme = self.theme_history[-1] if self.theme_history else "general_engineering"
        else:
            dominant_theme = top_theme

        self.theme_history.append(dominant_theme)

        # Measure stability: fraction of turns matching dominant theme
        dominant_occurrences = sum(1 for t in self.theme_history if t == dominant_theme)
        stability = dominant_occurrences / max(len(self.theme_history), 1)

        return {
            "dominant_theme": dominant_theme,
            "theme_stability_score": round(stability, 3),
            "total_turns_tracked": len(self.theme_history),
            "theme_distribution": theme_counts,
            "is_stable": stability >= 0.50
        }
