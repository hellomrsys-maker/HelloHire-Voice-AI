"""
Dutch Composition Task Pipeline
Assembles multi-clause Dutch prose, complex sentences, and idiomatic expressions.
"""

from typing import Dict, Any, List
from ..skills.generation import DutchGenerator

class DutchCompositionPipeline:
    def __init__(self):
        self.generator = DutchGenerator()
        self.idioms = {
            "disbelief": "Nu breekt mijn klomp!",
            "revelation": "Nu komt de aap uit de mouw.",
            "unfortunate": "Helaas pindakaas.",
            "small_talk": "Zullen we even over koetjes en kalfjes praten?",
            "consequences": "Nu zitten we met de gebakken peren."
        }

    def compose_complex_sentence(self, main_sub: str, main_verb: str, main_obj: str,
                                 sub_conj: str, sub_subj: str, sub_obj: str, sub_verb: str,
                                 front_subordinate: bool = False) -> str:
        """
        Builds a complex sentence combining a main clause and a subordinate clause.
        If front_subordinate=True: [Subordinate SOV clause], [Verb] [Subject] [Object] (V2 inversion triggered!).
        """
        sub_clause = self.generator.generate_subordinate_clause(sub_conj, sub_subj, sub_obj, sub_verb)

        if front_subordinate:
            # Fronted subordinate clause acts as Vorfeld element -> Triggers inversion in main clause!
            # e.g.: "Omdat Jan ziek is, blijft hij thuis."
            cap_sub = sub_clause[0].upper() + sub_clause[1:] if sub_clause else ""
            return f"{cap_sub}, {main_verb} {main_sub} {main_obj}."
        else:
            # Main clause first, then subordinate clause
            main_clause = self.generator.generate_v2_sentence(main_sub, main_verb, main_obj).rstrip(".")
            return f"{main_clause}, {sub_clause}."

    def get_idiomatic_expression(self, context_key: str) -> str:
        return self.idioms.get(context_key, "Dat klopt als een bus.")
