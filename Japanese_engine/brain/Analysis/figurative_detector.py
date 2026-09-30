"""
Japanese Figurative Language Detector
======================================
Identifies Japanese Yojijukugo (四字熟語), Giongo/Gitaigo (擬音語・擬態語 onomatopoeia),
Kanyouku (慣用句 idioms), and simile/metaphor structures.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class JapaneseFigurativeHit:
    category: str  # "yojijukugo", "giongo_gitaigo", "kanyouku", "simile", "metaphor"
    expression: str
    literal_or_etymological_meaning: str
    figurative_meaning: str
    start_char: int
    end_char: int


@dataclass
class JapaneseFigurativeReport:
    total_found: int
    richness_score: float
    hits: List[JapaneseFigurativeHit] = field(default_factory=list)


class JapaneseFigurativeDetector:
    """
    Detects idiomatic, metaphorical, and mimetic expressions in Japanese text.
    """

    def __init__(self) -> None:
        self.yojijukugo_dict = {
            "一期一会": ("One time, one meeting", "Treasure every unrepeatable encounter with others"),
            "以心伝心": ("Heart to heart transmission", "Tacit mutual understanding without words"),
            "自業自得": ("Own actions, own harvest", "Suffering the natural consequences of one's misdeeds"),
            "臨機応変": ("Look at occasion, respond to change", "Flexibly adapting to changing circumstances"),
            "切磋琢磨": ("Cutting, grinding, and polishing", "Cultivating character and skill through mutual effort"),
            "起死回生": ("Wake the dead, return to life", "A dramatic miraculous comeback from a desperate crisis"),
            "十人十色": ("Ten people, ten colors", "Everyone has their own unique individuality or tastes"),
            "電光石火": ("Lightning flash, flint spark", "At blinding speed with utter agility"),
        }

        self.kanyouku_dict = {
            "手を焼く": ("To burn one's hands", "To have a terrible time dealing with someone or something troublesome"),
            "足を引っ張る": ("To pull someone's leg backwards", "To sabotage or hinder someone's progress"),
            "胸をなでおろす": ("To stroke one's chest down", "To breathe a sigh of relief"),
            "腹を割る": ("To split one's belly open", "To speak frankly with complete sincerity and no secrets"),
            "顔が広い": ("To have a wide face", "To have an extensive social or professional network"),
            "耳を傾ける": ("To tilt one's ear", "To listen attentively and sincerely"),
            "壁にぶつかる": ("To run into a wall", "To encounter an obstacle or plateau in progress"),
        }

        self.mimetic_dict = {
            "ドキドキ": "Heart throbbing rapidly due to anxiety or excitement",
            "ワクワク": "Trembling with eager anticipation and joy",
            "ペラペラ": "Fluent speech or thin lightweight fluttering",
            "キラキラ": "Sparkling or glittering brilliantly with light",
            "さらさら": "Smooth silky flow or rustling effortlessly",
            "ギリギリ": "At the absolute last limit or skin of one's teeth",
            "ばらばら": "Scattered apart into pieces or lack of unity",
            "すっきり": "Refreshed, clear, and relieved of burden",
        }

    def detect(self, text: str) -> JapaneseFigurativeReport:
        hits: List[JapaneseFigurativeHit] = []

        # 1. Yojijukugo
        for idiom, (lit, fig) in self.yojijukugo_dict.items():
            for m in re.finditer(re.escape(idiom), text):
                hits.append(
                    JapaneseFigurativeHit(
                        category="yojijukugo",
                        expression=idiom,
                        literal_or_etymological_meaning=lit,
                        figurative_meaning=fig,
                        start_char=m.start(),
                        end_char=m.end(),
                    )
                )

        # 2. Kanyouku (Idioms)
        for idiom, (lit, fig) in self.kanyouku_dict.items():
            stem = idiom[:-1]
            pat = re.escape(stem) + r"[すくつるむぶいうしたてったいだいたけた]+"
            for m in re.finditer(pat, text):
                hits.append(
                    JapaneseFigurativeHit(
                        category="kanyouku",
                        expression=m.group(0),
                        literal_or_etymological_meaning=lit,
                        figurative_meaning=fig,
                        start_char=m.start(),
                        end_char=m.end(),
                    )
                )

        # 3. Giongo / Gitaigo (Mimesis & Onomatopoeia)
        for mimetic, meaning in self.mimetic_dict.items():
            for m in re.finditer(re.escape(mimetic), text):
                hits.append(
                    JapaneseFigurativeHit(
                        category="giongo_gitaigo",
                        expression=mimetic,
                        literal_or_etymological_meaning="Echoic / mimetic mora repetition",
                        figurative_meaning=meaning,
                        start_char=m.start(),
                        end_char=m.end(),
                    )
                )

        # 4. Explicit Simile markers (〜のようだ, 〜みたいだ, 〜かの如く)
        simile_pattern = re.finditer(r"([^\s、。]+)(のようだ|みたいだ|かの如く|のように)", text)
        for m in simile_pattern:
            hits.append(
                JapaneseFigurativeHit(
                    category="simile",
                    expression=m.group(0),
                    literal_or_etymological_meaning=f"Comparison vehicle: {m.group(1)}",
                    figurative_meaning="Direct illustrative simile comparing tenor to vehicle",
                    start_char=m.start(),
                    end_char=m.end(),
                )
            )

        richness = min(1.0, round(len(hits) * 0.25, 2))

        return JapaneseFigurativeReport(
            total_found=len(hits),
            richness_score=richness,
            hits=hits,
        )
