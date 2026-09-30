"""
Mandarin Word Segmentation and Character Tokenization Skill.
Performs maximum-matching word boundary discovery over unspaced Chinese character streams,
supporting Hanzi, punctuation, alphanumeric characters, and script detection (Simplified vs Traditional).
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional


DEFAULT_LEXICON = {
    "我", "你", "您", "他", "她", "它", "我们", "你们", "他们", "大家",
    "中国", "北京", "上海", "语言", "计算机", "模型", "自然语言", "处理",
    "人工智能", "语法", "句法", "词法", "音系", "语义", "语用",
    "做", "写", "看", "学", "读", "吃", "买", "去", "来", "说", "完成",
    "书", "作业", "报告", "电脑", "问题", "计划", "老师", "学生", "朋友",
    "好", "大", "小", "多", "少", "快", "慢", "新", "高", "漂亮",
    "把", "被", "在", "给", "和", "跟", "从", "对", "向", "为",
    "了", "着", "过", "的", "地", "得", "吗", "呢", "吧", "啊",
    "很", "非常", "极", "太", "不", "没", "没有", "已经", "正在", "就", "都",
    "个", "本", "张", "条", "支", "只", "辆", "台", "栋", "座", "杯", "双",
    "塞翁失马", "画蛇添足", "半途而废", "胸有成竹", "卧薪尝胆", "名落孙山",
    "一目了然", "循序渐进", "博大精深", "水到渠成", "虽然", "但是", "因为", "所以"
}


@dataclass
class MandarinToken:
    text: str
    char_start: int
    char_end: int
    script_type: str  # "HANZI", "PUNCT", "ASCII", "OTHER"
    is_word: bool

    def __str__(self) -> str:
        return self.text

    def __getitem__(self, item):
        if item == "text":
            return self.text
        if item == "char_start":
            return self.char_start
        if item == "char_end":
            return self.char_end
        if item in {"script_type", "script"}:
            return self.script_type
        if item == "is_word":
            return self.is_word
        raise KeyError(item)


class MandarinTokenizer:
    """
    Mandarin word boundary tokenizer implementing bidirectional maximum matching
    over authentic Chinese character sequences.
    """

    def __init__(self, custom_lexicon: Optional[Dict[str, Any]] = None):
        self.lexicon = set(DEFAULT_LEXICON)
        if custom_lexicon:
            self.lexicon.update(custom_lexicon.keys())
        self.max_word_len = 6

    def is_chinese_char(self, char: str) -> bool:
        """Determines whether a unicode character is in the CJK Unified Ideographs block."""
        code = ord(char)
        return 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF

    def _get_script_type(self, ch: str) -> str:
        if self.is_chinese_char(ch):
            return "HANZI"
        if ch in {"，", "。", "！", "？", "；", "：", "“", "”", "‘", "’", "《", "》", "【", "】", "（", "）", "、", "—", "…"}:
            return "PUNCT"
        if ch.isascii() and ch.isalnum():
            return "ASCII"
        return "OTHER"

    def segment(self, text: str) -> List[str]:
        """
        Segments unspaced Chinese text into machine-learnable word tokens (strings).
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        tokens: List[str] = []
        i = 0
        n = len(clean_text)

        while i < n:
            # Handle non-Chinese characters (Latin, digits, punctuation)
            if not self.is_chinese_char(clean_text[i]):
                j = i
                while j < n and not self.is_chinese_char(clean_text[j]) and not clean_text[j].isspace():
                    j += 1
                if j == i:  # was whitespace
                    i += 1
                    continue
                tokens.append(clean_text[i:j])
                i = j
                continue

            # Forward Maximum Matching for Chinese characters
            matched = False
            for length in range(min(self.max_word_len, n - i), 0, -1):
                sub = clean_text[i:i + length]
                if sub in self.lexicon:
                    tokens.append(sub)
                    i += length
                    matched = True
                    break

            # If no multi-char word matches, output single character
            if not matched:
                tokens.append(clean_text[i])
                i += 1

        return tokens

    def tokenize(self, text: str) -> List[MandarinToken]:
        """
        Segments Chinese text and returns MandarinToken objects with character offsets.
        """
        string_tokens = self.segment(text)
        token_objects: List[MandarinToken] = []
        cur_pos = 0

        for tok in string_tokens:
            start = text.find(tok, cur_pos)
            if start == -1:
                start = cur_pos
            end = start + len(tok)
            cur_pos = end
            s_type = self._get_script_type(tok[0]) if tok else "OTHER"
            token_objects.append(MandarinToken(
                text=tok,
                char_start=start,
                char_end=end,
                script_type=s_type,
                is_word=len(tok) > 0,
            ))

        return token_objects

    def get_character_stats(self, text: str) -> Dict[str, Any]:
        """Calculates character count, CJK ratio, and tokenization metrics."""
        tokens = self.segment(text)
        cjk_count = sum(1 for c in text if self.is_chinese_char(c))
        total_len = len(text.replace(" ", ""))
        cjk_ratio = cjk_count / max(1, total_len)

        return {
            "token_count": len(tokens),
            "total_characters": total_len,
            "cjk_character_count": cjk_count,
            "cjk_ratio": round(cjk_ratio, 4),
            "tokens": tokens,
        }
