"""
French Composition Task Pipeline.
Composes expressive, syntactically conforming sentences and multi-clause statements
with mood control, tense selection, and elision resolution.
"""

from typing import Dict, Any, Optional
from ..skills.generation import FrenchGenerator
from ..skills.verb_conjugator import FrenchVerbConjugator


class FrenchCompositionPipeline:
    """
    Composition and prose generator for French language synthesis.
    """

    def __init__(self):
        self.generator = FrenchGenerator()
        self.conjugator = FrenchVerbConjugator()

    def compose_statement(
        self,
        subject: str,
        verb_lemma: str,
        obj: Optional[str] = None,
        negative: bool = False,
        tense: str = "present"
    ) -> Dict[str, Any]:
        """
        Synthesizes a declarative statement with full grammatical concord.
        """
        sentence = self.generator.generate_statement(
            subject=subject,
            verb_lemma=verb_lemma,
            obj=obj,
            negative=negative,
            tense=tense
        )

        aux_type = self.conjugator.get_auxiliary(verb_lemma)

        return {
            "composed_text": sentence,
            "subject": subject,
            "verb": verb_lemma,
            "auxiliary_type": aux_type,
            "is_negative": negative,
            "tense": tense
        }

    def compose_complex_clause(
        self,
        main_subject: str,
        main_verb: str,
        sub_subject: str,
        sub_verb: str,
        sub_obj: Optional[str] = None,
        trigger: str = "veut que"
    ) -> Dict[str, Any]:
        """
        Composes a complex sentence with a matrix clause triggering the subjunctive in the subordinate clause.
        E.g. "Le professeur veut que l'étudiant finisse son travail."
        """
        # Matrix clause: Subject + trigger
        matrix = f"{main_subject.capitalize()} {trigger}"

        # Subordinate clause: sub_subject + subjunctive form of sub_verb
        person_idx = 2  # default 3rd sing
        if sub_subject.lower() in {"je", "j'"}:
            person_idx = 0
        elif sub_subject.lower() == "tu":
            person_idx = 1
        elif sub_subject.lower() == "nous":
            person_idx = 3
        elif sub_subject.lower() == "vous":
            person_idx = 4
        elif sub_subject.lower() in {"ils", "elles"}:
            person_idx = 5

        sub_conj = self.conjugator.get_conjugation_for_person(sub_verb, person_idx, "subjonctif_present")

        obj_str = f" {sub_obj}" if sub_obj else ""
        full_text = f"{matrix} {sub_subject} {sub_conj}{obj_str}."

        return {
            "composed_text": full_text,
            "matrix_trigger": trigger,
            "subordinate_mood": "subjonctif",
            "subordinate_verb": sub_conj
        }
