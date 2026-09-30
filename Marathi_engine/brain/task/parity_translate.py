"""
Marathi parity translation task. Implements English-FIRST translation:
Marathi -> English via the shared English-pivot comprehension layer, and a
reverse English -> Marathi gloss using the profile lexicon.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from engine_common.english_pivot import EnglishPivotComprehension
from engine_common.language_profile import get_profile


@dataclass
class MarathiTranslationResult:
    source_text: str
    target_language: str
    translated_text: str
    english_pivot_text: str
    confidence: float


class MarathiParityTranslator:
    def __init__(self) -> None:
        self.profile = get_profile("Marathi_engine")
        self.pivot = EnglishPivotComprehension(self.profile)
        self._en_to_native = {v: k for k, v in self.profile.to_english_lexicon.items() if v}

    def to_english(self, text: str) -> MarathiTranslationResult:
        res = self.pivot.comprehend(text)
        return MarathiTranslationResult(
            source_text=text, target_language="en",
            translated_text=res.canonical_english_order or res.english_projection,
            english_pivot_text=res.english_projection,
            confidence=res.comprehension_confidence,
        )

    def from_english(self, english_text: str) -> MarathiTranslationResult:
        words: List[str] = []
        for w in english_text.replace(".", " ").split():
            words.append(self._en_to_native.get(w.lower(), w))
        return MarathiTranslationResult(
            source_text=english_text, target_language="mr",
            translated_text=" ".join(words), english_pivot_text=english_text,
            confidence=0.75,
        )

    def translate(self, text: str, target_lang: str = "en") -> MarathiTranslationResult:
        return self.to_english(text) if target_lang == "en" else self.from_english(text)
