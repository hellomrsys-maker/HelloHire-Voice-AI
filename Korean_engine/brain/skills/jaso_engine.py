"""
Korean Engine — Jaso Decomposition & Composition Skill
Provides exact Unicode mathematical decomposition and composition for Hangul syllables.
"""

from typing import Tuple, Optional, Dict, Any

CHOSUNG_LIST = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

JUNGSUNG_LIST = [
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
    'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'
]

JONGSUNG_LIST = [
    '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
    'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

BASE_CODE = 0xAC00 # '가'
MAX_CODE = 0xD7A3  # '힣'

def is_hangul_syllable(char: str) -> bool:
    """Check if a single character is a precomposed Hangul syllable."""
    if not char or len(char) != 1:
        return False
    code = ord(char)
    return BASE_CODE <= code <= MAX_CODE

def decompose_syllable(char: str) -> Optional[Tuple[str, str, str]]:
    """
    Decompose a single Hangul syllable into (Chosung, Jungsung, Jongsung).
    If char is not a Hangul syllable, returns None.
    """
    if not is_hangul_syllable(char):
        return None
        
    code = ord(char) - BASE_CODE
    jong_idx = code % 28
    jung_idx = (code // 28) % 21
    cho_idx = (code // 28) // 21
    
    return CHOSUNG_LIST[cho_idx], JUNGSUNG_LIST[jung_idx], JONGSUNG_LIST[jong_idx]

def compose_syllable(cho: str, jung: str, jong: str = "") -> Optional[str]:
    """
    Compose (Chosung, Jungsung, Jongsung) into a unified Hangul syllable.
    """
    if cho not in CHOSUNG_LIST or jung not in JUNGSUNG_LIST or jong not in JONGSUNG_LIST:
        return None
        
    cho_idx = CHOSUNG_LIST.index(cho)
    jung_idx = JUNGSUNG_LIST.index(jung)
    jong_idx = JONGSUNG_LIST.index(jong)
    
    code = BASE_CODE + (cho_idx * 21 + jung_idx) * 28 + jong_idx
    return chr(code)

def has_batchim(char: str) -> bool:
    """
    Returns True if the character is a Hangul syllable with a final consonant (받침).
    """
    decomp = decompose_syllable(char)
    if not decomp:
        return False
    return len(decomp[2]) > 0

def get_batchim(char: str) -> str:
    """
    Returns the batchim grapheme of a Hangul syllable, or empty string if none.
    """
    decomp = decompose_syllable(char)
    if not decomp:
        return ""
    return decomp[2]
