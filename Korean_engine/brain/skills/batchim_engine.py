"""
Korean Engine — Batchim & Phonology Skill
Handles final consonant (받침) detection, 7-stop neutralization,
nasalization, tensification, and liquidization.
"""

from typing import Dict, Any, Optional
from .jaso_engine import decompose_syllable, compose_syllable, has_batchim, get_batchim

# Coda neutralization table: maps any batchim to one of the 7 canonical stops
CODA_NEUTRALIZATION = {
    'ㄱ': 'ㄱ', 'ㄲ': 'ㄱ', 'ㅋ': 'ㄱ', 'ㄳ': 'ㄱ', 'ㄺ': 'ㄱ',
    'ㄴ': 'ㄴ', 'ㄵ': 'ㄴ', 'ㄶ': 'ㄴ',
    'ㄷ': 'ㄷ', 'ㅅ': 'ㄷ', 'ㅆ': 'ㄷ', 'ㅈ': 'ㄷ', 'ㅊ': 'ㄷ', 'ㅌ': 'ㄷ', 'ㅎ': 'ㄷ',
    'ㄹ': 'ㄹ', 'ㄼ': 'ㄹ', 'ㄽ': 'ㄹ', 'ㄾ': 'ㄹ', 'ㅀ': 'ㄹ',
    'ㅁ': 'ㅁ', 'ㄻ': 'ㅁ',
    'ㅂ': 'ㅂ', 'ㅍ': 'ㅂ', 'ㄿ': 'ㅂ', 'ㅄ': 'ㅂ',
    'ㅇ': 'ㅇ'
}

# Nasalization: stops [ㄱ, ㄷ, ㅂ] before nasals [ㄴ, ㅁ]
NASALIZATION_MAP = {
    'ㄱ': 'ㅇ',
    'ㄷ': 'ㄴ',
    'ㅂ': 'ㅁ'
}

def neutralize_batchim(char: str) -> str:
    """
    Neutralize syllable coda to one of the 7 phonetic stops [ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ].
    """
    decomp = decompose_syllable(char)
    if not decomp:
        return char
    cho, jung, jong = decomp
    if not jong:
        return char
    neutral_jong = CODA_NEUTRALIZATION.get(jong, jong)
    return compose_syllable(cho, jung, neutral_jong) or char

def apply_phonological_processes(c1: str, c2: str) -> Dict[str, Any]:
    """
    Given two adjacent syllables c1 and c2, check phonological alternations:
    - Nasalization (비음화)
    - Liquidization (유음화)
    - Palatalization (구개음화)
    """
    d1 = decompose_syllable(c1)
    d2 = decompose_syllable(c2)
    if not d1 or not d2:
        return {"altered": False, "c1": c1, "c2": c2}
        
    cho1, jung1, jong1 = d1
    cho2, jung2, jong2 = d2
    
    if not jong1:
        return {"altered": False, "c1": c1, "c2": c2}
        
    neutral_coda = CODA_NEUTRALIZATION.get(jong1, jong1)
    
    # 1. Nasalization (비음화): [ㄱ, ㄷ, ㅂ] + [ㄴ, ㅁ] -> [ㅇ, ㄴ, ㅁ] + [ㄴ, ㅁ]
    if neutral_coda in NASALIZATION_MAP and cho2 in {'ㄴ', 'ㅁ'}:
        nasal_jong = NASALIZATION_MAP[neutral_coda]
        alt_c1 = compose_syllable(cho1, jung1, nasal_jong)
        return {
            "altered": True,
            "rule": "nasalization",
            "c1_surface": alt_c1,
            "c2_surface": c2
        }
        
    # 2. Liquidization (유음화): ㄴ + ㄹ or ㄹ + ㄴ -> ㄹ + ㄹ
    if (neutral_coda == 'ㄴ' and cho2 == 'ㄹ') or (neutral_coda == 'ㄹ' and cho2 == 'ㄴ'):
        alt_c1 = compose_syllable(cho1, jung1, 'ㄹ')
        alt_c2 = compose_syllable('ㄹ', jung2, jong2)
        return {
            "altered": True,
            "rule": "liquidization",
            "c1_surface": alt_c1,
            "c2_surface": alt_c2
        }
        
    # 3. Palatalization (구개음화): ㄷ, ㅌ + 이 -> 지, 치
    if jong1 in {'ㄷ', 'ㅌ'} and cho2 == 'ㅇ' and jung2 == 'ㅣ':
        palatal_cho = 'ㅈ' if jong1 == 'ㄷ' else 'ㅊ'
        alt_c1 = compose_syllable(cho1, jung1, '')
        alt_c2 = compose_syllable(palatal_cho, jung2, jong2)
        return {
            "altered": True,
            "rule": "palatalization",
            "c1_surface": alt_c1,
            "c2_surface": alt_c2
        }
        
    return {"altered": False, "c1": c1, "c2": c2}
