"""
Portuguese Sentence Generator: Synthesizes grammatically verified SVO clauses
with clitic placement, tense/mood concord, and contractions.
"""

from typing import Dict, Any, Optional, List
from .verb_conjugator import PortugueseVerbConjugator
from .clitic_engine import PortugueseCliticEngine
from .contraction_engine import PortugueseContractionEngine


class PortugueseGenerator:
    """
    Synthesizes Portuguese sentences adhering to SVO order and clitic placement rules.
    """

    PRONOUN_PERSON_MAP = {
        "eu": "eu", "tu": "tu", "ele": "ele", "ela": "ele", "você": "ele",
        "nós": "nos", "vós": "vos", "eles": "eles", "elas": "eles", "vocês": "eles"
    }

    def __init__(self):
        self.conjugator = PortugueseVerbConjugator()
        self.clitic_engine = PortugueseCliticEngine()
        self.contraction_engine = PortugueseContractionEngine()

    def generate_clause(
        self,
        verb_lemma: str,
        subject: Optional[str] = None,
        direct_object: Optional[str] = None,
        indirect_object: Optional[str] = None,
        clitic: Optional[str] = None,
        mood: str = "indicativo",
        tense: str = "presente",
        person: str = "ele",
        negative: bool = False,
        punctuation: str = "."
    ) -> str:
        """
        Synthesizes a Portuguese clause.
        """
        p = person
        if subject:
            p = self.PRONOUN_PERSON_MAP.get(subject.lower(), person)

        verb_form = self.conjugator.conjugate(verb_lemma, mood=mood, tense=tense, person=p)

        # Clitic placement logic
        verb_complex = verb_form
        if clitic:
            if negative:
                # Negation obligatorily attracts clitic into proclisis: "não me diz"
                verb_complex = f"{clitic} {verb_form}"
            else:
                # Default to enclisis: "diz-me"
                verb_complex = self.clitic_engine.apply_enclisis(verb_form, clitic)

        constituents = []
        if subject:
            constituents.append(subject)

        if negative:
            constituents.append("não")

        constituents.append(verb_complex)

        if direct_object:
            constituents.append(direct_object)

        if indirect_object:
            constituents.append(indirect_object)

        sentence = " ".join(constituents)
        if punctuation:
            sentence = f"{sentence}{punctuation}"

        return sentence
