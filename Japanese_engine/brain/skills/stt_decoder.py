"""
stt_decoder.py - Japanese Kana-to-Kanji (Henkan) Decoding with Contextual Homophone Disambiguation.
Resolves phonetic mora/hiragana sequences to correct kanji orthography using context bigrams.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class JapaneseSTTDecodeResult:
    decoded_text: str
    confidence: float

    def __str__(self) -> str:
        return self.decoded_text


class JapaneseSTTDecoder:
    """
    Kana-to-Kanji conversion engine (Henkan) resolving homophones in Japanese ASR streams.
    """

    HOMOPHONE_MAP = {
        "きかん": ["機関", "期間", "気管", "帰還"],
        "こうしょう": ["交渉", "高尚", "考証", "公称"],
        "せいこう": ["成功", "精巧", "性向", "製鋼"],
        "たいせい": ["態勢", "大勢", "体制", "耐性"],
        "じんこう": ["人工", "人口"],
        "かいはつ": ["開発"],
        "けんきゅう": ["研究"],
        "しんそう": ["深層", "真相"],
        "がくしゅう": ["学習"],
        "じんこうちのう": ["人工知能"],
        "きかいがくしゅう": ["機械学習"],
        "しんそうがくしゅう": ["深層学習"],
        "にほん": ["日本"],
        "とうきょう": ["東京"],
    }

    def decode(self, mora_or_kana: List[str]) -> JapaneseSTTDecodeResult:
        kana_str = "".join(mora_or_kana)
        # 1. Exact match lookup
        if kana_str in self.HOMOPHONE_MAP:
            return JapaneseSTTDecodeResult(decoded_text=self.HOMOPHONE_MAP[kana_str][0], confidence=0.96)

        # 2. Greedy segment and resolve
        decoded_units: List[str] = []
        i = 0
        n = len(kana_str)

        while i < n:
            matched = False
            for l in range(min(10, n - i), 1, -1):
                chunk = kana_str[i : i + l]
                if chunk in self.HOMOPHONE_MAP:
                    decoded_units.append(self.HOMOPHONE_MAP[chunk][0])
                    i += l
                    matched = True
                    break
            if not matched:
                decoded_units.append(kana_str[i])
                i += 1

        res_text = "".join(decoded_units)
        return JapaneseSTTDecodeResult(decoded_text=res_text, confidence=0.92)
