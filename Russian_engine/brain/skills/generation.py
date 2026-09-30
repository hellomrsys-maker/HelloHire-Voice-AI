"""Russian Generation Skill.

Generates grammatical Russian clauses adhering to SVO order,
case government, animacy rules, and numeral-paucal agreement.
"""

from typing import Dict, Any, Optional
from .case_engine import RussianCaseEngine
from .verb_aspect_conjugator import RussianVerbAspectConjugator
from .numeral_concord_engine import RussianNumeralConcordEngine


class RussianSentenceGenerator:
    def __init__(
        self,
        case_engine: RussianCaseEngine = None,
        verb_conjugator: RussianVerbAspectConjugator = None,
        numeral_engine: RussianNumeralConcordEngine = None
    ):
        self.case_engine = case_engine or RussianCaseEngine()
        self.verb_conjugator = verb_conjugator or RussianVerbAspectConjugator()
        self.numeral_engine = numeral_engine or RussianNumeralConcordEngine(self.case_engine)

    def generate_transitive_svo(
        self,
        subj_lemma: str,
        subj_gender: str,
        verb_lemma: str,
        obj_lemma: str,
        obj_gender: str,
        obj_declension: str = "2nd",
        obj_animacy: bool = False,
        tense: str = "past"
    ) -> str:
        """Generates a standard Russian Subject-Verb-Object (SVO) sentence."""
        # Subject in Nominative
        subject = subj_lemma.capitalize()

        # Verb conjugated
        if tense == "past":
            verb = self.verb_conjugator.conjugate_past(verb_lemma, gender=subj_gender, number="sing")
        else:
            verb = self.verb_conjugator.conjugate_present_1st_sing(verb_lemma)

        # Object in Accusative with animacy rules
        obj = self.case_engine.inflect_noun(
            lemma=obj_lemma,
            case="acc",
            gender=obj_gender,
            declension=obj_declension,
            number="sing",
            animacy=obj_animacy
        )

        return f"{subject} {verb} {obj}."

    def generate_prep_clause(
        self,
        subj_lemma: str,
        subj_gender: str,
        verb_lemma: str,
        prep: str,
        noun_lemma: str,
        noun_gender: str = "masc",
        noun_declension: str = "2nd"
    ) -> str:
        """Generates Subject + Verb + Preposition + Governed Noun."""
        subject = subj_lemma.capitalize()
        verb = self.verb_conjugator.conjugate_past(verb_lemma, gender=subj_gender, number="sing")
        expected_case = self.case_engine.get_expected_case_for_prep(prep) or "prep"
        noun = self.case_engine.inflect_noun(
            lemma=noun_lemma,
            case=expected_case,
            gender=noun_gender,
            declension=noun_declension,
            number="sing"
        )
        return f"{subject} {verb} {prep} {noun}."
