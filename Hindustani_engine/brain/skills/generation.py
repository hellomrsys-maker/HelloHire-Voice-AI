"""
Hindustani Sentence Generation Skill.
Synthesizes grammatically conforming SOV clauses in habitual, continuous,
perfective (with split-ergative ne and object concord), and future aspects.
"""

from typing import Dict, Any, Optional
from .verb_conjugator import HindustaniVerbConjugator
from .oblique_case_engine import ObliqueCaseEngine


class HindustaniGenerator:
    """
    Surface realizer and sentence synthesizer for Hindustani clauses.
    """

    PRONOUN_ERGATIVE = {
        "main": "maine", "tu": "tune", "woh": "usne", "yeh": "isne",
        "hum": "humne", "tum": "tumne", "aap": "aapne",
        "मैं": "मैंने", "तू": "तूने", "वह": "उसने", "यह": "इसने",
        "हम": "हमने", "तुम": "तुमने", "आप": "आपने"
    }

    COPULA_MAP = {
        "main": "hoon", "tu": "hai", "woh": "hai", "yeh": "hai",
        "tum": "ho", "aap": "hain", "hum": "hain"
    }

    def __init__(self):
        self.conjugator = HindustaniVerbConjugator()
        self.oblique_engine = ObliqueCaseEngine()

    def generate_statement(
        self,
        subject: str,
        verb_lemma: str,
        obj: Optional[str] = None,
        aspect: str = "habitual",      # "habitual", "continuous", "perfective", "future"
        subject_gender: str = "M",
        subject_number: str = "SG",
        object_gender: str = "M",
        object_number: str = "SG",
        honorific: bool = False
    ) -> str:
        """
        Synthesizes a full SOV clause observing split-ergativity rules.
        """
        subj_low = subject.lower().strip()
        is_trans = self.conjugator.is_transitive(verb_lemma)
        is_perf = aspect == "perfective"

        # 1. Subject Formation
        if is_trans and is_perf:
            # Ergative marking
            if subj_low in self.PRONOUN_ERGATIVE:
                subj_final = self.PRONOUN_ERGATIVE[subj_low]
            else:
                # Oblique noun + ne
                oblique_noun = self.oblique_engine.to_oblique(subject, subject_gender, subject_number)
                subj_final = f"{oblique_noun} ne"
        else:
            subj_final = subject

        # 2. Verbal Agreement Formation
        if is_trans and is_perf:
            # Perfective transitive verb agrees with OBJECT
            v_form = self.conjugator.conjugate(
                verb_lemma, aspect="perfective", gender=object_gender, number=object_number, honorific=False
            )
            verb_cluster = v_form
        else:
            # Verbs agree with SUBJECT
            v_form = self.conjugator.conjugate(
                verb_lemma, aspect=aspect, gender=subject_gender, number=subject_number, honorific=honorific
            )
            # Add auxiliary if habitual or continuous
            if aspect in {"habitual", "continuous"}:
                aux = "hain" if (honorific or subject_number == "PL") else self.COPULA_MAP.get(subj_low, "hai")
                verb_cluster = f"{v_form} {aux}"
            else:
                verb_cluster = v_form

        # 3. Assemble SOV clause: Subject + Object + Verb Cluster
        obj_str = f" {obj}" if obj else ""
        statement = f"{subj_final.capitalize()}{obj_str} {verb_cluster}."
        return statement
