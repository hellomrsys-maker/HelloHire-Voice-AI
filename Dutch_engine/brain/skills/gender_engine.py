"""
Dutch Gender & Adjective Inflection Engine
Handles common vs neuter gender classification and verifies the
fundamental Dutch adjective zero-ending invariant (e.g. 'een mooi huis' vs 'het mooie huis').
"""

from typing import Dict, Any, List, Optional

class DutchGenderEngine:
    def __init__(self):
        # Sample neuter nouns (het)
        self.het_nouns = {
            "huis", "boek", "kind", "meisje", "dier", "water", "brood", "geld",
            "werk", "land", "dorp", "oog", "oor", "been", "raam", "jaar",
            "feest", "bier", "paard", "bed", "probleem", "voorbeeld", "leven",
            "lichaam", "hart", "idee", "resultaat", "bericht", "vliegtuig",
            "schip", "museum", "station", "stationnetje", "gesprek", "onderzoek"
        }
        # Common gender nouns (de)
        self.de_nouns = {
            "man", "vrouw", "tafel", "stoel", "hond", "kat", "auto", "stad",
            "weg", "straat", "school", "trein", "fiets", "winkel", "taal",
            "computer", "telefoon", "sleutel", "deur", "kamer", "vriend",
            "vriendin", "leraar", "lerares", "krant", "boom", "zee", "bloem",
            "bibliotheek", "universiteit", "rekening", "ketting", "woning"
        }
        self.indefinite_determiners = {"een", "geen", "welk", "ieder", "elk", "veel", "weinig"}
        self.definite_determiners = {"de", "het", "'t", "dit", "dat", "deze", "die"}

    def get_gender(self, noun: str) -> str:
        low = noun.lower().strip()
        # Diminutives are unconditionally neuter
        if low.endswith(("tje", "je", "pje", "etje", "kje")) and len(low) > 3:
            return "neuter"
        if low in self.het_nouns:
            return "neuter"
        # Most other Dutch nouns are common gender
        return "common"

    def verify_article_noun(self, article: str, noun: str) -> Dict[str, Any]:
        art_low = article.lower().strip()
        noun_low = noun.lower().strip()
        gender = self.get_gender(noun_low)

        if art_low in {"de", "deze", "die"}:
            if gender == "neuter" and not noun_low.endswith("en"): # singular
                return {
                    "valid": False,
                    "expected": "het",
                    "error": f"Gender Discord: Noun '{noun}' is neuter and requires article 'het', not '{article}'."
                }
        elif art_low in {"het", "dit", "dat"}:
            if gender == "common":
                return {
                    "valid": False,
                    "expected": "de",
                    "error": f"Gender Discord: Noun '{noun}' has common gender and requires article 'de', not '{article}'."
                }

        return {"valid": True, "gender": gender, "error": None}

    def verify_adjective_inflection(self, determiner: Optional[str], adjective: str, noun: str) -> Dict[str, Any]:
        """
        Validates the adjective inflection rule:
        - Definite: always -e ('het mooie huis', 'de mooie vrouw')
        - Indefinite neuter singular: BARE / ZERO-ENDING ('een mooi huis')
        - Indefinite common: -e ('een mooie vrouw')
        - Plural: always -e ('mooie huizen')
        """
        det_low = determiner.lower().strip() if determiner else ""
        adj_low = adjective.lower().strip()
        noun_low = noun.lower().strip()
        gender = self.get_gender(noun_low)

        # Check if adjective ends with inflectional -e
        # Inherent non-inflecting adjectives: 'oranje', 'roze', 'beige', 'lila'
        if adj_low in {"oranje", "roze", "beige", "lila"}:
            has_e_ending = False
            bare_stem = adj_low
        elif adj_low.endswith("e"):
            has_e_ending = True
            if adj_low.endswith("oie"):
                bare_stem = adj_low[:-1]  # mooie -> mooi
            elif adj_low.endswith("aie"):
                bare_stem = adj_low[:-1]  # saaie -> saai
            elif adj_low.endswith("ieuwe"):
                bare_stem = adj_low[:-1]  # nieuwe -> nieuw
            else:
                bare_stem = adj_low[:-1]
                if bare_stem.endswith(("ott", "kk", "tt", "pp", "ll", "mm", "nn", "ss")):
                    bare_stem = bare_stem[:-1]
        else:
            has_e_ending = False
            bare_stem = adj_low

        # Case 1: Indefinite singular neuter -> MUST BE ZERO-ENDING (bare stem)
        if det_low in self.indefinite_determiners or not det_low:
            if gender == "neuter" and not noun_low.endswith("en"):
                if has_e_ending:
                    return {
                        "valid": False,
                        "adjective": adjective,
                        "expected": bare_stem,
                        "error": (
                            f"Adjective Inflection Violation: Attributive adjective modifying an indefinite singular neuter noun "
                            f"('{det_low or 'Ø'} ... {noun}') must have zero-ending (bare stem: '{bare_stem}'), not '{adjective}'."
                        )
                    }
                return {"valid": True, "error": None}

        # Case 2: Definite neuter singular -> MUST HAVE -e
        if det_low in {"het", "dit", "dat"} and gender == "neuter":
            if not has_e_ending:
                return {
                    "valid": False,
                    "adjective": adjective,
                    "expected": adj_low + "e",
                    "error": (
                        f"Adjective Inflection Violation: Attributive adjective following definite neuter determiner '{determiner}' "
                        f"must take suffix '-e': '{adj_low}e {noun}'."
                    )
                }

        return {"valid": True, "error": None}
