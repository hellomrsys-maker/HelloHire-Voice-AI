"""
Tamil parity translation task. Implements English-FIRST translation:
Tamil -> English via the shared English-pivot comprehension layer, and a
reverse English -> Tamil gloss using the profile lexicon.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from engine_common.english_pivot import EnglishPivotComprehension
from engine_common.language_profile import get_profile


@dataclass
class TamilTranslationResult:
    source_text: str
    target_language: str
    translated_text: str
    english_pivot_text: str
    confidence: float


class TamilParityTranslator:
    def __init__(self) -> None:
        self.profile = get_profile("Tamil_engine")
        self.pivot = EnglishPivotComprehension(self.profile)
        self._en_to_native = {v: k for k, v in self.profile.to_english_lexicon.items() if v}

    def to_english(self, text: str) -> TamilTranslationResult:
        res = self.pivot.comprehend(text)
        return TamilTranslationResult(
            source_text=text, target_language="en",
            translated_text=res.canonical_english_order or res.english_projection,
            english_pivot_text=res.english_projection,
            confidence=res.comprehension_confidence,
        )

    def from_english(self, english_text: str) -> TamilTranslationResult:
        words: List[str] = []
        for w in english_text.replace(".", " ").split():
            words.append(self._en_to_native.get(w.lower(), w))
        return TamilTranslationResult(
            source_text=english_text, target_language="ta",
            translated_text=" ".join(words), english_pivot_text=english_text,
            confidence=0.75,
        )

    def translate(self, text: str, target_lang: str = "en") -> TamilTranslationResult:
        return self.to_english(text) if target_lang == "en" else self.from_english(text)
