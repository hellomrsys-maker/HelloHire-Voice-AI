"""
Thai Sentence Generation Engine.
Synthesizes canonical isolating SVO clauses with post-nominal numeral classifiers,
preverbal aspect markers, and gendered politeness particles.
"""

from typing import Optional
from Thai_engine.brain.skills.classifier_engine import get_classifier_for_noun

def generate_thai_sentence(
    subject: str,
    verb: str,
    object_noun: Optional[str] = None,
    numeral: Optional[str] = None,
    aspect_preverbal: Optional[str] = None,
    polite_particle: Optional[str] = None
) -> str:
    """
    Synthesizes a natural, unspaced Thai clause:
    [Subject] + [Aspect] + [Verb] + [Object] + [Numeral] + [Classifier] + [Particle]
    """
    parts = [subject]
    
    if aspect_preverbal:
        parts.append(aspect_preverbal)
        
    parts.append(verb)
    
    if object_noun:
        parts.append(object_noun)
        if numeral:
            clf = get_classifier_for_noun(object_noun)
            parts.append(numeral)
            parts.append(clf)
            
    if polite_particle:
        parts.append(polite_particle)
        
    # Standard Thai uses scriptio continua (no spaces within a clause)
    return "".join(parts)
