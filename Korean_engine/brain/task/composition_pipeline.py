"""
Korean Engine — Composition & Style Task Pipeline
Assists in Korean prose composition, North-South dialectal adaptation, and ideophone analysis.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_eojeol
from ..skills.speech_level_engine import classify_speech_level

IDEOPHONES_COMMON = {
    "반짝반짝", "번쩍번쩍", "살금살금", "엉금엉금", "알록달록", "얼룩덜룩",
    "두근두근", "콩닥콩닥", "펄럭펄럭", "살랑살랑", "줄줄", "졸졸"
}

# Common South Korean head consonant changes (두음법칙): SK -> NK
NORTH_KOREAN_DU_EUM = {
    "노동": "로동",
    "이성": "리성",
    "여자": "녀자",
    "역사": "력사",
    "이론": "리론",
    "연습": "련습"
}

SOUTH_KOREAN_DU_EUM = {v: k for k, v in NORTH_KOREAN_DU_EUM.items()}

class KoreanCompositionPipeline:
    """Pipeline for prose style analysis and orthographic dialect adaptation."""

    def __init__(self):
        pass

    def adapt_orthography(self, text: str, target_standard: str = "south") -> str:
        """
        Adapt text between South Korean (두음법칙 적용) and North Korean (두음법칙 미적용) orthography.
        """
        adapted = text
        if target_standard.lower() == "north":
            for sk, nk in NORTH_KOREAN_DU_EUM.items():
                adapted = adapted.replace(sk, nk)
        elif target_standard.lower() == "south":
            for nk, sk in SOUTH_KOREAN_DU_EUM.items():
                adapted = adapted.replace(nk, sk)
        return adapted

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze textual style, ideophones, and clausal profile."""
        tokens = tokenize_eojeol(text)
        ideophones_found = [t for t in tokens if t in IDEOPHONES_COMMON]
        speech_level = classify_speech_level(text)
        
        return {
            "token_count": len(tokens),
            "speech_level": speech_level["level"],
            "ideophones": ideophones_found,
            "ideophone_count": len(ideophones_found),
            "style": "expressive" if len(ideophones_found) > 0 else "standard"
        }
