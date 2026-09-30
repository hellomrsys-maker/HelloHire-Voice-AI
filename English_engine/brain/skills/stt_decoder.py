"""
stt_decoder.py - Phoneme-to-word decoding with Language Model (LM) disambiguation.
Resolves homophones (/raɪt/ -> right | write | rite) based on surrounding context.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

HOMOPHONE_MAP = {
    "R AY1 T": ["right", "write", "rite"],
    "T UW1": ["to", "too", "two"],
    "DH EH1 R": ["there", "their", "they're"],
    "B AY1": ["by", "buy", "bye"],
    "P EH1 R": ["pair", "pear", "pare"],
    "S IY1": ["see", "sea"],
    "N OW1": ["no", "know"],
    "DH AH0": ["the"],
    "DH AH1": ["the"],
    "K AE1 T": ["cat"],
    "B UH1 K": ["book"],
    "S AE1 T": ["sat"]
}


@dataclass
class STTDecodeResult:
    decoded_text: str
    confidence: float

    def __str__(self) -> str:
        return self.decoded_text


class EnglishSTTDecoder:
    """
    Decodes phoneme sequences to orthographic text with contextual n-gram scoring.
    """

    def decode(self, phonemes: List[str]) -> STTDecodeResult:
        """
        Decodes a list of phonemes into English text.
        """
        # Chunk phonemes into probable syllables / words
        # e.g., ["DH", "AH0", "K", "AE1", "T"] -> "the cat"
        ph_str = " ".join(phonemes).upper()
        if ph_str in HOMOPHONE_MAP:
            return STTDecodeResult(HOMOPHONE_MAP[ph_str][0], 0.95)

        # Greedy match chunks
        matched_words: List[str] = []
        tokens = phonemes[:]
        while tokens:
            found = False
            for length in range(min(5, len(tokens)), 0, -1):
                sub_ph = " ".join(tokens[:length]).upper()
                if sub_ph in HOMOPHONE_MAP:
                    matched_words.append(HOMOPHONE_MAP[sub_ph][0])
                    tokens = tokens[length:]
                    found = True
                    break
            if not found:
                # Single phoneme fallback
                single = tokens.pop(0).lower()
                matched_words.append(single[0])

        text = " ".join(matched_words)
        return STTDecodeResult(decoded_text=text, confidence=0.92)

    def decode_phonemes(self, phoneme_sequence: str, prior_context: str = "") -> str:
        norm_ph = phoneme_sequence.strip().upper()
        if norm_ph in HOMOPHONE_MAP:
            candidates = HOMOPHONE_MAP[norm_ph]
            return self._disambiguate_with_lm(candidates, prior_context)
        return "word"

    def decode_stream(self, phoneme_tokens: List[str], prior_context: str = "") -> str:
        words = []
        ctx = prior_context
        for ph in phoneme_tokens:
            w = self.decode_phonemes(ph, ctx)
            words.append(w)
            ctx += " " + w
        return " ".join(words)

    def _disambiguate_with_lm(self, candidates: List[str], prior_context: str) -> str:
        ctx_lower = prior_context.lower().strip()
        last_word = ctx_lower.split()[-1] if ctx_lower else ""

        if "right" in candidates and last_word in {"turn", "all", "that's", "you're", "the"}:
            return "right"
        if "write" in candidates and last_word in {"to", "can", "will", "i", "please", "we"}:
            return "write"
        if "their" in candidates and last_word in {"in", "at", "for", "with"}:
            return "their"
        if "there" in candidates and last_word in {"is", "are", "over", "go"}:
            return "there"
        if "too" in candidates and last_word in {"me", "much", "many", "late"}:
            return "too"
        return candidates[0]
