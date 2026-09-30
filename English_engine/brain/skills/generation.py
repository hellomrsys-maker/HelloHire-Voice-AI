"""
generation.py - Grammar-constrained text generation with register and structural controls.
Generates declarative, interrogative, imperative, and passive transforms.
"""

from __future__ import annotations
from typing import Dict, Any, Optional


class EnglishTextGenerator:
    """
    Grammar-governed generator producing syntactically correct sentences under target constraints.
    """

    def generate(
        self,
        subject: str,
        verb: str,
        object_: Optional[str] = None,
        tense: str = "present",
        aspect: str = "simple",
        voice: str = "active",
        form: str = "declarative",
        sentence_type: Optional[str] = None,
    ) -> str:
        s_type = sentence_type or form
        return self.generate_clause(
            subject=subject,
            verb=verb,
            object_=object_,
            tense=tense,
            aspect=aspect,
            voice=voice,
            sentence_type=s_type,
        )

    def generate_clause(
        self,
        subject: str,
        verb: str,
        object_: Optional[str] = None,
        tense: str = "present",
        aspect: str = "simple",
        voice: str = "active",
        sentence_type: str = "declarative"
    ) -> str:
        """
        Synthesizes a complete clause matching grammatical specifications.
        """
        is_3sg = subject.lower() in {"he", "she", "it", "the company", "the model", "the engine"}

        # Voice transformation
        if voice == "passive" and object_:
            real_subj = object_
            real_obj = f"by {subject}"
            verb_form = f"is {verb}ed" if tense == "present" else f"was {verb}ed"
            clause = f"{real_subj.capitalize()} {verb_form} {real_obj}."
            return clause

        # Verb conjugation
        if tense == "present":
            if aspect == "simple":
                v_str = f"{verb}s" if is_3sg else verb
            elif aspect == "progressive":
                aux = "is" if is_3sg else ("am" if subject.lower() == "i" else "are")
                v_str = f"{aux} {verb}ing"
            elif aspect == "perfect":
                aux = "has" if is_3sg else "have"
                v_str = f"{aux} {verb}ed"
            else:
                v_str = verb
        elif tense == "past":
            v_str = f"{verb}ed"
        else: # future
            v_str = f"will {verb}"

        obj_str = f" {object_}" if object_ else ""

        # Sentence type transformation
        if sentence_type == "interrogative":
            aux_q = "Does" if is_3sg else "Do"
            if tense == "past":
                aux_q = "Did"
            return f"{aux_q} {subject} {verb}{obj_str}?"
        elif sentence_type == "imperative":
            return f"{verb.capitalize()}{obj_str}."
        else:
            return f"{subject.capitalize()} {v_str}{obj_str}."
