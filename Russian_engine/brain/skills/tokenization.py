"""Russian Tokenizer Skill.

Handles Cyrillic orthography, punctuation, and Russian compound hyphenated particles
such as 'кое-', '-то', '-либо', '-нибудь', 'из-за', 'из-под', 'по-русски'.
"""

import re
from typing import List, Dict, Any


class RussianTokenizer:
    # Pattern for hyphenated Russian particles and compounds
    HYPHENATED_COMPOUND = re.compile(
        r"^(?:кое-\w+|\w+-(?:то|либо|нибудь|таки|ка)|из-(?:за|под)|по-\w+)$",
        re.IGNORECASE
    )
    
    # Word token pattern matching Cyrillic words with optional internal hyphen
    WORD_PATTERN = re.compile(
        r"[а-яёА-ЯЁ]+(?:-[а-яёА-ЯЁ]+)*|\d+(?:[.,]\d+)?|[^\s\w]",
        re.UNICODE
    )
    
    SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯЁ])")

    def __init__(self):
        pass

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes Russian text into words, hyphenated compounds, and punctuation."""
        if not text:
            return []
        tokens = self.WORD_PATTERN.findall(text)
        return tokens

    def split_sentences(self, text: str) -> List[str]:
        """Splits Russian text into sentences."""
        if not text.strip():
            return []
        raw_sents = self.SENTENCE_SPLIT_PATTERN.split(text.strip())
        return [s.strip() for s in raw_sents if s.strip()]

    def analyze_tokens(self, text: str) -> List[Dict[str, Any]]:
        """Produces token metadata including Cyrillic character flags and hyphenation types."""
        tokens = self.tokenize(text)
        results = []
        for idx, tok in enumerate(tokens):
            is_cyrillic = bool(re.search(r"[а-яёА-ЯЁ]", tok))
            is_hyphenated = bool("-" in tok and is_cyrillic)
            is_punct = bool(re.match(r"^[^\w\s]+$", tok))
            is_num = bool(re.match(r"^\d+(?:[.,]\d+)?$", tok))
            results.append({
                "index": idx,
                "text": tok,
                "is_cyrillic": is_cyrillic,
                "is_hyphenated_compound": is_hyphenated,
                "is_punct": is_punct,
                "is_num": is_num,
                "length": len(tok)
            })
        return results
