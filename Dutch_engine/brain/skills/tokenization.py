"""
Dutch Tokenization Engine
Handles standard Dutch orthography, contractions ('s morgens, 't, z'n, m'n), and punctuation.
"""

import re
from typing import List, Dict, Any

class DutchTokenizer:
    def __init__(self):
        # Contraction patterns and split tokens
        self.clitics = {
            "'s": "des",
            "'t": "het",
            "z'n": "zijn",
            "m'n": "mijn",
            "d'r": "haar",
            "je": "je"
        }

    def tokenize(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        # Preserve Dutch apostrophe contractions while tokenizing punctuation
        # Matches words with leading or internal apostrophe, or standard words, or punctuation
        pattern = r"(?:'[a-zA-Z]+|[a-zA-Z]+'[a-zA-Z]+|[a-zA-Z]+|[0-9]+|[^\s\w])"
        tokens = re.findall(pattern, text, re.UNICODE)
        return tokens

    def split_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s for s in sentences if s]
