"""
Japanese Discourse Parser
=========================
Parses discourse cohesion, Rhetorical Structure Theory (RST) relations,
and traditional Japanese Ki-shō-ten-ketsu (起承転結) 4-stage narrative structures.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class JapaneseDiscourseSegment:
    segment_id: int
    text: str
    kishotenketsu_role: str  # "起 (Introduction)", "承 (Development)", "転 (Turn/Twist)", "結 (Conclusion)"
    rst_relation: str       # "Elaboration", "Contrast", "Cause_Result", "Condition", "Summary"
    connectives: List[str] = field(default_factory=list)


@dataclass
class JapaneseDiscourseReport:
    total_segments: int
    structure_type: str
    cohesion_score: float
    segments: List[JapaneseDiscourseSegment] = field(default_factory=list)


class JapaneseDiscourseParser:
    """
    Analyzes sentence-level rhetorical transitions and discourse organization
    in Japanese texts using connective markers and Ki-shō-ten-ketsu mapping.
    """

    def __init__(self) -> None:
        self.contrast_markers = ["しかし", "だが", "けれども", "一方で", "ところが", "にもかかわらず"]
        self.cause_markers = ["したがって", "そのため", "ゆえに", "よって", "から", "ので"]
        self.elaboration_markers = ["具体的には", "すなわち", "例えば", "つまり", "さらに", "また"]
        self.conclusion_markers = ["結論として", "要するに", "以上のように", "総じて"]

    def parse(self, text: str) -> JapaneseDiscourseReport:
        # Split into sentences
        raw_sentences = [s.strip() for s in re.split(r"[。！？\n]+", text) if s.strip()]
        if not raw_sentences:
            return JapaneseDiscourseReport(0, "Empty", 1.0, [])

        segments: List[JapaneseDiscourseSegment] = []
        n = len(raw_sentences)

        for i, s_text in enumerate(raw_sentences):
            # Connectives detection
            detected_connectives = []
            rst = "Elaboration"

            for c in self.contrast_markers:
                if c in s_text:
                    detected_connectives.append(c)
                    rst = "Contrast"

            for c in self.cause_markers:
                if c in s_text:
                    detected_connectives.append(c)
                    rst = "Cause_Result"

            for c in self.elaboration_markers:
                if c in s_text:
                    detected_connectives.append(c)
                    rst = "Elaboration"

            for c in self.conclusion_markers:
                if c in s_text:
                    detected_connectives.append(c)
                    rst = "Summary"

            # Ki-shō-ten-ketsu assignment by relative position and contrast triggers
            pos_ratio = i / max(1, n - 1)
            if pos_ratio < 0.25:
                role = "起 (Ki - Introduction)"
            elif pos_ratio < 0.55:
                role = "承 (Shō - Development)"
            elif pos_ratio < 0.80 or rst == "Contrast":
                role = "転 (Ten - Twist / Turn)"
            else:
                role = "結 (Ketsu - Conclusion)"

            segments.append(
                JapaneseDiscourseSegment(
                    segment_id=i + 1,
                    text=s_text,
                    kishotenketsu_role=role,
                    rst_relation=rst,
                    connectives=detected_connectives,
                )
            )

        # Cohesion metric based on connective density and smooth transitions
        connective_count = sum(len(seg.connectives) for seg in segments)
        cohesion = min(1.0, 0.5 + (connective_count / max(1, n)) * 0.3)

        return JapaneseDiscourseReport(
            total_segments=n,
            structure_type="起承転結 (Ki-shō-ten-ketsu)" if n >= 4 else "Linear Argument",
            cohesion_score=round(cohesion, 2),
            segments=segments,
        )
