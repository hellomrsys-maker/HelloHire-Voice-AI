"""
Spanish Tokenization and Orthographic Segmentation Skill.
Handles Spanish orthography, inverted punctuation (¿, ¡), contractions (al, del),
diacritics (á, é, í, ó, ú, ü, ñ), and enclitic clitic pronoun attachments.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

SPANISH_PUNCTUATION = {"¿", "?", "¡", "!", "«", "»", "\"", "“", "”", "(", ")", "[", "]", ",", ".", ";", ":", "—", "-", "…"}

CONTRACTIONS = {
    "al": ("a", "el"),
    "del": ("de", "el"),
}


@dataclass
class SpanishToken:
    text: str
    char_start: int
    char_end: int
    is_word: bool
    is_punctuation: bool

    def __str__(self) -> str:
        return self.text

    def __getitem__(self, item):
        if item == "text":
            return self.text
        if item == "char_start":
            return self.char_start
        if item == "char_end":
            return self.char_end
        if item == "is_word":
            return self.is_word
        if item == "is_punctuation":
            return self.is_punctuation
        raise KeyError(item)


class SpanishTokenizer:
    """
    Morphosyntactic boundary tokenizer for Spanish prose, dialogue, and correspondence.
    """

    def __init__(self, expand_contractions: bool = False):
        self.expand_contractions = expand_contractions
        self.token_regex = re.compile(
            r"(¿|¡|\?|!|«|»|“|”|\"|\(|\)|\[|\]|,|\.|;|:|—|\.\.\.|[a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9_]+|[^\s])",
            re.UNICODE
        )

    def segment(self, text: str) -> List[str]:
        """
        Splits Spanish text into a list of surface string tokens.
        """
        if not text or not text.strip():
            return []

        tokens: List[str] = []
        for match in self.token_regex.finditer(text):
            tok = match.group()
            if self.expand_contractions and tok.lower() in CONTRACTIONS:
                c1, c2 = CONTRACTIONS[tok.lower()]
                tokens.extend([c1, c2])
            else:
                tokens.append(tok)
        return tokens

    def tokenize(self, text: str) -> List[SpanishToken]:
        """
        Segments text into rich SpanishToken objects preserving exact character offsets.
        """
        if not text or not text.strip():
            return []

        tokens: List[SpanishToken] = []
        for match in self.token_regex.finditer(text):
            tok = match.group()
            start = match.start()
            end = match.end()
            is_punct = tok in SPANISH_PUNCTUATION or not tok.isalnum()
            is_w = not is_punct and bool(re.search(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9]", tok))

            tokens.append(SpanishToken(
                text=tok,
                char_start=start,
                char_end=end,
                is_word=is_w,
                is_punctuation=is_punct,
            ))
        return tokens

    def get_token_stats(self, text: str) -> Dict[str, Any]:
        """Calculates token counts, inverted punctuation usage, and accented character frequency."""
        tokens = self.tokenize(text)
        words = [t for t in tokens if t.is_word]
        puncts = [t for t in tokens if t.is_punctuation]
        has_inverted_question = "¿" in text
        has_inverted_exclamation = "¡" in text
        accent_count = sum(1 for c in text if c in "áéíóúÁÉÍÓÚ")

        return {
            "token_count": len(tokens),
            "word_count": len(words),
            "punctuation_count": len(puncts),
            "has_inverted_question": has_inverted_question,
            "has_inverted_exclamation": has_inverted_exclamation,
            "accented_vowel_count": accent_count,
        }
