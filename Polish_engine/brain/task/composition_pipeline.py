"""
Polish Composition Task Pipeline
Generates multi-clause Polish text, aspectual sentence sequences, and idiomatic expressions.
"""

from typing import Dict, Any, List
from ..skills.generation import PolishGenerator
from ..skills.aspect_engine import PolishAspectEngine

class PolishCompositionPipeline:
    def __init__(self):
        self.generator = PolishGenerator()
        self.aspect_engine = PolishAspectEngine()
        self.idioms = {
            "not_my_problem": "Nie mój cyrk, nie moje małpy.",
            "badgering": "Przestań wiercić mi dziurę w brzuchu!",
            "futile": "To jak rzucanie grochem o ścianę.",
            "stingy": "On ma węża w kieszeni.",
            "clueless": "Urwałeś się z choinki?",
            "crush": "Czuję do niej miętę."
        }

    def compose_aspectual_contrast(self, subject: str, verb_impf: str, noun_lemma: str) -> Dict[str, str]:
        """
        Creates a contrastive pair:
        1. Incomplete / Continuous action (Imperfective, present/past).
        2. Completed / Telic result (Perfective).
        """
        pair = self.aspect_engine.get_aspect_pair(verb_impf)
        if not pair:
            return {"error": f"No aspectual pair found for '{verb_impf}'"}

        impf = pair["imperfective"]
        pf = pair["perfective"]

        present_clause = self.generator.generate_clause(subject, "czytam" if impf == "czytać" else "piszę", noun_lemma, negate=False)
        future_pf_clause = self.generator.generate_clause(subject, "przeczytam" if pf == "przeczytać" else "napiszę", noun_lemma, negate=False)
        negated_clause = self.generator.generate_clause(subject, "czytam" if impf == "czytać" else "piszę", noun_lemma, negate=True)

        return {
            "imperfective_affirmative": present_clause,
            "perfective_telic": future_pf_clause,
            "genitive_of_negation": negated_clause
        }

    def get_idiomatic_expression(self, idiom_key: str) -> str:
        return self.idioms.get(idiom_key, "Wszystko gra i buczy.")
