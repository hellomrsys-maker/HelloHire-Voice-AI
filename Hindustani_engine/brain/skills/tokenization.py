"""
Hindustani Tokenization Skill.
Tokenizes Devanagari script (Hindi), Perso-Arabic script (Urdu), and Romanized Hindustani (Hinglish/ITRANS).
Supports danda punctuation (| and ||), virama clusters, nukta, and postpositional segmentation.
"""

import re
from typing import List, Tuple, Dict, Any


class HindustaniTokenizer:
    """
    Advanced multi-script tokenizer for Hindustani language text.
    """

    # Punctuation including Devanagari danda and Western symbols
    PUNCT_PATTERN = re.compile(
        r"([।॥\.,;:!\?\"'«»\(\)\[\]\{\}\—\–\-])"
    )

    # Common fused postpositions in Romanized and Devanagari
    FUSED_PRONOUN_ERGATIVE = {
        "maine": ("main", "ne"), "मैंने": ("मैं", "ने"),
        "tune": ("tu", "ne"), "तूने": ("तू", "ने"),
        "usne": ("us", "ne"), "उसने": ("उस", "ने"),
        "isne": ("is", "ne"), "इसने": ("इस", "ने"),
        "humne": ("hum", "ne"), "हमने": ("हम", "ने"),
        "tumne": ("tum", "ne"), "तुमने": ("तुम", "ने"),
        "aapne": ("aap", "ne"), "आपने": ("आप", "ने"),
        "unhonne": ("un", "ne"), "उन्होंने": ("उन्होंने", "ने"),
        "inhonne": ("in", "ne"), "इन्होंने": ("इन्होंने", "ने"),
    }

    def tokenize(self, text: str, split_fused_ergative: bool = False) -> List[str]:
        """
        Tokenizes text into word and punctuation tokens.
        If split_fused_ergative is True, splits words like 'maine' into ['main', 'ne'].
        """
        raw_words = text.strip().split()
        tokens: List[str] = []

        for word in raw_words:
            # Separate punctuation
            parts = [p for p in self.PUNCT_PATTERN.split(word) if p]
            for part in parts:
                low = part.lower()
                if split_fused_ergative and low in self.FUSED_PRONOUN_ERGATIVE:
                    base, post = self.FUSED_PRONOUN_ERGATIVE[low]
                    tokens.append(base)
                    tokens.append(post)
                else:
                    tokens.append(part)

        return tokens

    def get_token_spans(self, text: str) -> List[Tuple[str, int, int]]:
        """Returns list of (token, start_char, end_char) tuples."""
        tokens = self.tokenize(text, split_fused_ergative=False)
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
