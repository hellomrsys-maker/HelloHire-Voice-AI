"""
Bengali Tokenizer: Handles Unicode normalization, Bengali Dā̃ṛi (।),
punctuation separation, character span tracking, and enclitic classifier detachment.
"""

from typing import List, Dict, Any, Tuple
import re
import unicodedata


class BengaliTokenizer:
    """
    Tokenizer for Bengali script and romanized text.
    Handles enclitics, case inflections, and punctuation boundaries.
    """

    BENGALI_DARI = "।"
    BENGALI_DOUBLE_DARI = "॥"
    CLASSIFIERS = ["খানা", "খানি", "গুলো", "গুলি", "টা", "টি", "জন"]
    CASE_SUFFIXES = ["কে", "ের", "র", "তে", "ে", "য়"]

    def __init__(self):
        self.punct_pattern = re.compile(r"([।॥,\.!?;:\"'()\[\]{}—])")

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes input text into a clean list of lexical tokens.
        """
        if not text:
            return []
        
        # Normalize Unicode NFC
        normalized = unicodedata.normalize("NFC", text.strip())
        
        # Space out punctuation including Bengali dari
        spaced = self.punct_pattern.sub(r" \1 ", normalized)
        tokens = [t for t in spaced.split() if t]
        return tokens

    def tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """
        Tokenizes text while tracking start and end character offsets.
        """
        if not text:
            return []

        normalized = unicodedata.normalize("NFC", text)
        tokens = self.tokenize(normalized)
        spans = []
        current_idx = 0

        for token in tokens:
            idx = normalized.find(token, current_idx)
            if idx != -1:
                start = idx
                end = idx + len(token)
                current_idx = end
            else:
                start = current_idx
                end = current_idx + len(token)
            spans.append({
                "token": token,
                "start": start,
                "end": end
            })
        return spans

    def split_classifier(self, token: str) -> Tuple[str, str | None]:
        """
        Splits a nominal token into base stem and bound classifier if present.
        Example: 'বইটা' -> ('বই', 'টা'), 'ছাত্রজন' -> ('ছাত্র', 'জন')
        """
        for clf in self.CLASSIFIERS:
            if token.endswith(clf) and len(token) > len(clf):
                return token[:-len(clf)], clf
        return token, None

    def split_case_suffix(self, token: str) -> Tuple[str, str | None]:
        """
        Splits an inflected noun into stem and case marker if present.
        Example: 'ছেলেকে' -> ('ছেলে', 'কে'), 'বইয়ের' -> ('বই', 'ের')
        """
        for sfx in self.CASE_SUFFIXES:
            if token.endswith(sfx) and len(token) > len(sfx):
                return token[:-len(sfx)], sfx
        return token, None
