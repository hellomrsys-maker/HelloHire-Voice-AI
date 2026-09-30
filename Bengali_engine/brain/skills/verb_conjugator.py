"""
Bengali Verb Conjugator: Handles multi-class verb conjugation across all tenses,
aspects, and honorific tiers, as well as non-finite participles and lemmatization.
"""

from typing import Dict, Any, Optional, Tuple
import os
import json


class BengaliVerbConjugator:
    """
    Inflects Bengali verbs according to tense, aspect, person, and politeness hierarchy.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "verb_conjugation_db.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        
        self.verbs = self.db.get("verbs", {})
        self._build_reverse_index()

    def _build_reverse_index(self):
        """Builds reverse map from inflected form to (lemma, tense, tier)."""
        self.reverse_map: Dict[str, Tuple[str, str, str]] = {}
        for lemma, data in self.verbs.items():
            for tense, tiers in data.get("conjugations", {}).items():
                for tier, form in tiers.items():
                    if form not in self.reverse_map:
                        self.reverse_map[form] = (lemma, tense, tier)
            for non_fin_type, form in data.get("non_finite", {}).items():
                if form not in self.reverse_map:
                    self.reverse_map[form] = (lemma, "non_finite", non_fin_type)

    def conjugate(self, lemma: str, tense: str = "present_simple", tier: str = "3rd_ord") -> str:
        """
        Conjugates a verb lemma into a specified tense and person/honorific tier.
        Tiers: '1st', '2nd_fam', '2nd_int', 'hon', '3rd_ord'.
        """
        if lemma not in self.verbs:
            return lemma
        
        conj_data = self.verbs[lemma].get("conjugations", {})
        if tense in conj_data and tier in conj_data[tense]:
            return conj_data[tense][tier]
        
        # Fallback to present simple 3rd_ord
        return conj_data.get("present_simple", {}).get("3rd_ord", lemma)

    def get_non_finite(self, lemma: str, form_type: str = "conjunctive") -> str:
        """
        Returns non-finite participles: 'conjunctive' (-e), 'infinitive' (-te), 'conditional' (-le).
        """
        if lemma not in self.verbs:
            return lemma
        non_fin = self.verbs[lemma].get("non_finite", {})
        return non_fin.get(form_type, lemma)

    def lemmatize(self, form: str) -> Optional[Tuple[str, str, str]]:
        """
        Lemmatizes an inflected verbal form.
        Returns: (lemma, tense, tier) or None.
        """
        return self.reverse_map.get(form)

    def get_transitivity(self, lemma: str) -> str:
        """
        Returns 'transitive' or 'intransitive'.
        """
        if lemma in self.verbs:
            return self.verbs[lemma].get("transitivity", "intransitive")
        return "intransitive"
