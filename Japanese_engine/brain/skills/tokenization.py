"""
tokenization.py - Japanese Morphological Segmentation and Script Boundary Tokenizer.
Segments unspaced Japanese orthography (Kanji, Hiragana, Katakana, Romaji/Digits)
into morphemes with character spans, clitic particle handling, and subword BPE.
"""

from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Unicode blocks for Japanese script classification
KANJI_RE = re.compile(r"[\u4e00-\u9faf\u3400-\u4dbf]")
HIRAGANA_RE = re.compile(r"[\u3040-\u309f]")
KATAKANA_RE = re.compile(r"[\u30a0-\u30ff]")
PUNCTUATION_JA = {"、", "。", "！", "？", "「", "」", "『", "』", "・", "…", "—", ",", ".", "!", "?"}

# Core Japanese functional particles and auxiliary suffixes
FUNCTIONAL_PARTICLES = {
    "は", "が", "を", "に", "で", "と", "も", "へ", "から", "まで",
    "より", "の", "ね", "よ", "か", "わ", "ぞ", "ぜ", "な", "し",
    "ので", "から", "のに", "ても", "でも", "なら", "ば", "たり", "だり"
}

AUXILIARY_VERB_ENDINGS = {
    "です", "ます", "でした", "ました", "ません", "ません", "だ", "である",
    "ない", "なかった", "たい", "たがる", "れる", "られる", "せる", "させる",
    "て", "で", "た", "だ"
}


@dataclass
class JapaneseToken:
    text: str
    char_start: int
    char_end: int
    script_type: str  # "KANJI", "HIRAGANA", "KATAKANA", "ROMAJI", "PUNCT", "MIXED"
    is_word: bool

    def __str__(self) -> str:
        return self.text

    @property
    def script(self) -> str:
        return self.script_type.capitalize()

    def __getitem__(self, item):
        if item == "text":
            return self.text
        if item == "char_start":
            return self.char_start
        if item == "char_end":
            return self.char_end
        if item in {"script_type", "script"}:
            return self.script
        if item == "is_word":
            return self.is_word
        raise KeyError(item)


