"""
French Liaison & Elision Skill.
Evaluates phonological boundary phenomena: elision compliance, h aspiré prevention,
and compulsory vs forbidden liaison contexts.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class LiaisonElisionEngine:
    """
    Phonological engine assessing French elision, h aspiré boundaries, and liaison realizations.
    """

    VOWELS = {"a", "e", "i", "o", "u", "y", "é", "è", "ê", "ë", "à", "â", "î", "ï", "ô", "û", "ù"}

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent.parent / "rules" / "liaison_elision_rules.json")
        self.rules_path = rules_path
        self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except Exception:
            self.db = {
                "elision": {
                    "triggers": ["l'", "d'", "c'", "j'", "m'", "t'", "s'", "n'", "qu'"],
                    "vowel_starters": list(self.VOWELS),
                    "h_aspire_exceptions": ["héros", "haricot", "honte", "hasard", "hauteur", "hache", "hibou"]
                },
                "liaison": {
                    "sound_shifts": {"s": "z", "x": "z", "d": "t", "n": "n", "t": "t"}
                }
            }
        self.h_aspire_list = set(self.db.get("elision", {}).get("h_aspire_exceptions", []))

    def is_h_aspire(self, word: str) -> bool:
        """Returns True if the word begins with an aspirated h (preventing elision and liaison)."""
        clean = word.lower().strip("«»\"',.?!")
        return clean in self.h_aspire_list

    def evaluate_elision(self, token1: str, token2: str) -> Dict[str, Any]:
        """
        Evaluates whether elision should occur between token1 and token2,
        and flags erroneous elision (e.g. before h aspiré) or missing elision.
        """
        t1 = token1.lower()
        t2 = token2.lower().strip("«»\"',.?!")

        is_h_asp = self.is_h_aspire(t2)
        starts_vowel = len(t2) > 0 and (t2[0] in self.VOWELS or (t2[0] == 'h' and not is_h_asp))

        # Check if t1 is an unelided word that should have elided (e.g., "le ami", "je aime")
        unelided_candidates = {"le", "la", "de", "ce", "je", "me", "te", "se", "ne", "que"}
        if t1 in unelided_candidates and starts_vowel and not is_h_asp:
            return {
                "is_valid": False,
                "error_type": "missing_elision",
                "message": f"Élision requise: '{t1} {t2}' devrait s'écrire avec apostrophe (ex: {t1[0]}'{t2}).",
                "recommended": f"{t1[0]}'{t2}"
            }

        # Check if t1 is an elided prefix preceding an h aspiré (e.g., "l'héros")
        if t1.endswith("'") and is_h_asp:
            full_word = "le" if t1 in {"l'", "c'"} else t1.replace("'", "e")
            return {
                "is_valid": False,
                "error_type": "illicit_elision_h_aspire",
                "message": f"Élision interdite devant le 'h' aspiré de '{t2}' (écrire '{full_word} {t2}').",
                "recommended": f"{full_word} {t2}"
            }

        return {
            "is_valid": True,
            "error_type": None,
            "message": "Élision correcte ou non requise."
        }

    def evaluate_liaison(self, word1: str, word2: str) -> Dict[str, Any]:
        """
        Evaluates liaison potential and phonetic realization between two consecutive words.
        """
        w1 = word1.lower().strip("«»\"',.?!")
        w2 = word2.lower().strip("«»\"',.?!")

        if not w1 or not w2:
            return {"has_liaison": False, "reason": "empty"}

        # Forbidden liaison after "et"
        if w1 == "et":
            return {
                "has_liaison": False,
                "is_forbidden": True,
                "reason": "forbidden_after_et"
            }

        # Forbidden liaison before h aspiré
        if self.is_h_aspire(w2):
            return {
                "has_liaison": False,
                "is_forbidden": True,
                "reason": "forbidden_before_h_aspire"
            }

        # Check if w2 starts with a vowel or mute h
        starts_vocalic = len(w2) > 0 and (w2[0] in self.VOWELS or (w2[0] == 'h' and not self.is_h_aspire(w2)))
        if not starts_vocalic:
            return {"has_liaison": False, "reason": "consonant_onset"}

        # Check if w1 ends with a liaison consonant (s, x, z, d, t, n, p, r)
        final_char = w1[-1]
        sound_shifts = self.db.get("liaison", {}).get("sound_shifts", {"s": "z", "x": "z", "d": "t", "n": "n", "t": "t"})

        if final_char in sound_shifts:
            phonetic_liaison = sound_shifts[final_char]
            return {
                "has_liaison": True,
                "is_compulsory": w1 in {"les", "des", "aux", "un", "mon", "ton", "son", "mes", "tes", "ses", "nos", "vos", "leurs", "ils", "elles", "on", "nous", "vous", "dans", "en", "tout", "petit", "grand"},
                "liaison_consonant": final_char,
                "phonetic_realization": phonetic_liaison,
                "context": f"{w1}_{phonetic_liaison}_{w2}"
            }

        return {"has_liaison": False, "reason": "no_latent_coda"}
