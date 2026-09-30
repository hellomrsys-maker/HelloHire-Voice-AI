"""
Cantonese Diglossic Drift Cognitive Analyzer.
Audits spoken vs written register, flagging unnatural Mandarin intrusions in spoken Cantonese.
"""

from typing import Dict, List
from Cantonese_engine.brain.skills.pragmatics_engine import detect_register

MANDARIN_TO_CANTONESE_MAP = {
    "看": "睇",
    "吃": "食",
    "喝": "飲",
    "想": "諗",
    "說": "講",
    "在": "喺",
    "的": "嘅",
    "他": "佢",
    "他們": "佢哋",
    "我們": "我哋",
    "你們": "你哋",
    "甚麼": "乜嘢",
    "什麼": "乜嘢",
    "怎樣": "點樣",
    "沒有": "冇",
    "不": "唔",
    "給": "畀",
    "先行": "行先"
}

class DiglossicDriftAnalyzer:
    """
    Detects cross-register drift between spoken Cantonese and written Chinese.
    """
    def __init__(self):
        self.name = "Cantonese Diglossic Drift Analyzer"

    def analyze(self, text: str, target_register: str = "colloquial") -> Dict[str, any]:
        reg_info = detect_register(text)
        current_reg = reg_info["register"]
        
        drift_warnings = []
        conversions = {}
        
        if target_register == "colloquial":
            for m_word, c_word in MANDARIN_TO_CANTONESE_MAP.items():
                if m_word in text:
                    drift_warnings.append(f"Mandarin/Formal word '{m_word}' detected; recommend Cantonese colloquial '{c_word}'")
                    conversions[m_word] = c_word
                    
        is_aligned = len(drift_warnings) == 0
        drift_score = 1.0 - (min(len(drift_warnings), 5) * 0.15)
        
        return {
            "text": text,
            "target_register": target_register,
            "detected_register": current_reg,
            "tier_code": reg_info["tier_code"],
            "is_register_aligned": is_aligned,
            "drift_warnings": drift_warnings,
            "conversions": conversions,
            "register_score": max(0.0, drift_score)
        }
