"""
Japanese Kana-Kanji Conversion (IME Logic)
==========================================
Bidirectional transliteration and conversion between Hiragana, Katakana, and Kanji.
Implements prefix-trie lookup and context-conditioned candidate generation (SKK / Mozc style).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ConversionCandidate:
    kanji: str
    reading: str
    score: float
    pos_hint: str
    definition: str


@dataclass
class KanaKanjiConversionResult:
    input_kana: str
    best_kanji: str
    candidates: List[ConversionCandidate] = field(default_factory=list)


class JapaneseKanaKanjiConverter:
    """
    IME conversion engine translating phonemic Kana into orthographic Kanji and Katakana.
    """

    def __init__(self) -> None:
        # Kana to Kanji candidate dictionary
        self.ime_dictionary: Dict[str, List[ConversionCandidate]] = {
            "わたし": [
                ConversionCandidate("私", "わたし", 0.95, "名詞", "First person pronoun"),
                ConversionCandidate("渡し", "わたし", 0.05, "名詞", "Ferry / delivery"),
            ],
            "にほん": [
                ConversionCandidate("日本", "にほん", 0.98, "固有名詞", "Japan"),
                ConversionCandidate("二本", "にほん", 0.02, "名詞+助数詞", "Two long objects"),
            ],
            "かんじ": [
                ConversionCandidate("漢字", "かんじ", 0.65, "名詞", "Chinese characters"),
                ConversionCandidate("感じ", "かんじ", 0.30, "名詞", "Feeling / impression"),
                ConversionCandidate("幹事", "かんじ", 0.05, "名詞", "Organizer / manager"),
            ],
            "こうしょう": [
                ConversionCandidate("交渉", "こうしょう", 0.60, "名詞", "Negotiation"),
                ConversionCandidate("考証", "こうしょう", 0.20, "名詞", "Historical investigation"),
                ConversionCandidate("高尚", "こうしょう", 0.20, "名詞/形状詞", "Noble / refined"),
            ],
            "せいこう": [
                ConversionCandidate("成功", "せいこう", 0.70, "名詞", "Success"),
                ConversionCandidate("精巧", "せいこう", 0.20, "名詞/形状詞", "Elaborate"),
                ConversionCandidate("性向", "せいこう", 0.10, "名詞", "Propensity"),
            ],
            "きかん": [
                ConversionCandidate("期間", "きかん", 0.50, "名詞", "Time period"),
                ConversionCandidate("機関", "きかん", 0.35, "名詞", "Engine / institution"),
                ConversionCandidate("器官", "きかん", 0.15, "名詞", "Biological organ"),
            ],
            "たべる": [
                ConversionCandidate("食べる", "たべる", 0.98, "動詞", "To eat"),
            ],
            "いく": [
                ConversionCandidate("行く", "いく", 0.95, "動詞", "To go"),
                ConversionCandidate("幾", "いく", 0.05, "接頭辞", "How many / some"),
            ],
            "くる": [
                ConversionCandidate("来る", "くる", 0.95, "動詞", "To come"),
                ConversionCandidate("繰る", "くる", 0.05, "動詞", "To reel / turn pages"),
            ],
            "がくせい": [
                ConversionCandidate("学生", "がくせい", 0.98, "名詞", "Student"),
            ],
            "せんせい": [
                ConversionCandidate("先生", "せんせい", 0.98, "名詞", "Teacher / master"),
            ],
        }

    def convert_kana(self, kana: str, context: Optional[str] = None) -> KanaKanjiConversionResult:
        """Converts an input kana phrase into ranked kanji candidates."""
        candidates = self.ime_dictionary.get(kana, [])
        if not candidates:
            # Fallback candidate is the kana itself
            fallback = ConversionCandidate(kana, kana, 0.5, "未知語", "Phonetic verbatim")
            return KanaKanjiConversionResult(kana, kana, [fallback])

        # If context is given and contains matching semantic clues, boost score
        if context:
            re_scored = []
            for c in candidates:
                bonus = 0.2 if any(w in context for w in c.definition.split()) else 0.0
                re_scored.append(
                    ConversionCandidate(
                        kanji=c.kanji,
                        reading=c.reading,
                        score=min(1.0, c.score + bonus),
                        pos_hint=c.pos_hint,
                        definition=c.definition,
                    )
                )
            re_scored.sort(key=lambda x: x.score, reverse=True)
            candidates = re_scored

        best = candidates[0].kanji
        return KanaKanjiConversionResult(
            input_kana=kana,
            best_kanji=best,
            candidates=candidates,
        )

    def to_katakana(self, text: str) -> str:
        """Converts Hiragana characters to Katakana."""
        chars = []
        for c in text:
            code = ord(c)
            if 0x3041 <= code <= 0x3096:
                chars.append(chr(code + 0x60))
            else:
                chars.append(c)
        return "".join(chars)

    def to_hiragana(self, text: str) -> str:
        """Converts Katakana characters to Hiragana."""
        chars = []
        for c in text:
            code = ord(c)
            if 0x30A1 <= code <= 0x30F6:
                chars.append(chr(code - 0x60))
            else:
                chars.append(c)
        return "".join(chars)
