"""
Swahili Engine — Tokenization Skill
Handles sentence splitting and word tokenization, preserving Swahili apostrophes (e.g. ng'ombe, ng'aa).
"""

import re
from typing import List

SENTENCE_PATTERN = re.compile(r'(?<=[.!?])\s+')

def split_sentences(text: str) -> List[str]:
    """Split Swahili text into sentences by terminals (. ! ?)."""
    if not text:
        return []
    raw = SENTENCE_PATTERN.split(text.strip())
    return [s.strip() for s in raw if s.strip()]

def tokenize_words(text: str) -> List[str]:
    """
    Tokenize Swahili text into words, preserving internal apostrophes in words like 'ng'ombe'.
    """
    if not text:
        return []
    # Pattern matches words with optional apostrophes (ng'ombe), numbers, or punctuation
    tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", text)
    return tokens
