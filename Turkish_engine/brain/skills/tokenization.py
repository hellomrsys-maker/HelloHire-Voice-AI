"""Turkish Tokenizer Skill.

Handles Turkish orthography, dotted/dotless I (i/İ, ı/I) locale casing,
and apostrophe-separated proper noun inflection (e.g. 'Ahmet'in', 'Türkiye'de').
"""

import re
from typing import List, Dict, Any, Tuple


class TurkishTokenizer:
    # Pattern matching words with optional apostrophes for proper nouns, or punctuation/numbers
    WORD_PATTERN = re.compile(
        r"[abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ]+(?:'[abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ]+)?|\d+(?:[.,]\d+)?|[^\s\w]",
        re.UNICODE
    )

    SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ])")

    @staticmethod
    def turkish_lower(text: str) -> str:
        """Locale-aware Turkish lowercasing preserving dotted and dotless I."""
        result = []
        for char in text:
            if char == "İ":
                result.append("i")
            elif char == "I":
                result.append("ı")
            else:
                result.append(char.lower())
        return "".join(result)

    @staticmethod
    def turkish_upper(text: str) -> str:
        """Locale-aware Turkish uppercasing preserving dotted and dotless I."""
        result = []
        for char in text:
            if char == "i":
                result.append("İ")
            elif char == "ı":
                result.append("I")
            else:
                result.append(char.upper())
        return "".join(result)

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes Turkish text preserving apostrophe-bound inflectional suffixes."""
        if not text:
            return []
        return self.WORD_PATTERN.findall(text)

    def split_sentences(self, text: str) -> List[str]:
        """Splits Turkish text into sentences."""
        if not text.strip():
            return []
        raw_sents = self.SENTENCE_SPLIT_PATTERN.split(text.strip())
        return [s.strip() for s in raw_sents if s.strip()]

    def split_apostrophe(self, token: str) -> Tuple[str, str]:
        """Separates stem and suffix if token contains an apostrophe (e.g., 'Ankara'ya' -> ('Ankara', 'ya'))."""
        if "'" in token:
            parts = token.split("'", 1)
            return parts[0], parts[1]
        return token, ""

    def analyze_tokens(self, text: str) -> List[Dict[str, Any]]:
        """Produces token metadata including proper noun apostrophe detection."""
        tokens = self.tokenize(text)
        results = []
        for idx, tok in enumerate(tokens):
            has_apostrophe = "'" in tok
            stem, suffix = self.split_apostrophe(tok)
            is_punct = bool(re.match(r"^[^\w\s]+$", tok))
            is_num = bool(re.match(r"^\d+(?:[.,]\d+)?$", tok))
            results.append({
                "index": idx,
                "token": tok,
                "has_apostrophe": has_apostrophe,
                "stem": stem,
                "suffix": suffix,
                "is_punct": is_punct,
                "is_num": is_num,
                "length": len(tok)
            })
        return results
