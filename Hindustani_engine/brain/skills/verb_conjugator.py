"""
Hindustani Verb Conjugation Skill.
Provides morphological conjugation across habitual, continuous, perfective, and future TAM categories,
transitivity checking for split-ergativity, and lemmatization.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class HindustaniVerbConjugator:
    """
    Morphological conjugator and aspect engine for Hindustani verbs.
    """

    TRANSITIVE_VERBS = {
        "karna", "dekhna", "likhna", "padhna", "khana", "peena",
        "kehna", "sunna", "dena", "lena", "banana", "khareedna",
        "bechna", "dhundhna", "bhejna", "samajhna",
        "करना", "देखना", "लिखना", "पढ़ना", "खाना", "पीना",
        "कहना", "सुनना", "देना", "लेना", "बनाना", "खरीदना"
    }

    IRREGULAR_PERFECTIVE = {
        "karna": {"M_SG": "kiya", "M_PL": "kiye", "F_SG": "ki", "F_PL": "kin"},
        "करना":  {"M_SG": "किया", "M_PL": "किए",  "F_SG": "की", "F_PL": "कीं"},
        "jaana": {"M_SG": "gaya", "M_PL": "gaye", "F_SG": "gayi", "F_PL": "gayin"},
        "जाना":  {"M_SG": "गया",  "M_PL": "गए",   "F_SG": "गई",  "F_PL": "गईं"},
        "dena":  {"M_SG": "diya", "M_PL": "diye", "F_SG": "di", "F_PL": "din"},
        "देना":  {"M_SG": "दिया", "M_PL": "दिए",  "F_SG": "दी", "F_PL": "दीं"},
        "lena":  {"M_SG": "liya", "M_PL": "liye", "F_SG": "li", "F_PL": "lin"},
        "लेना":  {"M_SG": "लिया", "M_PL": "लिए",  "F_SG": "ली", "F_PL": "लीं"},
        "hona":  {"M_SG": "hua",  "M_PL": "hue",  "F_SG": "hui", "F_PL": "huin"},
        "होना":  {"M_SG": "हुआ",  "M_PL": "हुए",  "F_SG": "हुई", "F_PL": "हुईं"}
    }

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent.parent / "rules" / "verb_conjugation_db.json")
        self.rules_path = rules_path
        self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except Exception:
            self.db = {
                "transitivity_classes": {"transitive_verbs": list(self.TRANSITIVE_VERBS)},
                "irregular_perfective": self.IRREGULAR_PERFECTIVE
            }

    def is_transitive(self, lemma: str) -> bool:
        """Determines if the verb is transitive (triggers ergative ne in perfective)."""
        clean = lemma.lower().strip()
        return clean in self.TRANSITIVE_VERBS or lemma in self.TRANSITIVE_VERBS

    def get_stem(self, lemma: str) -> str:
        """Strips infinitive marker -na or -ना."""
        if lemma.endswith("ना"):
            return lemma[:-1]
        elif lemma.lower().endswith("na"):
            return lemma[:-2]
        return lemma

    def conjugate(
        self,
        lemma: str,
        aspect: str = "habitual",  # "habitual", "continuous", "perfective", "future"
        gender: str = "M",         # "M" or "F"
        number: str = "SG",        # "SG" or "PL"
        honorific: bool = False
    ) -> str:
        """
        Synthesizes conjugated verbal form according to aspect, gender, number, and honorific status.
        """
        stem = self.get_stem(lemma)
        feat_key = f"{gender}_{number}" if not honorific else f"{gender}_PL"

        if aspect == "perfective":
            # Check irregular perfective
            low = lemma.lower()
            if low in self.IRREGULAR_PERFECTIVE and feat_key in self.IRREGULAR_PERFECTIVE[low]:
                return self.IRREGULAR_PERFECTIVE[low][feat_key]
            if lemma in self.IRREGULAR_PERFECTIVE and feat_key in self.IRREGULAR_PERFECTIVE[lemma]:
                return self.IRREGULAR_PERFECTIVE[lemma][feat_key]

            # Regular perfective
            if lemma.endswith("ना"):
                suff_map = {"M_SG": "ा", "M_PL": "े", "F_SG": "ी", "F_PL": "ीं"}
                return stem + suff_map.get(feat_key, "ा")
            else:
                suff_map = {"M_SG": "a", "M_PL": "e", "F_SG": "i", "F_PL": "in"}
                # If stem ends in vowel, add y (e.g. khaa -> khaya)
                connector = "y" if stem.endswith(("a", "o", "u", "e")) else ""
                return stem + connector + suff_map.get(feat_key, "a")

        elif aspect == "habitual":
            if lemma.endswith("ना"):
                suff_map = {"M_SG": "ता", "M_PL": "ते", "F_SG": "ती", "F_PL": "तीं"}
                return stem + suff_map.get(feat_key, "ता")
            else:
                suff_map = {"M_SG": "ta", "M_PL": "te", "F_SG": "ti", "F_PL": "tin"}
                return stem + suff_map.get(feat_key, "ta")

        elif aspect == "continuous":
            if lemma.endswith("ना"):
                suff_map = {"M_SG": "रहा", "M_PL": "रहे", "F_SG": "रही", "F_PL": "रहीं"}
                return f"{stem} {suff_map.get(feat_key, 'रहा')}"
            else:
                suff_map = {"M_SG": "raha", "M_PL": "rahe", "F_SG": "rahi", "F_PL": "rahin"}
                return f"{stem} {suff_map.get(feat_key, 'raha')}"

        elif aspect == "future":
            if lemma.endswith("ना"):
                return stem + ("ेगा" if gender == "M" else "ेगी")
            else:
                if honorific or number == "PL":
                    return stem + ("enge" if gender == "M" else "engi")
                return stem + ("ega" if gender == "M" else "egi")

        return lemma

    def lemmatize(self, conjugated_form: str) -> Dict[str, Any]:
        """Recovers underlying lemma and transitivity."""
        form_low = conjugated_form.lower().strip()
        for lemma in self.TRANSITIVE_VERBS:
            stem = self.get_stem(lemma).lower()
            if form_low.startswith(stem) or form_low == stem:
                return {"lemma": lemma, "is_transitive": True}

        return {"lemma": form_low + "na", "is_transitive": False}
