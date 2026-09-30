"""
Thai Politeness Particle and Speech-Act Concord Engine.
Audits male (ครับ) and female (ค่ะ / คะ) particles, enforcing tone-act harmony:
- ค่ะ (falling tone): Declaratives, answers, gratitude (e.g. ขอบคุณค่ะ)
- คะ (high tone): Interrogatives, inquiries, calls (e.g. ไปไหนคะ?)
"""

from typing import Dict, List, Optional
import re

FEMALE_DECLARATIVE_CONCORD_ERRORS = [
    ("สวัสดีคะ", "สวัสดีค่ะ"),
    ("ขอบคุณคะ", "ขอบคุณค่ะ"),
    ("ใช่คะ", "ใช่ค่ะ"),
    ("เข้าใจแล้วคะ", "เข้าใจแล้วค่ะ")
]

FEMALE_QUESTION_CONCORD_ERRORS = [
    ("ไปไหนค่ะ", "ไปไหนคะ"),
    ("จริงหรือค่ะ", "จริงหรือคะ"),
    ("อะไรค่ะ", "อะไรคะ"),
    ("หรือยังค่ะ", "หรือยังคะ")
]

def audit_politeness_particles(text: str) -> Dict[str, any]:
    """
    Audits sentence-final politeness particles for speaker gender and speech-act harmony.
    """
    violations = []
    corrected = text
    
    # Check declarative errors with 'คะ'
    for bad, good in FEMALE_DECLARATIVE_CONCORD_ERRORS:
        if bad in text:
            violations.append(f"Invalid female declarative '{bad}' (used high-tone 'คะ' instead of falling-tone 'ค่ะ')")
            corrected = corrected.replace(bad, good)
            
    # Check question errors with 'ค่ะ'
    for bad, good in FEMALE_QUESTION_CONCORD_ERRORS:
        if bad in text or f"{bad}?" in text:
            violations.append(f"Invalid female interrogative '{bad}' (used falling-tone 'ค่ะ' instead of high-tone 'คะ')")
            corrected = corrected.replace(bad, good)
            
    has_male_part = "ครับ" in text
    has_female_part = "ค่ะ" in text or "คะ" in text
    has_particles = has_male_part or has_female_part
    
    is_concordant = len(violations) == 0
    
    return {
        "text": text,
        "is_concordant": is_concordant,
        "violations": violations,
        "corrected_text": corrected,
        "has_particles": has_particles,
        "speaker_gender_hint": "male" if has_male_part else ("female" if has_female_part else "neutral"),
        "concord_flag": 1 if is_concordant else 0
    }
