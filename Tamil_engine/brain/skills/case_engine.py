"""
Tamil Case Declension and Agglutinative Morphology Engine.
Analyzes and applies the 8 classical Tamil cases (Vēṟṟumai):
1: Nominative (Bare)
2: Accusative (-ai)
3: Instrumental (-āl) / Sociative (-uṭaṉ)
4: Dative (-ku / -ukku)
5: Ablative (-iliruntu)
6: Genitive (-iṉ / -uṭaiya)
7: Locative (-il / -iṭam)
8: Vocative (-ē)
"""

from typing import Dict, List, Optional, Tuple

CASE_SUFFIXES = [
    ("ablative", "ிலிருந்து", 5),
    ("ablative", "இலிருந்து", 5),
    ("sociative", "உடன்", 3),
    ("sociative", "ுடன்", 3),
    ("instrumental", "ால்", 3),
    ("instrumental", "ஆல்", 3),
    ("dative", "க்கு", 4),
    ("dative", "உக்கு", 4),
    ("dative", "ுக்கு", 4),
    ("genitive", "உடைய", 6),
    ("genitive", "ுடைய", 6),
    ("genitive", "ின்", 6),
    ("genitive", "இன்", 6),
    ("locative", "இடம்", 7),
    ("locative", "ிடம்", 7),
    ("locative", "இல்", 7),
    ("locative", "ில்", 7),
    ("accusative", "ை", 2),
    ("accusative", "ஐ", 2),
    ("vocative", "ே", 8),
    ("vocative", "ஏ", 8)
]

def analyze_noun_case(noun_token: str) -> Dict[str, any]:
    """
    Analyzes an inflected Tamil noun to identify case suffix and grammatical case.
    """
    # Special pronoun handling
    pronoun_cases = {
        "நான்": ("nominative", 1, "நான்"),
        "என்னை": ("accusative", 2, "நான்"),
        "என்னால்": ("instrumental", 3, "நான்"),
        "என்னுடன்": ("sociative", 3, "நான்"),
        "எனக்கு": ("dative", 4, "நான்"),
        "என்னிலிருந்து": ("ablative", 5, "நான்"),
        "என்": ("genitive", 6, "நான்"),
        "என்னுடைய": ("genitive", 6, "நான்"),
        "என்னிடம்": ("locative", 7, "நான்"),
        
        "அவன்": ("nominative", 1, "அவன்"),
        "அவனை": ("accusative", 2, "அவன்"),
        "அவனால்": ("instrumental", 3, "அவன்"),
        "அவனுடன்": ("sociative", 3, "அவன்"),
        "அவனுக்கு": ("dative", 4, "அவன்"),
        "அவனிடமிருந்து": ("ablative", 5, "அவன்"),
        "அவனுடைய": ("genitive", 6, "அவன்"),
        "அவனிடம்": ("locative", 7, "அவன்"),
        
        "நீ": ("nominative", 1, "நீ"),
        "உன்னை": ("accusative", 2, "நீ"),
        "உன்னால்": ("instrumental", 3, "நீ"),
        "உன்னுடன்": ("sociative", 3, "நீ"),
        "உனக்கு": ("dative", 4, "நீ"),
        "உன்னுடைய": ("genitive", 6, "நீ"),
        "உன்னிடம்": ("locative", 7, "நீ")
    }
    
    if noun_token in pronoun_cases:
        c_name, c_num, stem = pronoun_cases[noun_token]
        return {
            "token": noun_token,
            "stem": stem,
            "case_name": c_name,
            "case_number": c_num,
            "is_inflected": c_num != 1
        }
        
    for c_name, suff, c_num in CASE_SUFFIXES:
        if noun_token.endswith(suff):
            stem = noun_token[:-len(suff)]
            return {
                "token": noun_token,
                "stem": stem,
                "case_name": c_name,
                "case_number": c_num,
                "suffix": suff,
                "is_inflected": True
            }
            
    return {
        "token": noun_token,
        "stem": noun_token,
        "case_name": "nominative",
        "case_number": 1,
        "suffix": None,
        "is_inflected": False
    }

def inflect_case(noun: str, case_number: int) -> str:
    """
    Applies classical Tamil case declension to a noun stem.
    """
    if case_number == 1:
        return noun
    elif case_number == 2:  # Accusative
        if noun == "மரம்": return "மரத்தை"
        if noun == "புத்தகம்": return "புத்தகத்தை"
        if noun == "அவன்": return "அவனை"
        if noun == "நான்": return "என்னை"
        return f"{noun}ை"
    elif case_number == 3:  # Instrumental
        if noun == "மரம்": return "மரத்தால்"
        if noun == "அவன்": return "அவனால்"
        return f"{noun}ால்"
    elif case_number == 4:  # Dative
        if noun == "வீடு": return "வீட்டுக்கு"
        if noun == "அவன்": return "அவனுக்கு"
        if noun == "நான்": return "எனக்கு"
        return f"{noun}க்கு"
    elif case_number == 5:  # Ablative
        if noun == "ஊர்": return "ஊரிலிருந்து"
        if noun == "மரம்": return "மரத்திலிருந்து"
        return f"{noun}ிலிருந்து"
    elif case_number == 6:  # Genitive
        if noun == "அவன்": return "அவனுடைய"
        if noun == "நான்": return "என்"
        return f"{noun}ின்"
    elif case_number == 7:  # Locative
        if noun == "மரம்": return "மரத்தில்"
        if noun == "மேசை": return "மேசையில்"
        if noun == "அவன்": return "அவனிடம்"
        return f"{noun}ில்"
    elif case_number == 8:  # Vocative
        return f"{noun}ே"
    return noun
