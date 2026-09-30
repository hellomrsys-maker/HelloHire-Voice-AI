"""
ner.py - Japanese Named Entity Recognition (NER).
Extracts PERSON, ORG, GPE, DATE, and TECH entities using Japanese honorific markers,
institutional morpheme suffixes, gazetteers, and numeric patterns.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class JapaneseNamedEntity:
    text: str
    entity_type: str
    char_start: int
    char_end: int

    def __getitem__(self, item):
        if item in {"text", "entity"}:
            return self.text
        if item in {"entity_type", "label"}:
            return self.entity_type
        if item == "char_start":
            return self.char_start
        if item == "char_end":
            return self.char_end
        raise KeyError(item)


class JapaneseNamedEntityRecognizer:
    """
    Japanese Named Entity Recognizer for Person, Organization, Location, Date, and Tech.
    """

    HONORIFIC_SUFFIXES = ["さん", "様", "くん", "君", "ちゃん", "先生", "教授", "社長", "部長", "選手"]
    ORG_KEYWORDS = ["株式会社", "有限会社", "大学", "研究所", "銀行", "学会", "委員会", "グループ", "本社", "合同会社"]
    GPE_SUFFIXES = ["都", "道", "府", "県", "市", "区", "町", "村"]
    KNOWN_CITIES = {"東京", "京都", "大阪", "名古屋", "札幌", "福岡", "横浜", "神戸", "ロンドン", "ニューヨーク", "パリ", "日本"}
    TECH_TERMS = {"Python", "Rust", "C++", "CUDA", "Triton", "Java", "Julia", "人工知能", "深層学習", "機械学習", "トランスフォーマー", "ニューラルネットワーク"}

    def recognize(self, text: str) -> List[JapaneseNamedEntity]:
        entities: List[JapaneseNamedEntity] = []

        # 1. Organization detection
        for org in ["ソニー", "トヨタ", "任天堂", "パナソニック", "日立", "ソフトバンク", "Google", "Microsoft"]:
            for m in re.finditer(re.escape(org), text):
                entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="ORG", char_start=m.start(), char_end=m.end()))

        for kw in self.ORG_KEYWORDS:
            pat = rf"([A-Za-z0-9\u4e00-\u9faf\u30a0-\u30ff]{{2,10}}{kw}|{kw}[A-Za-z0-9\u4e00-\u9faf\u30a0-\u30ff]{{2,10}})"
            for m in re.finditer(pat, text):
                entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="ORG", char_start=m.start(), char_end=m.end()))

        # 2. Location (GPE) detection
        for city in self.KNOWN_CITIES:
            for m in re.finditer(re.escape(city), text):
                entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="GPE", char_start=m.start(), char_end=m.end()))

        for sfx in self.GPE_SUFFIXES:
            pat = rf"([\u4e00-\u9faf]{{2,4}}{sfx})"
            for m in re.finditer(pat, text):
                entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="GPE", char_start=m.start(), char_end=m.end()))

        # 3. Person detection via honorifics
        for sfx in self.HONORIFIC_SUFFIXES:
            pat = rf"([\u4e00-\u9faf]{{1,4}}){sfx}"
            for m in re.finditer(pat, text):
                name = m.group(1)
                entities.append(JapaneseNamedEntity(text=name, entity_type="PERSON", char_start=m.start(1), char_end=m.end(1)))

        # Person detection via Katakana names (e.g. アラン・チューリング, マリー・キュリー)
        katakana_person_pat = r"([\u30a0-\u30ff]+[・\s][\u30a0-\u30ff]+)"
        for m in re.finditer(katakana_person_pat, text):
            entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="PERSON", char_start=m.start(), char_end=m.end()))

        # 4. Tech term detection
        for tech in self.TECH_TERMS:
            for m in re.finditer(re.escape(tech), text, flags=re.IGNORECASE):
                entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="TECH", char_start=m.start(), char_end=m.end()))

        # 5. Date detection
        date_pat = r"((?:19|20)\d{2}年|\d{1,2}月|\d{1,2}日|令和\d{1,2}年|平成\d{1,2}年|今日|昨日|明日)"
        for m in re.finditer(date_pat, text):
            entities.append(JapaneseNamedEntity(text=m.group(0), entity_type="DATE", char_start=m.start(), char_end=m.end()))

        # Sort and deduplicate by start span
        entities.sort(key=lambda e: e.char_start)
        unique_entities: List[JapaneseNamedEntity] = []
        occupied_spans = set()

        for e in entities:
            span = (e.char_start, e.char_end)
            if span not in occupied_spans:
                unique_entities.append(e)
                occupied_spans.add(span)

        return unique_entities

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        named = self.recognize(text)
        return [
            {
                "entity": e.text,
                "label": e.entity_type,
                "start_char": e.char_start,
                "end_char": e.char_end,
            }
            for e in named
        ]
