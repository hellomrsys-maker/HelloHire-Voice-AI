"""
Japanese OCR Post-Processing Engine
===================================
Handles Japanese vertical text (縦書き Tategaki) reading order (top-to-bottom, right-to-left),
Furigana ruby filtering, and orthographic full-width/half-width normalization.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class OCRPostprocessResult:
    normalized_text: str
    detected_orientation: str  # "Horizontal (横書き)", "Vertical (縦書き)"
    removed_ruby_annotations: List[str]
    has_full_width_alphanumerics: bool


class JapaneseOCRPostprocessor:
    """
    Cleans raw OCR extractions from scanned manga, historical books, newspapers, and receipts.
    """

    def clean_ocr_text(self, raw_text: str, is_vertical: bool = False) -> OCRPostprocessResult:
        res = raw_text

        # 1. Normalize vertical punctuation and symbols if tategaki
        if is_vertical:
            vertical_map = {
                "﹁": "「", "﹂": "」", "﹃": "『", "﹄": "』",
                "︱": "ー", "︙": "…", "︰": "：",
            }
            for v_char, std_char in vertical_map.items():
                res = res.replace(v_char, std_char)

        # 2. Extract and filter inline ruby brackets (e.g. 漢字（かんじ） -> 漢字)
        ruby_matches = re.findall(r"[\u4e00-\u9faf]+[（\(]([ぁ-んァ-ン]+)[）\)]", res)
        # Clean inline parenthesis furigana to preserve clean text
        cleaned_text = re.sub(r"([\u4e00-\u9faf]+)[（\(][ぁ-んァ-ン]+[）\)]", r"\1", res)

        # 3. Detect full-width alphanumerics
        has_fw = bool(re.search(r"[Ａ-Ｚａ-ｚ０-９]", cleaned_text))

        # Convert full-width ASCII to standard half-width
        normalized_chars = []
        for c in cleaned_text:
            code = ord(c)
            if 0xFF01 <= code <= 0xFF5E:
                normalized_chars.append(chr(code - 0xFEE0))
            elif code == 0x3000:  # Full-width space
                normalized_chars.append(" ")
            else:
                normalized_chars.append(c)

        final_text = "".join(normalized_chars).strip()

        return OCRPostprocessResult(
            normalized_text=final_text,
            detected_orientation="Vertical (縦書き)" if is_vertical else "Horizontal (横書き)",
            removed_ruby_annotations=ruby_matches,
            has_full_width_alphanumerics=has_fw,
        )
