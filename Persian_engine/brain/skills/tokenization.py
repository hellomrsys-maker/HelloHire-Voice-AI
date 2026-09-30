"""
Persian Tokenizer & Script Normalization Engine
Handles Perso-Arabic RTL orthography, ZWNJ (نیم‌فاصله \u200c), and clitic boundaries.
"""

import re
from typing import List, Dict, Any

# Unicode character normalizations: Arabic variants to Persian standards
ARABIC_TO_PERSIAN_CHARS = {
    '\u0643': '\u06A9',  # Arabic Kaf -> Persian Keheh (ک)
    '\u0649': '\u06CC',  # Arabic Alef Maksura -> Persian Yeh (ی)
    '\u064A': '\u06CC',  # Arabic Yeh -> Persian Yeh (ی)
    '\u0629': '\u0647',  # Teh Marbuta -> Heh (ه)
    '\u0640': '',        # Tatweel/Kashida -> remove
}

ZWNJ = '\u200C'  # Zero-Width Non-Joiner

class PersianTokenizer:
    """
    Robust Persian morphological boundary tokenizer supporting ZWNJ preservation,
    Perso-Arabic unicode normalization, and enclitic handling.
    """
    
    def __init__(self):
        # Persian punctuation
        self.punct_pattern = re.compile(r'([،؛؟!«»\.\:\(\)\[\]])')
        
    def normalize_script(self, text: str) -> str:
        """Normalizes Arabic character variants to standard Persian Unicode codepoints."""
        result = []
        for ch in text:
            result.append(ARABIC_TO_PERSIAN_CHARS.get(ch, ch))
        normalized = "".join(result)
        # Standardize multiple spaces but keep ZWNJ
        normalized = re.sub(r'[ \t\r\f\v]+', ' ', normalized)
        return normalized.strip()

    def tokenize_words(self, text: str) -> List[str]:
        """Tokenizes Persian text into words, preserving internal ZWNJ boundaries."""
        normalized = self.normalize_script(text)
        # Pad punctuation with spaces
        spaced = self.punct_pattern.sub(r' \1 ', normalized)
        # Split on regular whitespace
        tokens = [t.strip() for t in spaced.split() if t.strip()]
        return tokens

    def tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """Returns tokens with start/end character offsets and morphological flags."""
        tokens = self.tokenize_words(text)
        results = []
        current_idx = 0
        for tok in tokens:
            pos = text.find(tok, current_idx)
            if pos == -1:
                pos = current_idx
            end = pos + len(tok)
            current_idx = end
            
            has_zwnj = ZWNJ in tok
            is_punct = bool(self.punct_pattern.match(tok))
            
            results.append({
                "token": tok,
                "start": pos,
                "end": end,
                "has_zwnj": has_zwnj,
                "is_punct": is_punct
            })
        return results

    def split_prefix_morphemes(self, word: str) -> List[str]:
        """Separates prefixes like mi- (می‌) or be- (بـ) if attached via ZWNJ."""
        if ZWNJ in word:
            parts = word.split(ZWNJ)
            return [p for p in parts if p]
        return [word]
