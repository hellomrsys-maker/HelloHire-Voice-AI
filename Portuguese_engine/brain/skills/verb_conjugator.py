"""
Portuguese Verb Conjugator: Inflects verbs across Indicative, Subjunctive,
Conditional, and Personal Infinitive moods, with full lemmatization support.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class PortugueseVerbConjugator:
    """
    Inflects Portuguese regular and irregular verbs.
    Supports Personal Infinitive (Infinitivo Pessoal) and Future Subjunctive.
    """

    PERSONAL_INF_ENDINGS = {
        "eu": "", "tu": "es", "ele": "", "ela": "", "você": "",
        "nos": "mos", "nós": "mos", "vos": "des", "vós": "des",
        "eles": "em", "elas": "em", "vocês": "em"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "verb_conjugation_db.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

        self.verbs = self.db.get("conjugations", {})
        self._build_reverse_index()

    def _build_reverse_index(self):
        """Builds reverse mapping from inflected form to (lemma, mood, tense, person)."""
        self.reverse_map: Dict[str, Tuple[str, str, str, str]] = {}
        for lemma, data in self.verbs.items():
            for mood in ("indicativo", "subjuntivo"):
                for tense, persons in data.get(mood, {}).items():
                    for person, form in persons.items():
                        if form not in self.reverse_map:
                            self.reverse_map[form] = (lemma, mood, tense, person)
            for person, form in data.get("infinitivo_pessoal", {}).items():
                if form not in self.reverse_map:
                    self.reverse_map[form] = (lemma, "infinitivo_pessoal", "presente", person)

    def conjugate(
        self,
        lemma: str,
        mood: str = "indicativo",
        tense: str = "presente",
        person: str = "ele"
    ) -> str:
        """
        Conjugates a verb into target mood, tense, and person.
        Persons: 'eu', 'tu', 'ele', 'nos', 'vos', 'eles' (or 'você', 'nós', 'vocês').
        """
        norm_p = person.lower()
        if norm_p in ("você", "ela"):
            norm_p = "ele"
        elif norm_p == "nós":
            norm_p = "nos"
        elif norm_p in ("vocês", "elas"):
            norm_p = "eles"

        if lemma in self.verbs:
            v_data = self.verbs[lemma]
            if mood in v_data and tense in v_data[mood]:
                return v_data[mood][tense].get(norm_p, lemma)
            if mood == "infinitivo_pessoal":
                return v_data.get("infinitivo_pessoal", {}).get(norm_p, lemma)

        # Fallback regular personal infinitive if requested
        if mood == "infinitivo_pessoal":
            ending = self.PERSONAL_INF_ENDINGS.get(norm_p, "")
            return f"{lemma}{ending}"

        return lemma

    def conjugate_personal_infinitive(self, lemma: str, person: str = "ele") -> str:
        """Convenience method for the inflected personal infinitive."""
        return self.conjugate(lemma, mood="infinitivo_pessoal", person=person)

    def get_gerund(self, lemma: str) -> str:
        """Returns the gerund form (e.g. falando, comendo, partindo)."""
        if lemma in self.verbs and "gerundio" in self.verbs[lemma]:
            return self.verbs[lemma]["gerundio"]
        if lemma.endswith("ar"):
            return lemma[:-2] + "ando"
        elif lemma.endswith("er"):
            return lemma[:-2] + "endo"
        elif lemma.endswith("ir"):
            return lemma[:-2] + "indo"
        return lemma

    def get_participle(self, lemma: str) -> str:
        """Returns the past participle form (e.g. falado, comido, feito)."""
        if lemma in self.verbs and "participio" in self.verbs[lemma]:
            return self.verbs[lemma]["participio"]
        if lemma.endswith("ar"):
            return lemma[:-2] + "ado"
        elif lemma.endswith(("er", "ir")):
            return lemma[:-2] + "ido"
        return lemma

    def lemmatize(self, form: str) -> Optional[Tuple[str, str, str, str]]:
        """Lemmatizes an inflected verbal form."""
        return self.reverse_map.get(form.lower())
