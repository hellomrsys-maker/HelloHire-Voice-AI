"""
Korean Engine — Surface Generation Skill
Generates well-formed Korean SOV clauses, inflected noun phrases, and epistolary communications.
"""

from typing import Dict, Any, Optional
from .particle_engine import attach_particle
from .verb_conjugator import conjugate_verb

def generate_clause(
    subject: str,
    object_noun: Optional[str],
    verb_infinitive: str,
    speech_level: str = "haeyo",
    honorific: bool = False,
    use_topic: bool = False
) -> str:
    """
    Synthesize a canonical Korean SOV clause.
    Example: subject='학생', object_noun='책', verb_infinitive='읽다', speech_level='haeyo'
             -> '학생이 책을 읽어요.'
    """
    parts = []
    
    # 1. Subject / Topic
    if subject:
        if honorific:
            parts.append(attach_particle(subject, "subject", honorific=True))
        elif use_topic:
            parts.append(attach_particle(subject, "topic"))
        else:
            parts.append(attach_particle(subject, "subject"))
            
    # 2. Object (if present)
    if object_noun:
        parts.append(attach_particle(object_noun, "object"))
        
    # 3. Verb Predicate (SOV final)
    conjugated = conjugate_verb(verb_infinitive, speech_level=speech_level, honorific=honorific)
    parts.append(conjugated + ".")
    
    return " ".join(parts)

def generate_business_email(
    recipient_name: str,
    recipient_title: str,
    body_text: str,
    sender_name: str,
    company_name: str = "솔로락"
) -> str:
    """
    Generate a formal business email conforming to Korean corporate etiquette (하십시오체 & 존칭).
    """
    salutation = f"{recipient_name} {recipient_title}님께,"
    opening = f"안녕하십니까, {company_name}의 {sender_name}입니다."
    closing = "감사합니다.\n\n" + f"{sender_name} 올림"
    
    lines = [
        salutation,
        "",
        opening,
        "",
        body_text,
        "",
        closing
    ]
    return "\n".join(lines)

def generate_polite_message(friend_name: str, message: str, sender_name: str) -> str:
    """Generate a polite everyday message (해요체)."""
    lines = [
        f"{friend_name} 씨, 안녕하세요!",
        "",
        message,
        "",
        f"- {sender_name} 드림"
    ]
    return "\n".join(lines)
