"""
Dutch Diminutive Morphology & Neuter Gender Coercion Engine
Implements the 5 allomorph rules (-tje, -je, -pje, -etje, -kje)
and enforces the absolute grammatical neuter gender invariant ('het').
"""

from typing import Dict, Any, Optional

class DutchDiminutiveEngine:
    def __init__(self):
        self.diminutive_suffixes = ("tje", "je", "pje", "etje", "kje")
        self.short_vowels = {"a", "e", "i", "o", "u"}
        self.long_vowel_digraphs = {"aa", "ee", "oo", "uu", "ie", "oe", "eu", "ei", "ij", "ou", "au", "ui"}

    def is_diminutive(self, word: str) -> bool:
        low = word.lower()
        return any(low.endswith(suf) for suf in self.diminutive_suffixes) and len(low) > 3

    def generate_diminutive(self, base_noun: str) -> Dict[str, str]:
        """
        Derives the standard diminutive for a Dutch base noun.
        Always returns grammatical gender 'neuter' and article 'het'.
        """
        w = base_noun.lower().strip()
        if not w:
            return {"base": "", "diminutive": "", "article": "het", "plural": ""}

        diminutive = ""
        rule_applied = ""

        # 1. Unstressed -ing -> -nkje
        if w.endswith("ing"):
            diminutive = w[:-2] + "nkje"
            rule_applied = "kje (ing -> nkje)"

        # 2. Ends in -m preceded by long vowel / diphthong / schwa -> -pje
        elif w.endswith("m"):
            # e.g., boom, raam, bloem, bodem
            if any(w[:-1].endswith(dg) for dg in self.long_vowel_digraphs) or w.endswith("em") or w.endswith("am"):
                diminutive = w + "pje"
                rule_applied = "pje (long vowel/schwa + m)"
            else:
                diminutive = w + "metje"
                rule_applied = "etje (short vowel + m)"

        # 3. Short vowel + single liquid/nasal (l, r, n, m, ng) -> -etje
        elif (len(w) >= 3 and w[-1] in {"l", "r", "n", "m", "g"} and
              w[-2] in self.short_vowels and (len(w) == 3 or w[-3] not in self.short_vowels)):
            last_char = w[-1]
            if last_char == "g" and w.endswith("ng"):
                diminutive = w + "etje"  # ring -> ringetje
            else:
                diminutive = w + last_char + "etje"  # bal -> balletje, man -> mannetje
            rule_applied = "etje (short vowel + liquid/nasal)"

        # 4. Voiceless obstruents /p, t, k, s, f/ or /d, b/ -> -je
        elif w.endswith(("p", "t", "k", "s", "f", "d", "b", "ch")):
            diminutive = w + "je"
            rule_applied = "je (obstruents)"

        # 5. Long open single vowels -> double vowel + tje (auto -> autootje, oma -> omaatje)
        elif w[-1] in {"a", "o", "u"}:
            diminutive = w + w[-1] + "tje"
            rule_applied = "tje (vowel doubling)"

        # 6. Default to -tje (vowels, diphthongs, l, r, n with long vowels/schwa)
        else:
            diminutive = w + "tje"
            rule_applied = "tje (general sonorant/diphthong)"

        return {
            "base": base_noun,
            "diminutive": diminutive,
            "article": "het",
            "plural": diminutive + "s",
            "rule": rule_applied
        }

    def verify_diminutive_concord(self, article: str, noun: str) -> Dict[str, Any]:
        """
        Validates that a diminutive noun is correctly paired with neuter 'het' (or plural 'de').
        """
        art_low = article.lower()
        noun_low = noun.lower()

        is_dim = self.is_diminutive(noun_low)
        if not is_dim:
            return {"valid": True, "error": None}

        is_plural = noun_low.endswith("s")
        if is_plural:
            # Plural diminutives take 'de' (de huisjes)
            if art_low in {"de", "alle"}:
                return {"valid": True, "error": None}
            elif art_low == "het":
                return {
                    "valid": False,
                    "error": f"Plural diminutive '{noun}' takes article 'de', not 'het'."
                }
        else:
            # Singular diminutives obligatorily take 'het'
            if art_low in {"het", "een", "geen", "elk", "ieder", "dit", "dat"}:
                return {"valid": True, "error": None}
            elif art_low in {"de", "deze", "die"}:
                return {
                    "valid": False,
                    "error": f"Diminutive Neuter Violation: Diminutive noun '{noun}' is strictly neuter and requires article 'het', never '{article}'."
                }

        return {"valid": True, "error": None}
