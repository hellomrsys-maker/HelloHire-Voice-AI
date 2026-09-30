"""
Spanish Verb Conjugation and Lemmatization Skill.
Provides 14-tense paradigms for regular verbs (-ar, -er, -ir) and top irregular verbs.
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "verb_conjugation_db.json")


class SpanishVerbConjugator:
    """
    Finite State inflector and morphological lemmatizer for Spanish verbs.
    """

    def __init__(self, db_path: Optional[str] = None):
        target = db_path or DB_PATH
        self.regular_endings: Dict[str, Any] = {}
        self.irregular_verbs: Dict[str, Any] = {}

        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.regular_endings = data.get("regular_endings", {})
                self.irregular_verbs = data.get("irregular_verbs", {})

    def conjugate(self, lemma: str, tense: str = "presente_indicativo") -> List[str]:
        """
        Conjugates a lemma across 6 grammatical persons [yo, tú, él, nosotros, vosotros, ellos].
        """
        lem = lemma.lower().strip()

        # Check irregular verb database
        if lem in self.irregular_verbs and tense in self.irregular_verbs[lem]:
            return self.irregular_verbs[lem][tense]

        # Regular conjugation
        conj_class = lem[-2:]
        if conj_class in self.regular_endings:
            stem = lem[:-2]
            tense_data = self.regular_endings[conj_class].get(tense)
            if tense_data:
                return [stem + ending for ending in tense_data]

        return []

    def get_conjugation_for_person(
        self,
        lemma: str,
        person_idx: int, # 0 = yo, 1 = tú, 2 = él/ella/usted, 3 = nosotros, 4 = vosotros, 5 = ellos/ustedes
        tense: str = "presente_indicativo"
    ) -> Optional[str]:
        forms = self.conjugate(lemma, tense)
        if forms and 0 <= person_idx < len(forms):
            return forms[person_idx]
        return None

    def lemmatize(self, surface_form: str) -> Dict[str, Any]:
        """
        Attempts to reverse-map an inflected surface verb to its infinitive lemma and tense features.
        """
        surf = surface_form.lower().strip()

        # Check irregulars
        for lemma, tenses in self.irregular_verbs.items():
            for t_name, forms in tenses.items():
                if isinstance(forms, list) and surf in forms:
                    p_idx = forms.index(surf)
                    return {
                        "surface": surface_form,
                        "lemma": lemma,
                        "tense": t_name,
                        "person_index": p_idx,
                        "is_irregular": True,
                    }

        # Regular stem stripping heuristic
        if surf.endswith(("ando", "ado")):
            return {"surface": surface_form, "lemma": surf[:-4] + "ar", "tense": "participio/gerundio", "is_irregular": False}
        if surf.endswith(("iendo", "ido")):
            return {"surface": surface_form, "lemma": surf[:-5] + "er", "tense": "participio/gerundio", "is_irregular": False}

        return {
            "surface": surface_form,
            "lemma": surf,
            "tense": "unknown",
            "is_irregular": False,
        }
