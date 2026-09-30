"""
Hindustani Ergative Split Skill.
Evaluates perfective aspect split-ergativity, ne-postposition assignment on transitive subjects,
and object-concord vs. default neutral verb agreement.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .verb_conjugator import HindustaniVerbConjugator


class ErgativeSplitEngine:
    """
    Cognitive rule engine evaluating the Indo-Aryan split-ergative alignment system.
    """

    PRONOMINAL_ERGATIVE = {
        "maine", "tune", "usne", "isne", "humne", "tumne", "aapne", "unhonne", "inhonne",
        "मैंने", "तूने", "उसने", "इसने", "हमने", "तुमने", "आपने", "उन्होंने", "इन्होंने"
    }

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent.parent / "rules" / "ergative_split_rules.json")
        self.rules_path = rules_path
        self.conjugator = HindustaniVerbConjugator()
        self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except Exception:
            self.db = {
                "ergative_conditions": {"marker": "ne"},
                "pronominal_ergative_forms": {}
            }

    def has_ergative_subject(self, subject_tokens: List[str]) -> bool:
        """Checks if the subject phrase contains 'ne' or fused pronominal ergative form."""
        for t in subject_tokens:
            low = t.lower()
            if low in {"ne", "ने"} or low in self.PRONOMINAL_ERGATIVE or t in self.PRONOMINAL_ERGATIVE:
                return True
        return False

    def evaluate_clause(
        self,
        subject_phrase: List[str],
        verb_lemma: str,
        aspect: str,                  # "perfective", "habitual", "continuous", "future"
        object_phrase: Optional[List[str]] = None,
        object_gender: str = "M",      # "M" or "F"
        object_number: str = "SG",     # "SG" or "PL"
        verb_surface: str = ""
    ) -> Dict[str, Any]:
        """
        Validates split-ergative alignment for a clause.
        """
        is_trans = self.conjugator.is_transitive(verb_lemma)
        is_perf = aspect == "perfective"
        requires_ne = is_trans and is_perf

        has_ne = self.has_ergative_subject(subject_phrase)

        # 1. Subject Ergative Alignment Check
        subject_valid = True
        if requires_ne and not has_ne:
            subject_valid = False
            msg = f"Violation d'ergativité scindée: le verbe transitif '{verb_lemma}' au perfectif exige la postposition 'ne' sur le sujet."
        elif not requires_ne and has_ne:
            subject_valid = False
            msg = f"Postposition 'ne' illicite: le verbe '{verb_lemma}' est intransitif ou non-perfectif."
        else:
            msg = "Alignement sujet conforme."

        # 2. Verbal Agreement Check in Ergative
        concord_valid = True
        expected_verb_form = ""
        has_ko = False
        if object_phrase:
            has_ko = any(t.lower() in {"ko", "को"} for t in object_phrase)

        if requires_ne:
            if has_ko:
                # Neutral default M_SG
                expected_verb_form = self.conjugator.conjugate(verb_lemma, aspect="perfective", gender="M", number="SG")
            else:
                # Agrees with direct object
                expected_verb_form = self.conjugator.conjugate(verb_lemma, aspect="perfective", gender=object_gender, number=object_number)

            if verb_surface:
                concord_valid = verb_surface.lower() == expected_verb_form.lower()

        overall_valid = subject_valid and concord_valid

        return {
            "verb_lemma": verb_lemma,
            "is_transitive": is_trans,
            "aspect": aspect,
            "requires_ne": requires_ne,
            "has_ne": has_ne,
            "subject_ergative_valid": subject_valid,
            "object_has_ko": has_ko,
            "expected_verb_form": expected_verb_form,
            "actual_verb_surface": verb_surface,
            "verb_concord_valid": concord_valid,
            "is_grammatically_sound": overall_valid,
            "message": msg if not subject_valid else ("Accord verbal conforme à l'objet." if concord_valid else f"Discordance verbale: attendu '{expected_verb_form}', trouvé '{verb_surface}'.")
        }
