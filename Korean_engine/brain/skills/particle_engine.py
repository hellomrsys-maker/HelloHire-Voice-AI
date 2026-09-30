"""
Korean Engine — Particle Engine Skill
Handles batchim-conditioned particle attachment, allomorph selection, and agreement validation.
"""

from typing import Dict, Any, Optional, Tuple
from .jaso_engine import has_batchim, get_batchim

PARTICLE_MAP = {
    "topic": {"consonant": "은", "vowel": "는"},
    "subject": {"consonant": "이", "vowel": "가", "honorific": "께서"},
    "object": {"consonant": "을", "vowel": "를"},
    "instrumental": {"consonant": "으로", "vowel": "로", "rieul": "로"},
    "comitative": {"consonant": "과", "vowel": "와"},
    "comitative_colloquial": {"consonant": "이랑", "vowel": "랑"},
    "dative_animate": {"normal": "에게", "colloquial": "한테", "honorific": "께"},
    "dative_inanimate": {"normal": "에"},
    "locative_dynamic": {"normal": "에서"},
    "genitive": {"normal": "의"}
}

def attach_particle(noun: str, particle_type: str, honorific: bool = False) -> str:
    """
    Attach the phonologically appropriate particle allomorph to noun.
    Handles batchim conditioning including the instrumental 'ㄹ' exception.
    """
    if not noun:
        return ""
        
    last_char = noun[-1]
    has_coda = has_batchim(last_char)
    coda = get_batchim(last_char)
    
    if particle_type == "subject" and honorific:
        return noun + "께서"
    elif particle_type == "dative_animate" and honorific:
        return noun + "께"
        
    p_info = PARTICLE_MAP.get(particle_type, {})
    
    if particle_type == "instrumental":
        if not has_coda or coda == "ㄹ":
            return noun + "로"
        else:
            return noun + "으로"
            
    if "consonant" in p_info and "vowel" in p_info:
        selected = p_info["consonant"] if has_coda else p_info["vowel"]
        return noun + selected
        
    if "normal" in p_info:
        return noun + p_info["normal"]
        
    return noun

def validate_particle_agreement(noun_with_particle: str) -> Dict[str, Any]:
    """
    Validate if the particle attached to the noun respects batchim conditioning.
    Examples:
      '책은' -> valid
      '책는' -> invalid (책 has batchim, requires 은)
      '사과가' -> valid
      '사과이' -> invalid (사과 ends in vowel, requires 가)
      '서울로' -> valid (ㄹ coda takes 로)
      '서울으로' -> invalid (ㄹ coda takes 로)
    """
    if len(noun_with_particle) < 2:
        return {"valid": True, "noun": noun_with_particle, "particle": ""}
        
    # Check 2-character particle suffixes: 으로, 에서, 에게, 이랑
    for p2, p_type in [("으로", "instrumental"), ("에서", "locative_dynamic"), ("에게", "dative_animate"), ("이랑", "comitative_colloquial")]:
        if noun_with_particle.endswith(p2):
            stem = noun_with_particle[:-len(p2)]
            if not stem:
                continue
            last_c = stem[-1]
            if p2 == "으로":
                if not has_batchim(last_c) or get_batchim(last_c) == "ㄹ":
                    return {
                        "valid": False,
                        "stem": stem,
                        "particle": p2,
                        "error": f"Stem '{stem}' ends in vowel or 'ㄹ'; expected '로', not '으로'"
                    }
            return {"valid": True, "stem": stem, "particle": p2}
            
    # Check 1-character particle suffixes: 은/는, 이/가, 을/를, 과/와, 로, 의, 에
    last_char = noun_with_particle[-1]
    stem = noun_with_particle[:-1]
    last_stem_char = stem[-1]
    stem_has_coda = has_batchim(last_stem_char)
    coda = get_batchim(last_stem_char)
    
    # Topic: 은/는
    if last_char == "은" and not stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "은", "error": f"Stem '{stem}' ends in vowel; expected '는', not '은'"}
    if last_char == "는" and stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "는", "error": f"Stem '{stem}' has batchim; expected '은', not '는'"}
        
    # Subject: 이/가
    if last_char == "이" and not stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "이", "error": f"Stem '{stem}' ends in vowel; expected '가', not '이'"}
    if last_char == "가" and stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "가", "error": f"Stem '{stem}' has batchim; expected '이', not '가'"}
        
    # Object: 을/를
    if last_char == "을" and not stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "을", "error": f"Stem '{stem}' ends in vowel; expected '를', not '을'"}
    if last_char == "를" and stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "를", "error": f"Stem '{stem}' has batchim; expected '을', not '를'"}
        
    # Comitative: 과/와
    if last_char == "과" and not stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "과", "error": f"Stem '{stem}' ends in vowel; expected '와', not '과'"}
    if last_char == "와" and stem_has_coda:
        return {"valid": False, "stem": stem, "particle": "와", "error": f"Stem '{stem}' has batchim; expected '과', not '와'"}
        
    # Instrumental: 로
    if last_char == "로" and stem_has_coda and coda != "ㄹ":
        return {"valid": False, "stem": stem, "particle": "로", "error": f"Stem '{stem}' has non-ㄹ batchim; expected '으로', not '로'"}
        
    return {"valid": True, "stem": stem, "particle": last_char}
