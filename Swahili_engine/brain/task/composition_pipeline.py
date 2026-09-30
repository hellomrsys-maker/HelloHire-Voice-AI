"""
Swahili Engine — Composition & Style Task Pipeline
Assists in Swahili prose composition, Methali (proverb) analysis, reduplication, and dialect adaptation (Standard Kiunguja vs Sheng).
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words

METHALI_DATABASE = [
    "haraka haraka haina baraka",
    "pole pole ndio mwendo",
    "mcheza kwao hutuzwa",
    "asiyesikia la mkuu huvunjika guu",
    "akili ni mali",
    "haba na haba hujaza kibaba",
    "subira yavuta heri",
    "mchumia juani hulia kivulini",
    "kuishi kwingi ni kuona mengi",
    "umoja ni nguvu utengano ni udhaifu"
]

NAHAU_DATABASE = [
    "piga mbio", "kula njama", "vunja moyo", "fanya bidii",
    "shika njia", "kata shauri", "ona haya", "fungua roho"
]

REDUPLICATION_TERMS = {
    "haraka haraka", "pole pole", "mbalimbali", "kidogo kidogo",
    "mara kwa mara", "vizuri vizuri", "upesi upesi", "sawa sawa"
}

SHENG_TO_STANDARD = {
    "chapaa": "pesa",
    "morio": "rafiki",
    "msee": "mtu",
    "manzi": "msichana",
    "beste": "rafiki",
    "dawa": "pesa",
    "ndai": "gari"
}

STANDARD_TO_SHENG = {
    "pesa": "chapaa",
    "rafiki": "morio",
    "mtu": "msee",
    "msichana": "manzi",
    "gari": "ndai"
}

class SwahiliCompositionPipeline:
    """Pipeline for prose style, proverb integration, and dialect adaptation."""

    def __init__(self):
        pass

    def adapt_dialect(self, text: str, target: str = "standard") -> str:
        """
        Adapt text between Sheng youth vernacular and Standard Kiunguja Swahili.
        """
        adapted = text
        text_lower = text.lower()
        if target.lower() == "standard":
            for sheng, std in SHENG_TO_STANDARD.items():
                if sheng in text_lower:
                    adapted = adapted.replace(sheng, std)
        elif target.lower() == "sheng":
            for std, sheng in STANDARD_TO_SHENG.items():
                if std in text_lower:
                    adapted = adapted.replace(std, sheng)
        return adapted

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary style, proverb density, idioms, and reduplication."""
        tokens = tokenize_words(text)
        text_lower = text.lower()
        
        proverbs_found = [p for p in METHALI_DATABASE if p in text_lower]
        idioms_found = [n for n in NAHAU_DATABASE if n in text_lower]
        reduplications_found = [r for r in REDUPLICATION_TERMS if r in text_lower]
        sheng_found = [s for s in SHENG_TO_STANDARD.keys() if s in text_lower]
        
        if proverbs_found:
            style = "proverbial_bantu"
        elif sheng_found:
            style = "sheng_vernacular"
        elif idioms_found or reduplications_found:
            style = "idiomatic_expressive"
        else:
            style = "standard"
            
        return {
            "token_count": len(tokens),
            "proverbs": proverbs_found,
            "proverb_count": len(proverbs_found),
            "idioms": idioms_found,
            "idiom_count": len(idioms_found),
            "reduplications": reduplications_found,
            "sheng_terms": sheng_found,
            "style": style
        }
