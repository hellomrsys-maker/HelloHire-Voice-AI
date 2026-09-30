"""
Bengali Compound Verb Engine (যৌগিক ক্রিয়া - Yougik Kriya):
Decomposes, analyzes, and synthesizes complex predicate serial constructions
consisting of a non-finite conjunctive participle (V1-e) + an aspectual vector auxiliary (V2).
"""

from typing import Dict, Any, Optional, Tuple, List
from .verb_conjugator import BengaliVerbConjugator


class BengaliCompoundVerbEngine:
    """
    Analyzes and constructs Bengali compound verbs with vector semantics.
    """

    VECTOR_VERBS = {
        "ফেলা": {
            "meaning": "completion, irrevocability, finality",
            "semantic_nuance": "telic_irrevocable",
            "example": "করে ফেলা (finish completely)"
        },
        "রাখা": {
            "meaning": "preparatory action, retention, preservation",
            "semantic_nuance": "preparatory_retentive",
            "example": "লিখে রাখা (note down for future)"
        },
        "দেওয়া": {
            "meaning": "benefactive action for another person",
            "semantic_nuance": "other_benefactive",
            "example": "বলে দেওয়া (tell on someone's behalf)"
        },
        "নেওয়া": {
            "meaning": "benefactive action for oneself / inward",
            "semantic_nuance": "self_benefactive",
            "example": "পড়ে নেওয়া (read through for oneself)"
        },
        "ওঠা": {
            "meaning": "sudden inception, emergence, surprise",
            "semantic_nuance": "inchoative_sudden",
            "example": "হেসে ওঠা (burst into laughter)"
        },
        "বসা": {
            "meaning": "rash, inadvertent, or foolish action",
            "semantic_nuance": "inadvertent_rash",
            "example": "করে বসা (do recklessly)"
        },
        "যাওয়া": {
            "meaning": "telic completion, transition of state",
            "semantic_nuance": "telic_transition",
            "example": "শুকিয়ে যাওয়া (dry up completely)"
        },
        "আসা": {
            "meaning": "progression toward the present or speaker",
            "semantic_nuance": "durative_directional",
            "example": "চলে আসা (arrive / come away)"
        }
    }

    def __init__(self, conjugator: Optional[BengaliVerbConjugator] = None):
        self.conjugator = conjugator or BengaliVerbConjugator()

    def is_vector_verb(self, lemma_or_form: str) -> bool:
        """Checks if a verb lemma is one of the 8 canonical Bengali vector verbs."""
        if lemma_or_form in self.VECTOR_VERBS:
            return True
        # Check lemmatization
        info = self.conjugator.lemmatize(lemma_or_form)
        if info and info[0] in self.VECTOR_VERBS:
            return True
        return False

    def analyze_compound(self, v1_conjunctive: str, v2_form: str) -> Dict[str, Any]:
        """
        Analyzes a pair of verbs to evaluate if they form a valid compound predicate.
        """
        # V1 must be in conjunctive participle form (typically ends in 'ে')
        is_v1_conj = v1_conjunctive.endswith("ে") or v1_conjunctive.endswith("িয়ে")
        
        # Lemmatize V2
        v2_lemma = v2_form
        v2_tense = "unknown"
        v2_tier = "unknown"
        lem_info = self.conjugator.lemmatize(v2_form)
        if lem_info:
            v2_lemma, v2_tense, v2_tier = lem_info
        
        is_vector = v2_lemma in self.VECTOR_VERBS
        
        if is_v1_conj and is_vector:
            vector_data = self.VECTOR_VERBS[v2_lemma]
            return {
                "is_compound": True,
                "v1_participle": v1_conjunctive,
                "v2_vector_lemma": v2_lemma,
                "v2_inflected": v2_form,
                "tense": v2_tense,
                "person_tier": v2_tier,
                "semantic_nuance": vector_data["semantic_nuance"],
                "aspectual_meaning": vector_data["meaning"]
            }
        
        return {
            "is_compound": False,
            "v1_participle": v1_conjunctive,
            "v2_form": v2_form
        }

    def compose_compound(self, main_lemma: str, vector_lemma: str, tense: str = "present_simple", tier: str = "3rd_ord") -> str:
        """
        Composes a compound verb from main lemma and vector auxiliary lemma.
        Example: 'করা' + 'ফেলা' -> 'করে ফেলে' (he finishes doing).
        """
        v1_participle = self.conjugator.get_non_finite(main_lemma, "conjunctive")
        v2_inflected = self.conjugator.conjugate(vector_lemma, tense, tier)
        return f"{v1_participle} {v2_inflected}"
