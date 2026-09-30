"""
Korean Engine — Tokenization Skill
Handles sentence splitting, Eojeol (word) tokenization, and punctuation separation.
"""

import re
from typing import List, Dict, Any

SENTENCE_DELIMITERS = re.compile(r'(?<=[.!?])\s+')

def split_sentences(text: str) -> List[str]:
    """Split Korean text into sentences by terminals (. ! ?)."""
    if not text:
        return []
    raw = SENTENCE_DELIMITERS.split(text.strip())
    return [s.strip() for s in raw if s.strip()]

def tokenize_eojeol(sentence: str) -> List[str]:
    """Tokenize a Korean sentence into Eojeol (space-delimited word tokens)."""
    if not sentence:
        return []
    # Match Hangul clusters, alphanumeric, and punctuation
    tokens = re.findall(r'[가-힣]+|[A-Za-z0-9]+|[^\s\w]', sentence)
    return tokens
