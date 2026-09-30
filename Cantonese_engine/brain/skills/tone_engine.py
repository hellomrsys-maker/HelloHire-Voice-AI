"""
Cantonese Tone and Jyutping Phonological Engine.
Handles 9 traditional Cantonese tones (6 citation tones + 3 entering/checked tones on -p, -t, -k),
tone contours, and character-to-Jyutping phonological mapping.
"""

from typing import Dict, List, Optional, Tuple

CHAR_JYUTPING_MAP = {
    # Pronouns
    "我": ("ngo5", 5, "陽上", "low rising", "23", False),
    "你": ("nei5", 5, "陽上", "low rising", "23", False),
    "佢": ("keoi5", 5, "陽上", "low rising", "23", False),
    "哋": ("dei6", 6, "陽去", "low level", "22", False),
    
    # Ditransitive & Verbs
    "畀": ("bei2", 2, "陰上", "high rising", "35", False),
    "送": ("sung3", 3, "陰去", "mid level", "33", False),
    "教": ("gaau3", 3, "陰去", "mid level", "33", False),
    "借": ("ze3", 3, "陰去", "mid level", "33", False),
    "還": ("waan4", 4, "陽平", "low falling", "21", False),
    "派": ("paai3", 3, "陰去", "mid level", "33", False),
    "食": ("sik6", 9, "陽入", "low checked", "22", True),  # Entering tone 9
    "飲": ("jam2", 2, "陰上", "high rising", "35", False),
    "睇": ("tai2", 2, "陰上", "high rising", "35", False),
    "講": ("gong2", 2, "陰上", "high rising", "35", False),
    "諗": ("nam2", 2, "陰上", "high rising", "35", False),
    "行": ("haang4", 4, "陽平", "low falling", "21", False),
    "走": ("zau2", 2, "陰上", "high rising", "35", False),
    "買": ("maai5", 5, "陽上", "low rising", "23", False),
    "賣": ("maai6", 6, "陽去", "low level", "22", False),
    "識": ("sik1", 7, "上陰入", "high checked", "55", True),  # Entering tone 7
    "錫": ("sek3", 8, "下陰入", "mid checked", "33", True),  # Entering tone 8
    "有": ("jau5", 5, "陽上", "low rising", "23", False),
    "冇": ("mou5", 5, "陽上", "low rising", "23", False),
    "係": ("hai6", 6, "陽去", "low level", "22", False),
    
    # Classifiers
    "個": ("go3", 3, "陰去", "mid level", "33", False),
    "隻": ("zek3", 8, "下陰入", "mid checked", "33", True),
    "條": ("tiu4", 4, "陽平", "low falling", "21", False),
    "件": ("gin6", 6, "陽去", "low level", "22", False),
    "本": ("bun2", 2, "陰上", "high rising", "35", False),
    "架": ("gaa3", 3, "陰去", "mid level", "33", False),
    "間": ("gaan1", 1, "陰平", "high level", "55", False),
    "張": ("zoeng1", 1, "陰平", "high level", "55", False),
    "啲": ("di1", 1, "陰平", "high level", "55", False),
    
    # Aspect Enclitics
    "咗": ("zo2", 2, "陰上", "high rising", "35", False),
    "緊": ("gan2", 2, "陰上", "high rising", "35", False),
    "過": ("gwo3", 3, "陰去", "mid level", "33", False),
    "開": ("hoi1", 1, "陰平", "high level", "55", False),
    "住": ("zyu6", 6, "陽去", "low level", "22", False),
    "吓": ("haa5", 5, "陽上", "low rising", "23", False),
    "晒": ("saai3", 3, "陰去", "mid level", "33", False),
    "埋": ("maai4", 4, "陽平", "low falling", "21", False),
    "返": ("faan1", 1, "陰平", "high level", "55", False),
    
    # Sentence-Final Particles
    "喇": ("laa3", 3, "陰去", "mid level", "33", False),
    "啦": ("laa1", 1, "陰平", "high level", "55", False),
    "呀": ("aa3", 3, "陰去", "mid level", "33", False),
    "㗎": ("gaa3", 3, "陰去", "mid level", "33", False),
    "啫": ("ze1", 1, "陰平", "high level", "55", False),
    "喎": ("wo3", 3, "陰去", "mid level", "33", False),
    "囉": ("lo1", 1, "陰平", "high level", "55", False),
    "添": ("tim1", 1, "陰平", "high level", "55", False),
    "咩": ("me1", 1, "陰平", "high level", "55", False),
    "咋": ("zaa3", 3, "陰去", "mid level", "33", False),
    
    # Common Nouns & Adjectives
    "書": ("syu1", 1, "陰平", "high level", "55", False),
    "車": ("ce1", 1, "陰平", "high level", "55", False),
    "人": ("jan4", 4, "陽平", "low falling", "21", False),
    "狗": ("gau2", 2, "陰上", "high rising", "35", False),
    "貓": ("maau1", 1, "陰平", "high level", "55", False),
    "大": ("daai6", 6, "陽去", "low level", "22", False),
    "細": ("sai3", 3, "陰去", "mid level", "33", False),
    "靚": ("leng3", 3, "陰去", "mid level", "33", False),
    "先": ("sin1", 1, "陰平", "high level", "55", False),
    "多": ("do1", 1, "陰平", "high level", "55", False),
    "少": ("siu2", 2, "陰上", "high rising", "35", False)
}

def analyze_character_tone(char: str) -> Dict[str, any]:
    """
    Returns phonological profile for a character:
    Jyutping, traditional 9-tone number (1-9), tone category name, pitch contour, checked coda flag.
    """
    if char in CHAR_JYUTPING_MAP:
        jp, tone_num, cat_name, desc, contour, is_checked = CHAR_JYUTPING_MAP[char]
        return {
            "character": char,
            "jyutping": jp,
            "tone_number": tone_num,
            "category_name": cat_name,
            "description": desc,
            "pitch_contour": contour,
            "is_checked_tone": is_checked
        }
    return {
        "character": char,
        "jyutping": "unknown",
        "tone_number": 0,
        "category_name": "unknown",
        "description": "unregistered",
        "pitch_contour": "00",
        "is_checked_tone": False
    }

def text_to_jyutping(text: str) -> List[Dict[str, any]]:
    """
    Transcribes Cantonese text to a list of Jyutping syllables and tone profiles.
    """
    result = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf' or '\U00020000' <= char <= '\U0002a6df':
            result.append(analyze_character_tone(char))
    return result

def is_entering_tone(char: str) -> bool:
    """
    Returns True if the character carries an entering tone (tones 7, 8, 9 with -p, -t, -k codas).
    """
    profile = analyze_character_tone(char)
    return profile["is_checked_tone"]
