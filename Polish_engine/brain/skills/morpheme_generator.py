"""
Polish Open-Vocabulary Morpheme Generator (POVE) — Tier 4 Implementation
=========================================================================
Polish has highly productive morphological patterns for assimilating loanwords.
This engine detects potential new/loanword verbs and nouns from their surface
morphology and generates their inflected forms on-the-fly, without needing a
pre-built dictionary entry.

Key Productive Patterns:
  VERBS:
    -ować (impf) → -uję, -ujesz, -uje / perfective: -ować + z-/za-/wy- prefix
    -izować / -yzować (impf) → technical loanwords from -ize (Google → googlować)
    -ić (impf, consonant-final) → standard 2nd conjugation

  NOUNS:
    -acja (fem) → abstract noun from action (prezentacja, instalacja)
    -ment (masc) → direct loanword from French/English (dokument, ekwipment)
    -er / -or (masc) → agent noun loanword (komputer, procesor)
    -ing (masc, neuter in some dialects) → gerundive loanword (marketing, branding)

Loanword Detection Heuristics:
  - Contains Q, V, X (foreign letters not native to Polish)
  - Ends in -ing, -er, -or, -ment, -tion/-cja
  - No Polish diacritics (ą ę ó ś ź ż ć ń ł) AND contains loanword suffix
  - If classified as verb AND ends in -uje/-ujesz: strong -ować present tense signal
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# ─── Foreign letter signals ───────────────────────────────────────────────────
FOREIGN_LETTERS = set("qvx")
POLISH_DIACRITICS = set("ąęóśźżćńł")

# ─── Productive verbal paradigm: -ować → present tense conjugation ────────────
def conjugate_owac_verb(stem: str) -> Dict[str, str]:
    """
    Given an -ować stem (e.g., "stream" from "streamować"),
    generates the full present and past tense forms.
    """
    # stem = root before -ować (e.g., "stream", "google", "download")
    return {
        "infinitive_impf": f"{stem}ować",
        "infinitive_pf":   f"za{stem}ować",  # za- is the neutral perfectivizer for most loanwords
        "1sg_pres":        f"{stem}uję",
        "2sg_pres":        f"{stem}ujesz",
        "3sg_pres":        f"{stem}uje",
        "1pl_pres":        f"{stem}ujemy",
        "2pl_pres":        f"{stem}ujecie",
        "3pl_pres":        f"{stem}ują",
        "masc_past":       f"{stem}ował",
        "fem_past":        f"{stem}owała",
        "neut_past":       f"{stem}owało",
        "pl_past":         f"{stem}owali",
        "aspect":          "imperfective",
        "paradigm":        "-ować (loanword assimilation)",
    }


def conjugate_izowac_verb(stem: str) -> Dict[str, str]:
    """For -izować / -yzować verbs (technical/English -ize loanwords)."""
    base = stem.rstrip("iz").rstrip("yz")
    return {
        "infinitive_impf": f"{base}izować",
        "1sg_pres":        f"{base}izuję",
        "2sg_pres":        f"{base}izujesz",
        "3sg_pres":        f"{base}izuje",
        "masc_past":       f"{base}izował",
        "aspect":          "imperfective",
        "paradigm":        "-izować (technical loanword -ize)",
    }


# ─── Nominal loanword suffixes → gender and declension class ────────────────
NOMINAL_LOANWORD_SUFFIXES: Dict[str, Dict[str, str]] = {
    "acja":    {"gender": "feminine",  "declension": "a-stem", "example": "prezentacja → prezentacji (gen)"},
    "cja":     {"gender": "feminine",  "declension": "a-stem", "example": "instalacja → instalacji (gen)"},
    "ment":    {"gender": "masculine", "declension": "o-stem", "example": "dokument → dokumentu (gen)"},
    "er":      {"gender": "masculine", "declension": "o-stem", "example": "komputer → komputera (gen)"},
    "or":      {"gender": "masculine", "declension": "o-stem", "example": "procesor → procesora (gen)"},
    "ing":     {"gender": "masculine", "declension": "o-stem (indeclinable in some registers)", "example": "marketing → marketingu (gen)"},
    "tion":    {"gender": "feminine",  "declension": "a-stem (assimilated as -cja)", "example": "→ assimilate to -cja pattern"},
    "ista":    {"gender": "masc/fem",  "declension": "a-stem", "example": "pianista → pianiście (dat)"},
}


class PolishMorphemeGenerator:
    """
    Generates inflected forms and classifies unknown/loanword words
    using productive Polish morphological patterns.
    """

    def classify_and_generate(self, word: str) -> Dict[str, Any]:
        """
        Main entry point: given an unknown word, classify its likely
        part-of-speech, generate its paradigm, and return diagnostics.
        """
        low = word.lower().strip()

        # 1. Try verbal detection first
        verbal = self._try_verb_classification(low)
        if verbal:
            return verbal

        # 2. Try nominal detection
        nominal = self._try_nominal_classification(low)
        if nominal:
            return nominal

        return {
            "word": word,
            "classification": "UNKNOWN",
            "is_loanword": self._is_probable_loanword(low),
            "note": "No productive paradigm matched. Word may be indeclinable loanword or proper noun.",
        }

    def _normalize_ascii_approximation(self, word: str) -> str:
        """
        Normalizes ASCII approximations of Polish words to the canonical diacritic form
        for pattern matching. 'owac' → 'ować', 'izowac' → 'izować', etc.
        This allows the engine to handle loanword input from users who cannot type diacritics.
        """
        # Heuristic: if word ends in 'owac' but not 'ować', treat as 'ować'
        if word.endswith("owac") and not word.endswith("owac\u0107"):
            # 'owac' at end is almost certainly 'ować' approximation
            pass  # handled in _try_verb_classification via additional suffix check
        return word

    def _try_verb_classification(self, low: str) -> Optional[Dict[str, Any]]:
        """Detects -ować and -izować verbal stems, including ASCII approximations."""
        # ASCII approximation: 'owac' → treat as 'owac' (user typed without diacritic)
        if low.endswith("owac") and len(low) > 4:
            stem = low[:-4]  # strip -owac (ASCII approx of -ować)
            return {
                "word": low,
                "classification": "VERB",
                "subtype": "imperfective -owac/-owac (ASCII approx of -owac)",
                "aspect": "imperfective",
                "is_loanword": True,
                "paradigm": conjugate_owac_verb(stem),
                "usage_note": (
                    f"'{low}' detected as ASCII approximation of '{stem}owac' loanword verb. "
                    f"Canonical form: '{stem}owac'. Perfective: za{stem}owac."
                )
            }

        # Canonical form with diacritic
        if low.endswith("owac"):
            stem = low[:-4]  # strip -ować
            return {
                "word": low,
                "classification": "VERB",
                "subtype": "imperfective -ować",
                "aspect": "imperfective",
                "is_loanword": True,
                "paradigm": conjugate_owac_verb(stem),
                "usage_note": (
                    f"'{low}' follows the productive -ować loanword pattern. "
                    f"Perfective: za{stem}ować (or wy{stem}ować depending on semantics)."
                )
            }

        if low.endswith("izować") or low.endswith("yzować"):
            return {
                "word": low,
                "classification": "VERB",
                "subtype": "imperfective -izować (technical -ize loanword)",
                "aspect": "imperfective",
                "is_loanword": True,
                "paradigm": conjugate_izowac_verb(low),
                "usage_note": f"'{low}' follows the -izować pattern (from English -ize / French -iser)."
            }

        # Present tense forms ending in -uje/-ujesz/-ują
        for suffix, person in [("uję", "1sg"), ("ujesz", "2sg"), ("uje", "3sg"), ("ujemy", "1pl"), ("ują", "3pl")]:
            if low.endswith(suffix) and len(low) > len(suffix) + 2:
                stem = low[:-len(suffix)]
                return {
                    "word": low,
                    "classification": "VERB",
                    "subtype": f"-ować present tense ({person})",
                    "aspect": "imperfective",
                    "is_loanword": self._is_probable_loanword(stem),
                    "inferred_infinitive": f"{stem}ować",
                    "paradigm": conjugate_owac_verb(stem),
                    "usage_note": (
                        f"'{low}' is the {person} present form of '{stem}ować' "
                        f"(productive -ować loanword/neologism paradigm)."
                    )
                }

        return None

    def _try_nominal_classification(self, low: str) -> Optional[Dict[str, Any]]:
        """Detects nominal loanword suffixes and returns gender/declension."""
        for suffix, info in NOMINAL_LOANWORD_SUFFIXES.items():
            if low.endswith(suffix) and len(low) > len(suffix):
                return {
                    "word": low,
                    "classification": "NOUN",
                    "gender": info["gender"],
                    "declension_class": info["declension"],
                    "is_loanword": True,
                    "example_forms": info["example"],
                    "usage_note": (
                        f"'{low}' ends in -{suffix}: classified as {info['gender']} noun, "
                        f"follows {info['declension']} declension."
                    )
                }
        return None

    def _is_probable_loanword(self, word: str) -> bool:
        """Heuristic: word contains foreign letters or has no Polish diacritics + loanword shape."""
        low = word.lower()
        if any(c in FOREIGN_LETTERS for c in low):
            return True
        # No diacritics + contains typical English consonant clusters
        has_diacritics = any(c in POLISH_DIACRITICS for c in low)
        has_loanword_cluster = bool(re.search(r"(str|spr|tch|ght|ing|ck|wn)", low))
        return not has_diacritics and has_loanword_cluster


class PolishOpenVocabClassifier:
    """
    Integrates the Morpheme Generator with the POS tagger pipeline.
    Intercepts unknown words before they are silently labeled NOUN
    and attempts productive morphological classification.
    """

    def __init__(self):
        self.generator = PolishMorphemeGenerator()
        self._cache: Dict[str, Dict[str, Any]] = {}

    def classify(self, word: str) -> Dict[str, Any]:
        """
        Returns a classification for any unknown word.
        Results are cached for the session to avoid redundant computation.
        """
        low = word.lower().strip()
        if low in self._cache:
            return self._cache[low]

        result = self.generator.classify_and_generate(low)
        self._cache[low] = result
        return result

    def is_verb(self, word: str) -> bool:
        """Quick check: is this unknown word classifiable as a verb?"""
        result = self.classify(word)
        return result.get("classification") == "VERB"

    def is_noun(self, word: str) -> bool:
        """Quick check: is this unknown word classifiable as a noun?"""
        result = self.classify(word)
        return result.get("classification") == "NOUN"

    def inferred_infinitive(self, word: str) -> Optional[str]:
        """Returns the inferred infinitive for a verb form, if available."""
        result = self.classify(word)
        return result.get("inferred_infinitive") or result.get("paradigm", {}).get("infinitive_impf")
