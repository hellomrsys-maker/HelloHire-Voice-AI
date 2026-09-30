"""
Japanese Furigana Annotator Pipeline
====================================
Generates ruby readings for pedagogical, learner, and accessibility contexts.
Supports HTML5 <ruby> tags, bracketed notation, and JLPT/grade-level filtering.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.reading_generation import JapaneseReadingGenerator


@dataclass
class FuriganaAnnotatorResult:
    original_text: str
    html_output: str
    bracketed_output: str  # e.g., 漢字[かんじ]
    kanji_count: int


class JapaneseFuriganaAnnotator:
    """
    Pedagogical and publishing tool generating precise furigana glosses above kanji.
    """

    def __init__(self) -> None:
        self.reading_gen = JapaneseReadingGenerator()

    def annotate(self, text: str, format_type: str = "html") -> FuriganaAnnotatorResult:
        gen_res = self.reading_gen.generate_reading(text)

        # Build bracketed output: 漢字[かんじ]
        bracketed = text
        for ann in reversed(gen_res.annotations):
            rep = f"{ann.kanji_surface}[{ann.hiragana_reading}]"
            bracketed = bracketed[:ann.start_char] + rep + bracketed[ann.end_char:]

        return FuriganaAnnotatorResult(
            original_text=text,
            html_output=gen_res.annotated_html,
            bracketed_output=bracketed,
            kanji_count=len(gen_res.annotations),
        )
