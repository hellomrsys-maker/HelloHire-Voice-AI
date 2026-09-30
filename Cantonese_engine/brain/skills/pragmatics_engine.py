"""
Cantonese Pragmatics and Diglossic Register Engine.
Audits diglossic levels:
- Spoken Cantonese (口語 Hau2 Jyu5)
- Standard Written Chinese (書面語 Syu1 Min6 Jyu5)
Provides business epistolary formulas and register alignment.
"""

from typing import Dict, List, Optional

COLLOQUIAL_MARKERS = {
    "喺", "嘅", "咗", "緊", "畀", "諗", "睇", "食", "飲", "佢", "佢哋", "我哋", "你哋",
    "乜", "乜嘢", "點樣", "點解", "點算", "冇", "唔", "咪", "未", "搞掂", "行先", "買嘢",
    "喇", "啦", "呀", "㗎", "啫", "喎", "囉", "添", "咩", "咋"
}

FORMAL_MARKERS = {
    "在", "的", "了", "正在", "給", "想", "看", "吃", "喝", "他", "他們", "我們", "你們",
    "甚麼", "什麼", "怎樣", "為何", "如何", "沒有", "不", "非", "未曾", "完成", "先行", "購物",
    "台鑒", "此致", "敬禮", "閣下", "鈞安"
}

def detect_register(text: str) -> Dict[str, any]:
    """
    Evaluates text to classify register as Colloquial Cantonese (Hau2 Jyu5)
    or Formal Written Chinese (Syu1 Min6 Jyu5).
    """
    colloquial_hits = [m for m in COLLOQUIAL_MARKERS if m in text]
    formal_hits = [m for m in FORMAL_MARKERS if m in text]
    
    colloquial_score = len(colloquial_hits)
    formal_score = len(formal_hits)
    
    if colloquial_score > formal_score:
        register = "colloquial_cantonese"
        tier_code = 1
        description = "口語 (Hau2 Jyu5) - Spoken Cantonese"
    elif formal_score > colloquial_score:
        register = "formal_written"
        tier_code = 2
        description = "書面語 (Syu1 Min6 Jyu5) - Standard Written Chinese"
    else:
        register = "hybrid_or_neutral"
        tier_code = 1 if colloquial_score > 0 else 0
        description = "中性 / 混合 (Neutral / Hybrid)"
        
    return {
        "register": register,
        "tier_code": tier_code,
        "description": description,
        "colloquial_score": colloquial_score,
        "formal_score": formal_score,
        "colloquial_markers_found": colloquial_hits,
        "formal_markers_found": formal_hits
    }

def compose_email(recipient: str, subject: str, message: str, register: str = "formal") -> str:
    """
    Generates a structured email according to Cantonese / Hong Kong epistolary conventions.
    """
    if register == "formal":
        salutation = f"{recipient} 閣下 / 執事先生："
        closing = "祝\n工作順利，身體健康。\n\n此致\n敬禮"
        body = message
    else:
        salutation = f"Hi {recipient} / 喂 {recipient}："
        closing = "唔該晒！\n下次再傾！"
        body = message
        
    return f"【電郵主旨】: {subject}\n\n{salutation}\n\n{body}\n\n{closing}"
