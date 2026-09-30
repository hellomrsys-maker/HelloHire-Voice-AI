"""
Arabic Engine — Tokenization Skill
Handles Arabic sentence boundary segmentation and word tokenization,
preserving Arabic punctuation marks (، ؛ ؟), diacritics, and stripping cosmetic tatweel (kashida).
"""

import re
from typing import List

SENTENCE_SPLIT_REGEX = re.compile(r'(?<=[.!?؟])\s+')
TATWEEL = '\u0640'

def strip_tatweel(text: str) -> str:
    """Remove cosmetic kashida/tatweel glyphs."""
    return text.replace(TATWEEL, "")

def split_sentences(text: str) -> List[str]:
    """Split Arabic text into individual sentences by punctuation (. ! ? ؟)."""
    if not text:
        return []
    cleaned = strip_tatweel(text.strip())
    raw = SENTENCE_SPLIT_REGEX.split(cleaned)
    return [s.strip() for s in raw if s.strip()]

def tokenize_words(text: str) -> List[str]:
    """
    Tokenize Arabic text into words and punctuation tokens.
    Preserves Arabic script glyphs, diacritics, and punctuation (، ؛ ؟).
    """
    if not text:
        return []
    cleaned = strip_tatweel(text)
    # Pattern matches Arabic/Latin words with optional hyphens (al-awlad) and apostrophes, numbers, or punctuation
    pattern = r"[\u0600-\u06FFa-zA-Z]+(?:'[\u0600-\u06FFa-zA-Z]+)?(?:-[\u0600-\u06FFa-zA-Z]+)*|\d+|[^\w\s\u0600-\u06FF]"
    tokens = re.findall(pattern, cleaned)
    return tokens

