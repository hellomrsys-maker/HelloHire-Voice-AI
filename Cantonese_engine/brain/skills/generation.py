"""
Cantonese Sentence Generation Engine.
Synthesizes grammatically authentic Cantonese utterances with canonical SVO order,
DOC inversion (V + DO + IO), aspect enclitics, postverbal adverbs, and sentence-final particles.
"""

from typing import Optional
from Cantonese_engine.brain.skills.classifier_engine import get_classifier_for_noun

def generate_cantonese_sentence(
    subject: str,
    verb: str,
    theme_object: Optional[str] = None,
    recipient_io: Optional[str] = None,
    aspect: Optional[str] = None,
    adverb: Optional[str] = None,
    sfp: Optional[str] = None
) -> str:
    """
    Generates a natural Cantonese sentence enforcing:
    1. Ditransitive DOC inversion: V + [Aspect] + DO + IO (e.g. 畀咗本書我)
    2. Postverbal adverbs: V + [Aspect] + Adv (e.g. 行先)
    3. Sentence-final particles: coda position (e.g. 喇)
    """
    elements = [subject]
    verb_phrase = verb
    
    if aspect:
        verb_phrase += aspect
        
    if adverb and adverb in ["先", "多", "少"]:
        # Postverbal adverb
        if theme_object and not recipient_io:
            verb_phrase += adverb
        elif not theme_object:
            verb_phrase += adverb
            
    elements.append(verb_phrase)
    
    if theme_object and recipient_io:
        # Ditransitive: V + DO + IO
        elements.append(theme_object)
        elements.append(recipient_io)
    elif theme_object:
        elements.append(theme_object)
        if adverb and adverb not in ["先", "多", "少"]:
            elements.append(adverb)
            
    sentence = "".join(elements)
    
    if sfp:
        sentence += sfp
    else:
        sentence += "。"
        
    return sentence

def generate_comparative(subject_a: str, subject_b: str, adjective: str) -> str:
    """
    Generates a canonical Cantonese comparative using post-adjectival '過' (A + Adj + 過 + B).
    """
    return f"{subject_a}{adjective}過{subject_b}。"
