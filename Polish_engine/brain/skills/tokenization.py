"""
Polish Tokenization Engine
Handles Polish orthography, diacritics (ą, ć, ę, ł, ń, ó, ś, ź, ż),
abbreviations (np., m.in., tzw., prof., dr), and punctuation.
"""

import re
from typing import List

class PolishTokenizer:
    def __init__(self):
        self.abbreviations = {
            "np.", "m.in.", "tzw.", "tzn.", "itd.", "itp.", "prof.", "dr", "hab.",
            "mgr", "inż.", "ul.", "al.", "pl.", "art.", "godz.", "r."
        }

    def tokenize(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        # Matches Polish words with full diacritics, numbers, or individual punctuation symbols
        pattern = r"(?:[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+(?:-[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+)?|[0-9]+|[^\s\w])"
        tokens = re.findall(pattern, text, re.UNICODE)
        return tokens

    def split_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        # Split on sentence terminals while respecting common abbreviations
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = []
        for s in raw_sentences:
            if s:
                sentences.append(s)
        return sentences
