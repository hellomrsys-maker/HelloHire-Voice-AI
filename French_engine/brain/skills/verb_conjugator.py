"""
French Verb Conjugation Skill.
Provides morphological conjugation across Groups 1, 2, and 3 (irregulars),
compound tense auxiliary classification (être vs. avoir), and lemmatization.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class FrenchVerbConjugator:
    """
    Morphological conjugator and lemmatizer for French verbs.
    """

    ETRE_VERBS = {
        "aller", "arriver", "descendre", "devenir", "entrer", "monter",
        "mourir", "naître", "partir", "rentrer", "rester", "retourner",
        "revenir", "sortir", "tomber", "venir"
    }

    PERSON_PRONOUNS = ["je", "tu", "il", "nous", "vous", "ils"]

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
                "regular_groups": {},
                "auxiliary_classification": {"etre_verbs": list(self.ETRE_VERBS)},
                "irregular_verbs": {}
            }

    def get_auxiliary(self, lemma: str) -> str:
        """Determines whether the verb takes 'être' or 'avoir' in compound tenses."""
        low = lemma.lower()
        if low.startswith("se ") or low.startswith("s'"):
            return "être"
        if low in self.ETRE_VERBS:
            return "être"
        return "avoir"

    def conjugate(self, lemma: str, tense: str = "present") -> List[str]:
        """
        Conjugates a verb across all 6 grammatical persons for the given tense.
        Tenses: present, imparfait, futur, conditionnel, subjonctif_present.
        """
        lemma_low = lemma.lower()
        irregular_verbs = self.db.get("irregular_verbs", {})

        # Irregular verb lookup
        if lemma_low in irregular_verbs:
            irr = irregular_verbs[lemma_low]
            if tense in irr:
                return irr[tense]

        # Regular Group 1 (-er)
        if lemma_low.endswith("er") and lemma_low != "aller":
            stem = lemma_low[:-2]
            group1 = self.db.get("regular_groups", {}).get("group1_er", {})
            endings = group1.get(tense)
            if endings:
                return [stem + end for end in endings]
            if tense == "present":
                return [stem + e for e in ["e", "es", "e", "ons", "ez", "ent"]]

        # Regular Group 2 (-ir with -issant)
        if lemma_low.endswith("ir") and lemma_low not in irregular_verbs:
            stem = lemma_low[:-2]
            group2 = self.db.get("regular_groups", {}).get("group2_ir", {})
            endings = group2.get(tense)
            if endings:
                return [stem + end for end in endings]
            if tense == "present":
                return [stem + e for e in ["is", "is", "it", "issons", "issez", "issent"]]

        # Fallback default
        return [lemma_low] * 6

    def conjugate_passe_compose(self, lemma: str, subject_gender: str = "M", subject_number: str = "SG") -> List[str]:
        """
        Generates Passé Composé conjugations with correct auxiliary and participle agreement.
        """
        aux_verb = self.get_auxiliary(lemma)
        participle = self.get_past_participle(lemma)

        # Apply agreement if auxiliary is être
        if aux_verb == "être":
            agreement_suffix = ""
            if subject_gender == "F":
                agreement_suffix += "e"
            if subject_number == "PL":
                agreement_suffix += "s"
            participle = participle + agreement_suffix

        aux_forms = self.conjugate(aux_verb, "present")
        return [f"{aux} {participle}" for aux in aux_forms]

    def get_past_participle(self, lemma: str) -> str:
        """Returns the base past participle of the verb."""
        lemma_low = lemma.lower()
        irregular_verbs = self.db.get("irregular_verbs", {})

        if lemma_low in irregular_verbs and "participe_passe" in irregular_verbs[lemma_low]:
            return irregular_verbs[lemma_low]["participe_passe"]

        if lemma_low.endswith("er"):
            return lemma_low[:-2] + "é"
        elif lemma_low.endswith("ir"):
            return lemma_low[:-2] + "i"
        elif lemma_low.endswith("re"):
            return lemma_low[:-2] + "u"
        return lemma_low

    def get_conjugation_for_person(self, lemma: str, person_idx: int, tense: str = "present") -> str:
        """Returns specific conjugated form for person 0..5."""
        forms = self.conjugate(lemma, tense)
        if 0 <= person_idx < len(forms):
            return forms[person_idx]
        return lemma

    def lemmatize(self, conjugated_form: str) -> Dict[str, Any]:
        """Identifies possible lemma and morphological features."""
        form_low = conjugated_form.lower()
        irregular_verbs = self.db.get("irregular_verbs", {})

        for lemma, tenses in irregular_verbs.items():
            for t_name, forms in tenses.items():
                if isinstance(forms, list) and form_low in forms:
                    person = forms.index(form_low)
                    return {
                        "lemma": lemma,
                        "tense": t_name,
                        "person": person,
                        "is_irregular": True
                    }
                elif isinstance(forms, str) and form_low == forms:
                    return {
                        "lemma": lemma,
                        "tense": t_name,
                        "person": None,
                        "is_irregular": True
                    }

        # Regular -er check
        if form_low.endswith(("e", "es", "ons", "ez", "ent", "é")):
            return {"lemma": form_low + "...", "tense": "present/participle", "person": None, "is_irregular": False}

        return {"lemma": form_low, "tense": "unknown", "person": None, "is_irregular": False}
