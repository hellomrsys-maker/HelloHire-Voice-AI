"""
French Tokenization Skill.
Handles French orthography, contractions, apostrophe elisions (l', d', j', c', qu'),
hyphenated pronominal inversions, and French quotation marks («, »).
"""

import re
from typing import List, Tuple, Dict, Any


class FrenchTokenizer:
    """
    Advanced rule-based tokenizer for French supporting elision splitting,
    hyphenated clitics, and character span tracking.
    """

    # Elision prefixes that detach from subsequent word
    ELISION_PREFIXES = {
        "l'", "d'", "c'", "j'", "m'", "t'", "s'", "n'", "qu'", "jusqu'", "lorsqu'", "puisqu'"
    }

    PUNCTUATION_PATTERN = re.compile(
        r"([«»\"'“”„`\(\)\[\]\{\},;:!\?\.\—\–\-])"
    )

    def __init__(self):
        pass

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes French text, splitting on whitespace and separating punctuation,
        while isolating elided prefixes (e.g. "l'arbre" -> ["l'", "arbre"]).
        """
        raw_tokens = text.strip().split()
        tokens: List[str] = []

        for raw in raw_tokens:
            low = raw.lower()

            # Check for elision prefix
            elision_matched = False
            for prefix in sorted(self.ELISION_PREFIXES, key=len, reverse=True):
                if low.startswith(prefix) and len(raw) > len(prefix):
                    pref_actual = raw[:len(prefix)]
                    remainder = raw[len(prefix):]
                    tokens.append(pref_actual)
                    # Process remainder
                    sub_toks = self._tokenize_word_and_punct(remainder)
                    tokens.extend(sub_toks)
                    elision_matched = True
                    break

            if not elision_matched:
                sub_toks = self._tokenize_word_and_punct(raw)
                tokens.extend(sub_toks)

        return tokens

    def _tokenize_word_and_punct(self, word: str) -> List[str]:
        """Separates boundary and interior punctuation except interior hyphens if desired."""
        # Split preserving French punctuation
        parts = re.split(r"([«»\"„\(\)\[\]\{\},;:!\?\.\—\–])", word)
        res = [p for p in parts if p]
        return res

    def get_token_spans(self, text: str) -> List[Tuple[str, int, int]]:
        """Returns list of (token, start_char, end_char) tuples."""
        tokens = self.tokenize(text)
        spans: List[Tuple[str, int, int]] = []
        cursor = 0
        for tok in tokens:
            idx = text.find(tok, cursor)
            if idx != -1:
                spans.append((tok, idx, idx + len(tok)))
                cursor = idx + len(tok)
            else:
                spans.append((tok, cursor, cursor + len(tok)))
                cursor += len(tok)
        return spans