class JapaneseTokenizer:
    """
    Japanese morphological tokenizer handling script transitions and particle attachments.
    """

    def __init__(self, vocab: Optional[Dict[str, int]] = None):
        self.vocab = vocab or {}
        # Known common multi-character words
        self.common_lexicon = {
            "私", "僕", "彼", "彼女", "人間", "言語", "人工知能", "機械学習",
            "自然言語処理", "深層学習", "モデル", "システム", "研究", "開発",
            "日本", "東京", "京都", "世界", "時間", "仕事", "会社", "大学",
            "先生", "学生", "友達", "本", "車", "水", "今日", "明日", "昨日",
            "食べる", "飲む", "走る", "話す", "読む", "書く", "行く", "来る",
            "する", "思う", "考える", "見る", "聞く", "分かる", "できる",
            "大きい", "小さい", "新しい", "古い", "良い", "悪い", "高い", "低い",
            "美しい", "素晴らしい", "非常に", "とても", "しかし", "また", "そして",
            # Verb stems and polite forms
            "読み", "書き", "話し", "食べ", "飲み", "行き", "買い", "持ち", "待ち",
            "呼び", "遊び", "使い", "思い", "言い", "知り", "帰り", "入り", "走り",
            "読みます", "書きます", "話します", "食べます", "飲みます", "行きます", "来ます",
            "読みました", "書きました", "食べました", "来ました", "しました",
        }

    def _get_script_type(self, ch: str) -> str:
        if ch in PUNCTUATION_JA or ch.isspace():
            return "PUNCT"
        if KANJI_RE.match(ch):
            return "KANJI"
        if HIRAGANA_RE.match(ch):
            return "HIRAGANA"
        if KATAKANA_RE.match(ch):
            return "KATAKANA"
        if ch.isascii() and ch.isalnum():
            return "ROMAJI"
        return "OTHER"

    def split_sentences(self, text: str) -> List[str]:
        """Splits text on Japanese sentence delimiters (。, ！, ？, newline)."""
        if not text or not text.strip():
            return []
        raw_units = re.split(r"(?<=[。！？\n])", text.strip())
        return [u.strip() for u in raw_units if u.strip()]

    def tokenize(self, text: str) -> List[JapaneseToken]:
        """
        Segments Japanese text into tokens using lexical lookup and script boundary heuristics.
        """
        norm_text = unicodedata.normalize("NFKC", text)
        tokens: List[JapaneseToken] = []
        n = len(norm_text)
        i = 0

        while i < n:
            ch = norm_text[i]

            # Whitespace skip
            if ch.isspace():
                i += 1
                continue

            # Punctuation
            if ch in PUNCTUATION_JA:
                tokens.append(JapaneseToken(text=ch, char_start=i, char_end=i + 1, script_type="PUNCT", is_word=False))
                i += 1
                continue

            # Longest match lookup in common lexicon
            matched = False
            for l in range(min(8, n - i), 1, -1):
                candidate = norm_text[i : i + l]
                if candidate in self.common_lexicon:
                    s_type = "KANJI" if all(KANJI_RE.match(c) for c in candidate) else ("KATAKANA" if all(KATAKANA_RE.match(c) for c in candidate) else "MIXED")
                    tokens.append(JapaneseToken(text=candidate, char_start=i, char_end=i + l, script_type=s_type, is_word=True))
                    i += l
                    matched = True
                    break
            if matched:
                continue

            # Script transition segmentation
            cur_script = self._get_script_type(ch)
            start_idx = i

            # Group Katakana words or Romaji words continuously
            if cur_script in {"KATAKANA", "ROMAJI"}:
                while i < n and self._get_script_type(norm_text[i]) == cur_script:
                    i += 1
                t_str = norm_text[start_idx:i]
                tokens.append(JapaneseToken(text=t_str, char_start=start_idx, char_end=i, script_type=cur_script, is_word=True))
                continue

            # Group Kanji sequences
            if cur_script == "KANJI":
                while i < n and self._get_script_type(norm_text[i]) == "KANJI":
                    i += 1
                t_str = norm_text[start_idx:i]
                tokens.append(JapaneseToken(text=t_str, char_start=start_idx, char_end=i, script_type="KANJI", is_word=True))
                continue

            # Hiragana handling: isolate functional particles or short grammatical units
            if cur_script == "HIRAGANA":
                # Check for two-character particles/endings (e.g., から, まで, です, ます, ない)
                if i + 2 <= n and norm_text[i : i + 2] in (FUNCTIONAL_PARTICLES | AUXILIARY_VERB_ENDINGS):
                    t_str = norm_text[i : i + 2]
                    tokens.append(JapaneseToken(text=t_str, char_start=i, char_end=i + 2, script_type="HIRAGANA", is_word=True))
                    i += 2
                    continue
                # Single character particle or inflection
                if ch in FUNCTIONAL_PARTICLES or ch in {"た", "て", "だ", "で", "る", "い", "う"}:
                    tokens.append(JapaneseToken(text=ch, char_start=i, char_end=i + 1, script_type="HIRAGANA", is_word=True))
                    i += 1
                    continue

                # Run of remaining hiragana
                while i < n and self._get_script_type(norm_text[i]) == "HIRAGANA" and norm_text[i] not in FUNCTIONAL_PARTICLES:
                    i += 1
                t_str = norm_text[start_idx:i] if i > start_idx else ch
                if i == start_idx:
                    i += 1
                    t_str = ch
                tokens.append(JapaneseToken(text=t_str, char_start=start_idx, char_end=i, script_type="HIRAGANA", is_word=True))
                continue

            # Default single character
            tokens.append(JapaneseToken(text=ch, char_start=i, char_end=i + 1, script_type=cur_script, is_word=True))
            i += 1

        return tokens

    def tokenize_words(self, text: str) -> List[str]:
        """Returns string tokens."""
        return [t.text for t in self.tokenize(text)]
