"""Russian Verb Aspect & Conjugation Skill.

Analyzes Russian verb aspect (НСВ/СВ), Aktionsarten derivations,
suppletion, and inflects past and non-past forms.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple


class RussianVerbAspectConjugator:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "verb_aspect_db.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.aspect_pairs = self.db.get("aspect_pairs", {})
        self.aktionsart_prefixes = self.db.get("aktionsart_prefixes", {})

    def get_aspect(self, verb: str) -> Dict[str, Any]:
        """Determines if a verb is imperfective (НСВ) or perfective (СВ)."""
        v_low = verb.lower()

        # Check DB
        if v_low in self.aspect_pairs:
            entry = self.aspect_pairs[v_low]
            return {
                "verb": verb,
                "aspect": entry["aspect"],
                "partner": entry["partner"],
                "derivation_type": entry.get("type", "known")
            }

        # Suffix heuristics
        if any(v_low.endswith(sfx) for sfx in ("ывать", "ивать", "ываться", "иваться", "ывал", "ивал")):
            return {
                "verb": verb,
                "aspect": "impf",
                "partner": None,
                "derivation_type": "suffixal_impf"
            }

        if any(v_low.endswith(sfx) for sfx in ("нуть", "нуться", "нул", "нула", "нули")):
            return {
                "verb": verb,
                "aspect": "perf",
                "partner": None,
                "derivation_type": "semelfactive_perf"
            }

        # Prefix heuristics: common perfectivizing prefixes
        common_perf_prefixes = ("с", "по", "на", "про", "за", "вы", "пере", "от", "до", "у", "вз", "вс", "при", "под")
        for pref in common_perf_prefixes:
            if v_low.startswith(pref) and len(v_low) >= len(pref) + 3:
                return {
                    "verb": verb,
                    "aspect": "perf",
                    "partner": None,
                    "derivation_type": "prefixal_perf"
                }

        # Check if past tense form with known root
        if v_low.endswith(("л", "ла", "ло", "ли")):
            stem = v_low[:-1] if v_low.endswith("л") else v_low[:-2]
            for inf_cand in (stem + "ть", stem + "ать", stem + "ить", stem + "еть"):
                if inf_cand in self.aspect_pairs:
                    entry = self.aspect_pairs[inf_cand]
                    return {
                        "verb": verb,
                        "aspect": entry["aspect"],
                        "partner": entry["partner"],
                        "derivation_type": entry.get("type", "known")
                    }

        # Default standard infinitive is imperfective
        return {
            "verb": verb,
            "aspect": "impf",
            "partner": None,
            "derivation_type": "default"
        }


    def conjugate_past(self, stem_or_inf: str, gender: str = "masc", number: str = "sing") -> str:
        """Conjugates past tense for Russian verbs based on gender and number."""
        stem = stem_or_inf
        if stem.endswith(("ть", "ти")):
            stem = stem[:-2]
        elif stem.endswith("чь"):
            stem = stem[:-2] + "г"  # approximate stem alternation (мочь -> мог)

        if number == "plur":
            return stem + "ли"
        if gender == "fem":
            return stem + "ла"
        if gender == "neut":
            return stem + "ло"
        return stem + "л"

    def conjugate_present_1st_sing(self, stem_or_inf: str, conj_class: int = 1) -> str:
        """Generates 1st person singular (я) present/simple future."""
        stem = stem_or_inf
        if stem.endswith("ать"):
            return stem[:-3] + "аю"
        if stem.endswith("ить"):
            return stem[:-3] + "ю"
        if stem.endswith("еть"):
            return stem[:-3] + "ею"
        if stem.endswith("ть"):
            return stem[:-2] + "ю"
        return stem + "ю"
