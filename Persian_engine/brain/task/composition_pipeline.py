"""
Persian Composition Task Pipeline
Synthesizes styled Persian prose, converts Tehrani spoken forms into Standard
Literary Persian, and enriches discourse with classical proverbs.
"""

from typing import Dict, Any, List
import re
from Persian_engine.brain.skills.generation import PersianGenerator
from Persian_engine.brain.analysis.taarof_deference_analyzer import COLLOQUIAL_LEAKS

PERSIAN_PROVERBS = [
    {
        "proverb": "هر چه کنی به خود کنی گر همه نیک و بد کنی",
        "theme": "karma_reciprocity",
        "meaning": "Whatever you do, good or bad, you do unto yourself."
    },
    {
        "proverb": "جوجه را آخر پاییز می‌شمارند",
        "theme": "patience_results",
        "meaning": "Don't count your chickens before they hatch."
    },
    {
        "proverb": "با یک گل بهار نمی‌شود",
        "theme": "collective_action",
        "meaning": "One flower does not make spring."
    },
    {
        "proverb": "دل به دل راه دارد",
        "theme": "mutual_affection",
        "meaning": "Hearts find a way to each other."
    }
]

class PersianCompositionPipeline:
    """
    Styled prose composition, dialect normalization, and literary enrichment.
    """

    def __init__(self):
        self.generator = PersianGenerator()

    def normalize_colloquial_to_literary(self, colloquial_text: str) -> str:
        """
        Converts Tehrani spoken forms (e.g. تهرون, نون, خونه, میره)
        into standard written Literary Persian (تهران, نان, خانه, می‌رود).
        """
        words = colloquial_text.split()
        normalized_words = []
        for w in words:
            # Strip punctuation for lookup
            clean = re.sub(r'[،؛.؟!«»]', '', w)
            punct = w.replace(clean, '')
            if clean in COLLOQUIAL_LEAKS:
                replacement = COLLOQUIAL_LEAKS[clean]
                normalized_words.append(f"{replacement}{punct}")
            else:
                normalized_words.append(w)
        return " ".join(normalized_words)

    def inject_classical_proverb(self, text: str, theme: str) -> str:
        """Enriches Persian prose with an authentic classical proverb matching a given theme."""
        matched = [p for p in PERSIAN_PROVERBS if p["theme"] == theme]
        if matched:
            proverb = matched[0]["proverb"]
            return f"{text.strip()} همان‌طور که در ضرب‌المثل کهن فارسی آمده است: «{proverb}»."
        return text
