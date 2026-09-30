"""
pos_tagging.py - Japanese Part-of-Speech Tagging (UniDic/IPADic and Universal Dependencies).
Maps Japanese morphemes to Meishi, Doushi, Keiyoushi, Joshi, Jodoushi, and Universal Dependencies.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Union

from .tokenization import JapaneseToken

# UniDic to Universal Dependencies 17 mapping
UNIDIC_TO_UD = {
    "名詞": "NOUN",
    "固有名詞": "PROPN",
    "代名詞": "PRON",
    "数詞": "NUM",
    "動詞": "VERB",
    "形容詞": "ADJ",
    "形状詞": "ADJ",
    "助詞": "ADP",
    "助動詞": "AUX",
    "副詞": "ADV",
    "連体詞": "DET",
    "接続詞": "CCONJ",
    "感動詞": "INTJ",
    "記号": "PUNCT",
    "補助記号": "PUNCT",
    "接頭辞": "NOUN",
    "接尾辞": "NOUN"
}


@dataclass
class JapaneseTaggedToken:
    token: JapaneseToken
    pos_tag: str       # UniDic category (e.g., "名詞", "動詞", "助詞")
    sub_tag: str       # Subcategory (e.g., "格助詞", "係助詞", "自立")
    ud_tag: str        # Universal Dependencies tag (e.g., "NOUN", "VERB", "ADP")

    @property
    def pos(self) -> str:
        romaji_map = {
            "名詞": "Meishi",
            "固有名詞": "Meishi",
            "代名詞": "Meishi",
            "数詞": "Meishi",
            "動詞": "Doushi",
            "形容詞": "Keiyoushi",
            "形状詞": "Keiyoushi",
            "助詞": "Joshi",
            "助動詞": "Jodoushi",
            "副詞": "Fukushi",
            "記号": "Kigou",
            "補助記号": "Kigou",
        }
        return romaji_map.get(self.pos_tag, self.pos_tag)

    def __getitem__(self, item):
        if item == "token":
            return self.token.text if isinstance(self.token, JapaneseToken) else str(self.token)
        if item in {"pos_tag", "tag", "pos"}:
            return self.pos
        if item == "sub_tag":
            return self.sub_tag
        if item == "ud_tag":
            return self.ud_tag
        raise KeyError(item)


class JapanesePOSTagger:
    """
    Japanese POS tagger mapping tokens to UniDic Japanese grammatical categories and UD tags.
    """

    PARTICLES = {
        "は": ("助詞", "係助詞"),
        "が": ("助詞", "格助詞"),
        "を": ("助詞", "格助詞"),
        "に": ("助詞", "格助詞"),
        "で": ("助詞", "格助詞"),
        "と": ("助詞", "格助詞"),
        "も": ("助詞", "係助詞"),
        "へ": ("助詞", "格助詞"),
        "から": ("助詞", "格助詞"),
        "まで": ("助詞", "副助詞"),
        "より": ("助詞", "格助詞"),
        "の": ("助詞", "連体化"),
        "ね": ("助詞", "終助詞"),
        "よ": ("助詞", "終助詞"),
        "か": ("助詞", "終助詞"),
        "な": ("助詞", "終助詞"),
    }

    AUXILIARIES = {
        "です": ("助動詞", "丁寧"),
        "ます": ("助動詞", "丁寧"),
        "でした": ("助動詞", "過去"),
        "ました": ("助動詞", "過去"),
        "だ": ("助動詞", "断定"),
        "である": ("助動詞", "断定"),
        "ない": ("助動詞", "否定"),
        "なかった": ("助動詞", "否定過去"),
        "たい": ("助動詞", "希望"),
        "れる": ("助動詞", "受身・自発"),
        "られる": ("助動詞", "受身・可能"),
        "せる": ("助動詞", "使役"),
        "させる": ("助動詞", "使役"),
        "た": ("助動詞", "過去・完了"),
    }

    PRONOUNS = {"私", "僕", "俺", "自分", "あなた", "君", "彼", "彼女", "これ", "それ", "あれ", "どれ", "誰", "何"}

    COMMON_VERBS = {
        "食べる", "飲む", "走る", "話す", "読む", "書く", "行く", "来る",
        "する", "思う", "考える", "見る", "聞く", "分かる", "できる", "ある", "いる"
    }

    COMMON_ADJECTIVES = {
        "大きい", "小さい", "新しい", "古い", "良い", "悪い", "高い", "低い",
        "美しい", "素晴らしい", "速い", "遅い", "難しい", "易しい", "美味しい"
    }

    def tag_tokens(self, tokens: Union[List[JapaneseToken], List[str]]) -> List[JapaneseTaggedToken]:
        norm_tokens: List[JapaneseToken] = []
        for t in tokens:
            if isinstance(t, JapaneseToken):
                norm_tokens.append(t)
            else:
                s = str(t)
                norm_tokens.append(JapaneseToken(text=s, char_start=0, char_end=len(s), script_type="MIXED", is_word=True))

        tagged: List[JapaneseTaggedToken] = []
        for tok in norm_tokens:
            w = tok.text

            # 1. Punctuation
            if w in {"、", "。", "！", "？", "「", "」", "『", "』", "・", ",", ".", "!", "?"}:
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag="補助記号", sub_tag="句点・読点", ud_tag="PUNCT"))
                continue

            # 2. Particles (Joshi)
            if w in self.PARTICLES:
                p_tag, s_tag = self.PARTICLES[w]
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag=p_tag, sub_tag=s_tag, ud_tag="ADP"))
                continue

            # 3. Auxiliaries (Jodoushi)
            if w in self.AUXILIARIES:
                p_tag, s_tag = self.AUXILIARIES[w]
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag=p_tag, sub_tag=s_tag, ud_tag="AUX"))
                continue

            # 4. Pronouns
            if w in self.PRONOUNS:
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag="代名詞", sub_tag="人称", ud_tag="PRON"))
                continue

            # 5. Adjectives (i-Adjective)
            if w in self.COMMON_ADJECTIVES or (w.endswith("い") and len(w) > 1 and tok.script_type in {"HIRAGANA", "MIXED"}):
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag="形容詞", sub_tag="一般", ud_tag="ADJ"))
                continue

            # 6. Verbs (Dictionary or inflected form)
            if (
                w in self.COMMON_VERBS
                or w in {"読み", "書き", "話し", "食べ", "飲み", "行き", "買い", "持ち", "待ち", "呼び", "遊び", "使い", "思い", "言い", "知り", "帰り", "入り", "走り", "立ち", "乗り", "降り", "開き", "教え", "始め", "終わり"}
                or (w.endswith(("る", "く", "ぐ", "す", "つ", "ぬ", "ぶ", "む", "う", "み", "き", "ち", "し", "い", "ます", "ました", "ません")) and tok.script_type in {"MIXED", "KANJI"})
            ):
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag="動詞", sub_tag="一般", ud_tag="VERB"))
                continue

            # 7. Numerals
            if re.match(r"^[0-9０-９一二三四五六七八九十百千万億]+$", w):
                tagged.append(JapaneseTaggedToken(token=tok, pos_tag="名詞", sub_tag="数詞", ud_tag="NUM"))
                continue

            # Default: Noun (Meishi)
            tagged.append(JapaneseTaggedToken(token=tok, pos_tag="名詞", sub_tag="普通名詞", ud_tag="NOUN"))

        return tagged
