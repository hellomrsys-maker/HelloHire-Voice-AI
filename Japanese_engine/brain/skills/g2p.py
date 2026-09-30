"""
g2p.py - Japanese Grapheme-to-Phoneme (G2P), Furigana Reading, and Mora Decomposition.
Converts Kanji-Kana mixed orthography into Hiragana readings, Romaji, and phonetic mora streams.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class JapaneseG2PResult:
    word: str
    reading: str       # Hiragana reading (Furigana)
    phonemes: List[str]# Mora / Phonemic tokens
    pitch_accent_type: str = "Heiban (平板)"

    @property
    def phonetic_moras(self) -> List[str]:
        return self.phonemes

    @property
    def hiragana_reading(self) -> str:
        return self.reading

    def __iter__(self):
        return iter(self.phonemes)


class JapaneseG2PConverter:
    """
    G2P converter mapping Japanese Kanji-Kana mixed text to Hiragana readings and phonemic mora streams.
    """

    KANJI_READINGS = {
        "私": "わたし",
        "僕": "ぼく",
        "彼": "かれ",
        "彼女": "かのじょ",
        "人間": "にんげん",
        "言語": "げんご",
        "人工知能": "じんこうちのう",
        "機械学習": "きかいがくしゅう",
        "深層学習": "しんそうがくしゅう",
        "研究": "けんきゅう",
        "開発": "かいはつ",
        "日本": "にほん",
        "東京": "とうきょう",
        "京都": "きょうと",
        "世界": "せかい",
        "先生": "せんせい",
        "学生": "がくせい",
        "大学": "だいがく",
        "会社": "かいしゃ",
        "本": "ほん",
        "水": "みず",
        "今日": "きょう",
        "明日": "あした",
        "昨日": "きのう",
        "食べる": "たべる",
        "食べた": "たべた",
        "飲む": "のむ",
        "飲んだ": "のんだ",
        "行く": "いく",
        "行った": "いった",
        "来る": "くる",
        "来た": "きた",
        "話す": "はなす",
        "話した": "はなした",
        "読む": "よむ",
        "読んだ": "よんだ",
        "書く": "かく",
        "書いた": "かいた",
        "美しい": "うつくしい",
        "新しい": "あたらしい",
        "高い": "たかい",
    }

    HIRA_TO_MORA = {
        "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
        "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
        "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
        "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
        "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
        "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
        "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
        "や": "ya", "ゆ": "yu", "よ": "yo",
        "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
        "わ": "wa", "を": "o", "ん": "N",
        "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
        "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
        "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
        "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
        "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
        "っ": "Q", "ー": ":"
    }

    def convert_word(self, word: str) -> JapaneseG2PResult:
        w = word.strip()
        reading = self.KANJI_READINGS.get(w, w)

        # Mora breakdown from Hiragana reading
        mora_list: List[str] = []
        i = 0
        n = len(reading)

        while i < n:
            ch = reading[i]
            # Digraph kana (拗音: きゃ, しゃ, ちょ, etc.)
            if i + 1 < n and reading[i + 1] in {"ゃ", "ゅ", "ょ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ"}:
                digraph = reading[i : i + 2]
                mora_list.append(digraph)
                i += 2
                continue

            if ch in self.HIRA_TO_MORA:
                mora_list.append(self.HIRA_TO_MORA[ch])
            else:
                mora_list.append(ch)
            i += 1

        return JapaneseG2PResult(word=w, reading=reading, phonemes=mora_list)

    def text_to_phonemes(self, text: str) -> List[str]:
        all_phonemes: List[str] = []
        # Match words or single characters
        for token in re.findall(r"[\u4e00-\u9faf]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[A-Za-z0-9]+|[^\s]", text):
            res = self.convert_word(token)
            all_phonemes.extend(res.phonemes)
        return all_phonemes

    def convert(self, text: str) -> JapaneseG2PResult:
        moras = self.text_to_phonemes(text)
        tokens = re.findall(r"[\u4e00-\u9faf]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[A-Za-z0-9]+|[^\s]", text)
        readings = [self.KANJI_READINGS.get(t, t) for t in tokens]
        hiragana_reading = "".join(readings)

        # Tokyo standard accent contour inference
        accent = "Heiban (平板)"
        if moras and moras[0] in {"ha", "a", "ho", "ka"}:
            accent = "Atamadaka (頭高)"
        elif len(moras) >= 3:
            accent = "Nakadaka (中高)"

        return JapaneseG2PResult(
            word=text,
            reading=hiragana_reading,
            phonemes=moras,
            pitch_accent_type=accent,
        )

