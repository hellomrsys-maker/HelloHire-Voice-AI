"""Turkish Consonant Mutation Skill.

Handles consonant lenition (ünsüz yumuşaması: p->b, ç->c, t->d, k->ğ)
and consonant assimilation/devoicing (ünsüz benzeşmesi: d->t, c->ç).
"""

import json
import os
from typing import Dict, Any, Optional, List
from .tokenization import TurkishTokenizer


class TurkishConsonantMutationEngine:
    VOICELESS_CONSONANTS = {"f", "s", "t", "k", "ç", "ş", "h", "p"}

    LENITION_MAP = {
        "p": "b",
        "ç": "c",
        "t": "d",
        "k": "ğ"
    }

    ASSIMILATION_MAP = {
        "d": "t",
        "c": "ç"
    }

    DEFAULT_EXCEPTIONS = {
        "top", "ip", "kat", "saç", "süt", "ot", "at", "ak", "et",
        "hukuk", "devlet", "millet", "cumhuriyet", "saat", "sanat", "hayat", "bilet", "dikkat"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "consonant_mutation_matrix.json")

        self.exceptions = set(self.DEFAULT_EXCEPTIONS)
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.exceptions.update(data.get("non_leniting_exceptions", []))

    def can_lenite(self, stem: str) -> bool:
        """Determines if the final consonant of a stem undergoes softening before vowels."""
        s_low = TurkishTokenizer.turkish_lower(stem.strip())
        if not s_low:
            return False

        last_char = s_low[-1]
        if last_char not in self.LENITION_MAP:
            return False

        # Check exceptions
        if s_low in self.exceptions:
            return False

        return True

    def apply_lenition(self, stem: str) -> str:
        """Applies intervocalic softening to the final consonant of the stem."""
        if not self.can_lenite(stem):
            return stem

        last_char = TurkishTokenizer.turkish_lower(stem[-1])
        softened = self.LENITION_MAP.get(last_char, last_char)
        # Preserve original casing
        if stem[-1].isupper():
            softened = softened.upper()
        return stem[:-1] + softened

    def ends_with_voiceless(self, stem: str) -> bool:
        """Checks if the stem ends in a voiceless consonant (Fıstıkçı Şahap)."""
        s_low = TurkishTokenizer.turkish_lower(stem.strip())
        if not s_low:
            return False
        return s_low[-1] in self.VOICELESS_CONSONANTS

    def assimilate_suffix(self, stem: str, suffix: str) -> str:
        """Devoices initial 'd' or 'c' in suffix if stem ends with a voiceless consonant."""
        if not suffix or not self.ends_with_voiceless(stem):
            return suffix

        first_char = TurkishTokenizer.turkish_lower(suffix[0])
        if first_char in self.ASSIMILATION_MAP:
            devoiced = self.ASSIMILATION_MAP[first_char]
            if suffix[0].isupper():
                devoiced = devoiced.upper()
            return devoiced + suffix[1:]
        return suffix
