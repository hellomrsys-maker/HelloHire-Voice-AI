"""Turkish Vowel Harmony Skill.

Implements 2-fold (A-type) and 4-fold (I-type) vowel harmony assimilation rules,
vocalic feature extraction (front/back, rounded/unrounded), and word-level harmony auditing.
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple
from .tokenization import TurkishTokenizer


class TurkishVowelHarmonyEngine:
    FRONT_VOWELS = {"e", "i", "ö", "ü"}
    BACK_VOWELS = {"a", "ı", "o", "u"}
    ALL_VOWELS = FRONT_VOWELS | BACK_VOWELS

    TWO_WAY_MAP = {
        "e": "e", "i": "e", "ö": "e", "ü": "e",
        "a": "a", "ı": "a", "o": "a", "u": "a"
    }

    FOUR_WAY_MAP = {
        "e": "i", "i": "i",
        "a": "ı", "ı": "ı",
        "ö": "ü", "ü": "ü",
        "o": "u", "u": "u"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "vowel_harmony_matrix.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

    def extract_vowels(self, text: str) -> List[str]:
        """Extracts all vowels in order from a Turkish word."""
        t_low = TurkishTokenizer.turkish_lower(text)
        return [c for c in t_low if c in self.ALL_VOWELS]

    def get_last_vowel(self, text: str) -> Optional[str]:
        """Returns the last vowel in the given stem."""
        vowels = self.extract_vowels(text)
        return vowels[-1] if vowels else None

    def get_two_way_harmonic_vowel(self, stem: str) -> str:
        """Returns 'e' or 'a' according to 2-way vowel harmony for the stem."""
        last_v = self.get_last_vowel(stem)
        if not last_v:
            return "e"
        return self.TWO_WAY_MAP.get(last_v, "e")

    def get_four_way_harmonic_vowel(self, stem: str) -> str:
        """Returns 'i', 'ı', 'ü', or 'u' according to 4-way vowel harmony for the stem."""
        last_v = self.get_last_vowel(stem)
        if not last_v:
            return "i"
        return self.FOUR_WAY_MAP.get(last_v, "i")

    def check_internal_harmony(self, word: str) -> Dict[str, Any]:
        """Audits a Turkish word for internal major vowel harmony (Büyük Ünlü Uyumu)."""
        vowels = self.extract_vowels(word)
        if len(vowels) <= 1:
            return {
                "word": word,
                "is_harmonic": True,
                "vowel_count": len(vowels),
                "type": "monosyllabic_or_invariant"
            }

        first_is_front = vowels[0] in self.FRONT_VOWELS
        consistent = all((v in self.FRONT_VOWELS) == first_is_front for v in vowels[1:])

        return {
            "word": word,
            "is_harmonic": consistent,
            "vowel_count": len(vowels),
            "frontness": "front" if first_is_front else "back"
        }
