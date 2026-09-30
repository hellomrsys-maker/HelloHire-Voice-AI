"""
Vietnamese Sentence Generation Engine
Synthesizes canonical SVO clauses with classifiers, TAM preverbal markers, and kinship deixis.
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.brain.skills.classifier_engine import VietnameseClassifierEngine
from Vietnamese_engine.brain.skills.tam_engine import VietnameseTAMEngine

class VietnameseGenerator:
    """
    Synthesizes grammatical Vietnamese sentences:
    [Subject] + [TAM Marker] + [Verb] + [Direct Object (Numeral + Classifier + Noun)]
    """

    def __init__(self):
        self.clf_engine = VietnameseClassifierEngine()
        self.tam_engine = VietnameseTAMEngine()

    def generate_svo_clause(
        self,
        subject: Optional[str],
        verb: str,
        direct_object_noun: Optional[str] = None,
        quantifier: Optional[str] = None,
        classifier: Optional[str] = None,
        tense: Optional[str] = None,
        aspect: Optional[str] = None,
        negative: bool = False
    ) -> str:
        """
        Synthesizes an isolating SVO clause.
        """
        components = []
        
        # 1. Subject
        if subject:
            components.append(subject.strip())
            
        # 2. TAM Preverbal cluster + Verb
        pred = self.tam_engine.construct_tam_predicate(
            verb=verb,
            tense=tense,
            aspect=aspect,
            negative=negative
        )
        components.append(pred)
        
        # 3. Direct Object with Classifier
        if direct_object_noun:
            if quantifier:
                np = self.clf_engine.construct_quantified_np(
                    number=quantifier,
                    noun=direct_object_noun,
                    classifier=classifier
                )
                components.append(np)
            else:
                components.append(direct_object_noun.strip())

        return " ".join(components)
