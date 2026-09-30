"""
Bengali Sentence Generator: Synthesizes grammatically verified SOV clauses
with classifier concord, compound verbs, and sentence-final negation.
"""

from typing import Dict, Any, Optional, List
from .verb_conjugator import BengaliVerbConjugator
from .classifier_engine import BengaliClassifierEngine
from .compound_verb_engine import BengaliCompoundVerbEngine


class BengaliGenerator:
    """
    Synthesizes Bengali sentences from structured linguistic specifications.
    """

    PRONOUN_TIER_MAP = {
        "আমি": "1st", "আমরা": "1st",
        "তুমি": "2nd_fam", "তোমরা": "2nd_fam",
        "তুই": "2nd_int", "তোরা": "2nd_int",
        "আপনি": "hon", "আপনারা": "hon",
        "তিনি": "hon", "তাঁরা": "hon",
        "সে": "3rd_ord", "তারা": "3rd_ord"
    }

    def __init__(self):
        self.conjugator = BengaliVerbConjugator()
        self.classifier_engine = BengaliClassifierEngine()
        self.compound_engine = BengaliCompoundVerbEngine(self.conjugator)

    def generate_clause(
        self,
        verb_lemma: str,
        subject: Optional[str] = None,
        direct_object: Optional[str] = None,
        indirect_object: Optional[str] = None,
        adverbial: Optional[str] = None,
        tense: str = "present_simple",
        politeness: str = "familiar",
        negative: bool = False,
        negative_marker: str = "না",
        vector_verb: Optional[str] = None,
        classifier: Optional[str] = None,
        punctuation: str = "।"
    ) -> str:
        """
        Synthesizes a Bengali sentence following SOV ordering rules.
        """
        # Determine person/honorific tier
        tier = "3rd_ord"
        if subject:
            tier = self.PRONOUN_TIER_MAP.get(subject, "3rd_ord")
            if politeness == "superior" and tier in ("3rd_ord", "2nd_fam"):
                tier = "hon"
        elif politeness == "superior":
            tier = "hon"
        elif politeness == "familiar":
            tier = "2nd_fam"
        elif politeness == "intimate":
            tier = "2nd_int"

        # Conjugate verb or compound verb
        if vector_verb:
            verb_str = self.compound_engine.compose_compound(verb_lemma, vector_verb, tense, tier)
        else:
            verb_str = self.conjugator.conjugate(verb_lemma, tense, tier)

        # Prepare direct object with classifier if requested
        dobj_str = direct_object
        if dobj_str and classifier:
            dobj_str = self.classifier_engine.attach_classifier(dobj_str, classifier)

        # Assemble constituents in SOV order:
        # [Subject] + [Adverbial] + [Indirect Object] + [Direct Object] + [Verb] + [Negation]
        constituents = []
        if subject:
            constituents.append(subject)
        if adverbial:
            constituents.append(adverbial)
        if indirect_object:
            constituents.append(indirect_object)
        if dobj_str:
            constituents.append(dobj_str)
        
        constituents.append(verb_str)

        if negative:
            constituents.append(negative_marker)

        sentence = " ".join(constituents)
        if punctuation:
            sentence = f"{sentence}{punctuation}"
        return sentence
