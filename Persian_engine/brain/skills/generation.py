"""
Persian Sentence Generation Engine
Synthesizes canonical SOV clauses with Ezafe phrases, DOM marker 'rā', and verbal concord.
"""

from typing import Dict, Any, List, Optional
from Persian_engine.brain.skills.verb_conjugator import PersianVerbConjugator
from Persian_engine.brain.skills.ezafe_engine import PersianEzafeEngine
from Persian_engine.brain.skills.dom_marker_engine import PersianDOMEngine

class PersianGenerator:
    """
    Synthesizes Persian sentences following canonical Subject-Object-Verb (SOV) order:
    [Subject] + [Object (+ rā if definite)] + [Verb]
    """

    def __init__(self):
        self.conjugator = PersianVerbConjugator()
        self.ezafe = PersianEzafeEngine()
        self.dom = PersianDOMEngine()

    def generate_sov_clause(
        self,
        subject: Optional[str],
        direct_object: Optional[str],
        verb_infinitive: str,
        tense: str = "past_simple",
        person: int = 1,
        is_definite_object: bool = True,
        negative: bool = False
    ) -> str:
        """
        Synthesizes a canonical Persian clause:
        - Subject (optional due to pro-drop)
        - Direct Object (+ 'rā' if definite)
        - Verb (final position)
        """
        components = []
        
        # 1. Subject
        if subject:
            components.append(subject.strip())
            
        # 2. Direct Object
        if direct_object:
            obj = direct_object.strip()
            if is_definite_object:
                obj = self.dom.attach_dom_marker(obj)
            components.append(obj)
            
        # 3. Verb (head-final)
        verb = self.conjugator.conjugate(verb_infinitive, tense, person, negative)
        components.append(verb)
        
        return " ".join(components)

    def generate_modified_noun_phrase(self, head: str, modifier: str) -> str:
        """Generates an Ezafe-linked noun phrase (e.g., کتابِ خوب or خانهٔ بزرگ)."""
        return self.ezafe.construct_ezafe_phrase(head, modifier)
