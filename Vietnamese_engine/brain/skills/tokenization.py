"""
Vietnamese Syllable & Compound Word Tokenizer
Handles Unicode NFC normalization, syllable segmentation, and compound word extraction.
"""

import re
import unicodedata
from typing import List, Dict, Any

# High-frequency multi-syllabic compound words (Từ ghép)
COMMON_COMPOUND_WORDS = {
    "học sinh", "sinh viên", "giáo viên", "bác sĩ", "thành phố",
    "quốc gia", "kinh tế", "đại học", "chính phủ", "gia đình",
    "bàn ghế", "quần áo", "nhà cửa", "xe đạp", "máy bay",
    "hoa hồng", "tiểu thuyết", "từ điển", "thời gian", "công việc",
    "phát triển", "nghiên cứu", "làm việc", "giúp đỡ", "cảm ơn"
}

class VietnameseTokenizer:
    """
    Tokenizes Vietnamese text into syllables or lexical compound words,
    enforcing standard Unicode NFC normalization.
    """

    def __init__(self):
        self.punct_pattern = re.compile(r'([,\.\?!;:«»\(\)\[\]"“”—])')

    def normalize_text(self, text: str) -> str:
        """Converts text to standard Unicode NFC (precomposed) format."""
        normalized = unicodedata.normalize("NFC", text)
        normalized = re.sub(r'[ \t\r\f\v]+', ' ', normalized)
        return normalized.strip()

    def tokenize_syllables(self, text: str) -> List[str]:
        """Splits Vietnamese text into individual orthographic syllables (tiếng)."""
        norm = self.normalize_text(text)
        spaced = self.punct_pattern.sub(r' \1 ', norm)
        return [t.strip() for t in spaced.split() if t.strip()]

    def tokenize_words(self, text: str) -> List[str]:
        """
        Tokenizes text by combining consecutive syllables that form recognized
        compound words (Từ ghép), falling back to individual syllables.
        """
        syllables = self.tokenize_syllables(text)
        words = []
        i = 0
        while i < len(syllables):
            # Check 2-syllable compound
            if i + 1 < len(syllables):
                two_syl = f"{syllables[i]} {syllables[i + 1]}".lower()
                if two_syl in COMMON_COMPOUND_WORDS:
                    # Preserve original case
                    words.append(f"{syllables[i]} {syllables[i + 1]}")
                    i += 2
                    continue
            words.append(syllables[i])
            i += 1
        return words

    def tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """Returns tokens with start/end character spans."""
        norm = self.normalize_text(text)
        words = self.tokenize_words(norm)
        results = []
        curr = 0
        for w in words:
            pos = norm.find(w, curr)
            if pos == -1:
                pos = curr
            end = pos + len(w)
            curr = end
            results.append({
                "token": w,
                "start": pos,
                "end": end,
                "is_compound": " " in w,
                "is_punct": bool(self.punct_pattern.match(w))
            })
        return results
