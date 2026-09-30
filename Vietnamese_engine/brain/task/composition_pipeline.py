"""
Vietnamese Composition Task Pipeline
Synthesizes styled Vietnamese prose, adapts regional vocabulary, and enriches
text with classical Thành ngữ (four-syllable idioms).
"""

from typing import Dict, Any, List, Optional
import re

VIETNAMESE_PROVERBS = [
    {
        "proverb": "Nước chảy đá mòn",
        "theme": "perseverance",
        "meaning": "Constant persistence overcomes the hardest obstacle."
    },
    {
        "proverb": "Uống nước nhớ nguồn",
        "theme": "gratitude",
        "meaning": "When drinking water, remember the source."
    },
    {
        "proverb": "Ăn quả nhớ kẻ trồng cây",
        "theme": "loyalty",
        "meaning": "When eating fruit, remember who planted the tree."
    },
    {
        "proverb": "Đi một ngày đàng học một sàng khôn",
        "theme": "travel_wisdom",
        "meaning": "Travel broadens the mind."
    }
]

# Southern to Northern standard vocabulary mapping
SOUTHERN_TO_NORTHERN = {
    "ly": "cốc",
    "muỗng": "thìa",
    "trái": "quả",
    "heo": "lợn",
    "nón": "mũ",
    "bông": "hoa",
    "dù": "ô",
    "hột": "hạt"
}

class VietnameseCompositionPipeline:
    """
    Styled prose composition, dialect adaptation, and literary idiom enrichment.
    """

    def adapt_southern_to_northern_standard(self, text: str) -> str:
        """Normalizes Southern regional vocabulary to Standard Northern literary norms."""
        words = text.split()
        adapted = []
        for w in words:
            clean = re.sub(r'[,.\?!;:«»"]', '', w).lower()
            punct = w.replace(clean, '')
            if clean in SOUTHERN_TO_NORTHERN:
                replacement = SOUTHERN_TO_NORTHERN[clean]
                adapted.append(f"{replacement}{punct}")
            else:
                adapted.append(w)
        return " ".join(adapted)

    def inject_thanh_ngu(self, text: str, theme: str) -> str:
        """Enriches prose by embedding a classical 4-syllable idiom matching a theme."""
        matched = [p for p in VIETNAMESE_PROVERBS if p["theme"] == theme]
        if matched:
            proverb = matched[0]["proverb"]
            return f"{text.strip()} Như ông cha ta thường dạy: «{proverb}»."
        return text
