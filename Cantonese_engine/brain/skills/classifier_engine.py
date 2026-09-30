"""
Cantonese Classifier and Definiteness Engine.
Handles classifier selection, agreement, and bare classifier definiteness (e.g. 隻狗 -> the dog).
"""

from typing import Dict, List, Optional
import json
import os

CLASSIFIER_NOUN_MAP = {
    "狗": "隻", "貓": "隻", "雞": "隻", "船": "隻", "碟": "隻", "手": "隻", "眼": "隻",
    "人": "個", "橙": "個", "蘋果": "個", "問題": "個", "諗法": "個", "電話": "個",
    "魚": "條", "路": "條", "褲": "條", "毛巾": "條", "河": "條",
    "衫": "件", "事": "件", "行李": "件", "外套": "件",
    "書": "本", "雜誌": "本", "字典": "本", "筆記": "本",
    "車": "架", "飛機": "架", "電腦": "架", "相機": "架",
    "屋": "間", "房": "間", "舖頭": "間", "茶餐廳": "間", "學校": "間", "公司": "間",
    "紙": "張", "枱": "張", "凳": "張", "床": "張", "飛": "張", "相": "張",
    "糖": "粒", "米": "粒", "藥": "粒", "掣": "粒"
}

def get_classifier_for_noun(noun: str) -> str:
    """Returns the canonical Cantonese classifier for a given noun, defaulting to '個'."""
    return CLASSIFIER_NOUN_MAP.get(noun, "個")

def parse_classifier_phrase(phrase: str) -> Dict[str, any]:
    """
    Parses a noun phrase to determine classifier structure:
    - Bare classifier definiteness: [CLF] + [NOUN] (e.g. 隻狗 -> definite 'the dog')
    - Quantified phrase: [NUM] + [CLF] + [NOUN] (e.g. 一條魚 -> indefinite 'a fish')
    - Demonstrative phrase: [DEM] + [CLF] + [NOUN] (e.g. 呢本書 -> 'this book')
    """
    dem_markers = ["呢", "嗰"]
    nums = ["一", "兩", "二", "三", "四", "五", "六", "七", "八", "九", "十", "幾"]
    clfs = ["個", "隻", "條", "件", "本", "架", "間", "張", "粒", "啲", "份", "杯", "碗", "碟", "部", "把"]
    
    # Check demonstrative
    if len(phrase) >= 2 and phrase[0] in dem_markers and phrase[1] in clfs:
        dem = phrase[0]
        clf = phrase[1]
        noun = phrase[2:]
        return {
            "phrase": phrase,
            "type": "demonstrative",
            "demonstrative": dem,
            "classifier": clf,
            "noun": noun,
            "is_definite": True,
            "english_gloss": f"{'this' if dem == '呢' else 'that'} {noun}"
        }
        
    # Check quantified
    if len(phrase) >= 2 and phrase[0] in nums and phrase[1] in clfs:
        num = phrase[0]
        clf = phrase[1]
        noun = phrase[2:]
        return {
            "phrase": phrase,
            "type": "quantified",
            "numeral": num,
            "classifier": clf,
            "noun": noun,
            "is_definite": False,
            "english_gloss": f"{num} {noun}"
        }
        
    # Check bare classifier definiteness [CLF] + [NOUN]
    if len(phrase) >= 2 and phrase[0] in clfs:
        clf = phrase[0]
        noun = phrase[1:]
        return {
            "phrase": phrase,
            "type": "bare_classifier_definite",
            "classifier": clf,
            "noun": noun,
            "is_definite": True,
            "english_gloss": f"the {noun} (bare-classifier definiteness)"
        }
        
    return {
        "phrase": phrase,
        "type": "unclassified_noun",
        "noun": phrase,
        "is_definite": False,
        "english_gloss": phrase
    }
