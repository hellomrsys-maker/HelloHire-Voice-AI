"""Russian Case Engine Skill.

Governs Russian's 6 grammatical cases (Nom, Gen, Dat, Acc, Inst, Prep),
handles prepositional/verbal government valency, animacy splits in the accusative,
and nominal declension morphology across 3 declension classes.
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple


class RussianCaseEngine:
    CASES = ["nom", "gen", "dat", "acc", "inst", "prep"]

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "case_declension_matrix.json")

        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.prep_gov = self.db.get("preposition_government", {})
        self.dual_prep = self.db.get("dual_case_prepositions", {})
        self.verb_gov = self.db.get("verb_government", {})

    def get_expected_case_for_prep(self, prep: str, motion: bool = False) -> Optional[str]:
        """Returns the expected case for a Russian preposition."""
        p_low = prep.lower()
        if p_low in self.dual_prep:
            return self.dual_prep[p_low]["motion"] if motion else self.dual_prep[p_low]["static"]
        return self.prep_gov.get(p_low)

    def get_expected_case_for_verb(self, verb: str) -> Optional[str]:
        """Returns the expected case government for a specific Russian verb."""
        v_low = verb.lower()
        return self.verb_gov.get(v_low)

    def inflect_noun(
        self,
        lemma: str,
        case: str,
        gender: str = "masc",
        declension: str = "2nd",
        number: str = "sing",
        animacy: bool = False
    ) -> str:
        """Inflects a Russian noun lemma into a target case given gender, declension, number, and animacy."""
        c = case.lower()
        if c == "nom" and number == "sing":
            return lemma

        # 1st Declension (книга, мама, земля)
        if declension == "1st":
            stem = lemma[:-1] if lemma.endswith(("а", "я")) else lemma
            is_soft = lemma.endswith("я")
            if number == "sing":
                if c == "nom":
                    return stem + ("я" if is_soft else "а")
                elif c == "gen":
                    return stem + ("и" if is_soft or stem[-1] in "гкхжчшщ" else "ы")
                elif c == "dat" or c == "prep":
                    return stem + "е"
                elif c == "acc":
                    return stem + ("ю" if is_soft else "у")
                elif c == "inst":
                    return stem + ("ей" if is_soft else "ой")
            else: # Plural
                if c == "nom":
                    return stem + ("и" if is_soft or stem[-1] in "гкхжчшщ" else "ы")
                elif c == "gen":
                    return stem + ("ь" if is_soft else "")
                elif c == "dat":
                    return stem + ("ям" if is_soft else "ам")
                elif c == "acc":
                    return self.inflect_noun(lemma, "gen" if animacy else "nom", gender, declension, "plur", animacy)
                elif c == "inst":
                    return stem + ("ями" if is_soft else "ами")
                elif c == "prep":
                    return stem + ("ях" if is_soft else "ах")

        # 2nd Declension (стол, студент, окно)
        elif declension == "2nd":
            if gender == "neut":
                stem = lemma[:-1] if lemma.endswith(("о", "е", "ё")) else lemma
                is_soft = lemma.endswith(("е", "ё"))
                if number == "sing":
                    if c in ("nom", "acc"):
                        return stem + ("е" if is_soft else "о")
                    elif c == "gen":
                        return stem + ("я" if is_soft else "а")
                    elif c == "dat":
                        return stem + ("ю" if is_soft else "у")
                    elif c == "inst":
                        return stem + ("ем" if is_soft else "ом")
                    elif c == "prep":
                        return stem + "е"
            else: # Masculine
                stem = lemma[:-1] if lemma.endswith(("ь", "й")) else lemma
                is_soft = lemma.endswith(("ь", "й"))
                if number == "sing":
                    if c == "nom":
                        return lemma
                    elif c == "gen":
                        return stem + ("я" if is_soft else "а")
                    elif c == "dat":
                        return stem + ("ю" if is_soft else "у")
                    elif c == "acc":
                        return self.inflect_noun(lemma, "gen" if animacy else "nom", gender, declension, "sing", animacy)
                    elif c == "inst":
                        return stem + ("ем" if is_soft else "ом")
                    elif c == "prep":
                        return stem + "е"

        # 3rd Declension (ночь, дверь, тетрадь)
        elif declension == "3rd":
            stem = lemma[:-1] if lemma.endswith("ь") else lemma
            if number == "sing":
                if c in ("nom", "acc"):
                    return stem + "ь"
                elif c in ("gen", "dat", "prep"):
                    return stem + "и"
                elif c == "inst":
                    return stem + "ью"

        return lemma

    def check_accusative_animacy(self, noun: str, is_animate: bool, gender: str, number: str) -> Dict[str, Any]:
        """Validates animacy rule: masculine singular animates and all plural animates take genitive in accusative."""
        requires_genitive_form = (is_animate and gender == "masc" and number == "sing") or (is_animate and number == "plur")
        return {
            "noun": noun,
            "is_animate": is_animate,
            "gender": gender,
            "number": number,
            "accusative_takes_genitive_form": requires_genitive_form
        }
