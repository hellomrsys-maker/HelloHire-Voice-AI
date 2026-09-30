"""
Hindustani Composition Task Pipeline.
Composes expressive, syntactically conforming SOV sentences with vector verb enrichment
and split-ergative concord across aspects.
"""

from typing import Dict, Any, Optional
from ..skills.generation import HindustaniGenerator
from ..skills.compound_verb_engine import CompoundVerbEngine


class HindustaniCompositionPipeline:
    """
    Composition and prose generator for Hindustani language synthesis.
    """

    def __init__(self):
        self.generator = HindustaniGenerator()
        self.compound_engine = CompoundVerbEngine()

    def compose_statement(
        self,
        subject: str,
        verb_lemma: str,
        obj: Optional[str] = None,
        aspect: str = "habitual",
        subject_gender: str = "M",
        subject_number: str = "SG",
        object_gender: str = "M",
        object_number: str = "SG",
        honorific: bool = False
    ) -> Dict[str, Any]:
        """
        Synthesizes a declarative SOV statement with full grammatical concord.
        """
        sentence = self.generator.generate_statement(
            subject=subject,
            verb_lemma=verb_lemma,
            obj=obj,
            aspect=aspect,
            subject_gender=subject_gender,
            subject_number=subject_number,
            object_gender=object_gender,
            object_number=object_number,
            honorific=honorific
        )

        return {
            "composed_text": sentence,
            "subject": subject,
            "verb": verb_lemma,
            "aspect": aspect,
            "is_ergative": aspect == "perfective" and self.generator.conjugator.is_transitive(verb_lemma)
        }

    def compose_compound_verb_statement(
        self,
        subject: str,
        v1_stem: str,
        v2_vector: str,
        obj: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a sentence enriched with a polar + vector compound verb (e.g. khaa lena).
        """
        compound_info = self.compound_engine.analyze_compound_verb(v1_stem, v2_vector)
        obj_str = f" {obj}" if obj else ""
        text = f"{subject.capitalize()}{obj_str} {v1_stem} {v2_vector}."

        return {
            "composed_text": text,
            "compound_info": compound_info
        }
