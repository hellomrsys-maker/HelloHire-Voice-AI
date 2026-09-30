"""
Japanese Reading Generation (Furigana / Ruby Annotations)
=========================================================
Transforms Kanji orthography into Kana readings (Hiragana and Katakana)
with character-level alignment for ruby rendering and pronunciation lookup.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer


@dataclass
class RubyAnnotation:
    kanji_surface: str
    hiragana_reading: str
    katakana_reading: str
    start_char: int
    end_char: int
    html_ruby: str


@dataclass
class ReadingGenerationResult:
    original_text: str
    annotated_html: str
    hiragana_stream: str
    katakana_stream: str
    annotations: List[RubyAnnotation] = field(default_factory=list)


class JapaneseReadingGenerator:
    """
    Generates Furigana readings for Kanji words and compound expressions.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()

        # Core Kanji-to-Reading dictionary
        self.kanji_reading_dict: Dict[str, str] = {
            "漢字": "かんじ", "日本": "にほん", "私": "わたし", "僕": "ぼく", "俺": "おれ",
            "彼": "かれ", "彼女": "かのじょ", "先生": "せんせい", "学生": "がくせい",
            "学校": "がっこう", "大学": "だいがく", "勉強": "べんきょう", "研究": "けんきゅう",
            "言語": "げんご", "文法": "ぶんぽう", "意味": "いみ", "東京": "とうきょう",
            "京都": "きょうと", "昨日": "きのう", "今日": "きょう", "明日": "あした",
            "食べる": "たべる", "飲む": "のむ", "行く": "いく", "来る": "くる",
            "見る": "みる", "聞く": "きく", "話す": "はなす", "書く": "かく", "読む": "よむ",
            "新しい": "あたらしい", "古い": "ふるい", "高い": "たかい", "安い": "やすい",
            "良い": "よい", "美しい": "うつくしい", "静か": "しずか", "簡単": "かんたん",
            "時間": "じかん", "社会": "しゃかい", "世界": "せかい", "人間": "にんげん",
            "開発": "かいはつ", "情報": "じょうほう", "技術": "ぎじゅつ", "自然": "しぜん",
            "一期一会": "いちごいちえ", "以心伝心": "いしんでんしん", "十人十色": "じゅうにんといろ",
        }

    def _hira_to_kata(self, hira: str) -> str:
        """Converts Hiragana to Katakana."""
        chars = []
        for c in hira:
            code = ord(c)
            if 0x3041 <= code <= 0x3096:
                chars.append(chr(code + 0x60))
            else:
                chars.append(c)
        return "".join(chars)

    def generate_reading(self, text: str) -> ReadingGenerationResult:
        tokens = self.tokenizer.tokenize(text)
        annotations: List[RubyAnnotation] = []
        html_parts: List[str] = []
        hira_parts: List[str] = []
        kata_parts: List[str] = []

        for tok in tokens:
            surface = tok.text
            # Check if token contains Kanji
            has_kanji = bool(re.search(r"[\u4e00-\u9faf]", surface))

            if has_kanji:
                reading = self.kanji_reading_dict.get(surface)
                if not reading:
                    # Partial matching: strip trailing okurigana if any
                    m = re.match(r"^([\u4e00-\u9faf]+)(.*)$", surface)
                    if m and m.group(1) in self.kanji_reading_dict:
                        reading = self.kanji_reading_dict[m.group(1)] + m.group(2)
                    else:
                        reading = surface  # fallback

                kata = self._hira_to_kata(reading)
                ruby_tag = f"<ruby>{surface}<rt>{reading}</rt></ruby>"
                html_parts.append(ruby_tag)
                hira_parts.append(reading)
                kata_parts.append(kata)

                annotations.append(
                    RubyAnnotation(
                        kanji_surface=surface,
                        hiragana_reading=reading,
                        katakana_reading=kata,
                        start_char=tok.char_start,
                        end_char=tok.char_end,
                        html_ruby=ruby_tag,
                    )
                )
            else:
                html_parts.append(surface)
                hira_parts.append(surface)
                kata_parts.append(self._hira_to_kata(surface))

        return ReadingGenerationResult(
            original_text=text,
            annotated_html="".join(html_parts),
            hiragana_stream="".join(hira_parts),
            katakana_stream="".join(kata_parts),
            annotations=annotations,
        )
