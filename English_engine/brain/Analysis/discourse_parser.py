"""
Discourse Parser implementing Rhetorical Structure Theory (RST).
Segments text into Elementary Discourse Units (EDUs) and parses nucleus-satellite
rhetorical relations (Elaboration, Contrast, Cause, Condition, Concession, Attribution).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ElementaryDiscourseUnit:
    edu_id: int
    text: str
    char_start: int
    char_end: int


@dataclass
class RhetoricalRelation:
    relation_name: str  # "Elaboration", "Contrast", "Cause", "Condition", "Concession", "Attribution"
    nucleus_id: int
    satellite_id: int
    connector_lexical: Optional[str]
    confidence: float


@dataclass
class DiscourseTree:
    raw_text: str
    edus: List[ElementaryDiscourseUnit]
    relations: List[RhetoricalRelation]
    root_nucleus_id: int


class DiscourseParser:
    """
    RST parser segmenting multi-clause sentences and paragraphs into
    discourse trees with nuclearity and rhetorical relation typing.
    """

    RELATION_CONNECTORS = {
        "Contrast": ["however", "but", "although", "whereas", "on the other hand", "conversely", "yet"],
        "Cause": ["because", "since", "therefore", "thus", "consequently", "as a result"],
        "Condition": ["if", "provided that", "unless", "assuming that"],
        "Concession": ["even though", "despite", "in spite of", "nevertheless"],
        "Attribution": ["said", "stated", "claimed", "reported", "argued", "believes"],
        "Elaboration": ["for example", "specifically", "in particular", "furthermore", "moreover"],
    }

    def segment_edus(self, text: str) -> List[ElementaryDiscourseUnit]:
        """Splits sentences or coordinated clauses into EDUs."""
        # Segmentation based on punctuation and discourse conjunctions
        pattern = r"(?<=[.!?])\s+|(?<=,)\s+(?=however|but|although|because|since|if|unless|while)\b"
        raw_units = re.split(pattern, text)

        edus: List[ElementaryDiscourseUnit] = []
        curr_offset = 0
        edu_counter = 0

        for unit in raw_units:
            unit_stripped = unit.strip()
            if not unit_stripped:
                continue
            idx = text.find(unit_stripped, curr_offset)
            if idx == -1:
                idx = curr_offset
            edus.append(
                ElementaryDiscourseUnit(
                    edu_id=edu_counter,
                    text=unit_stripped,
                    char_start=idx,
                    char_end=idx + len(unit_stripped),
                )
            )
            curr_offset = idx + len(unit_stripped)
            edu_counter += 1

        return edus

    def parse(self, text: str) -> DiscourseTree:
        edus = self.segment_edus(text)
        relations: List[RhetoricalRelation] = []

        if len(edus) <= 1:
            return DiscourseTree(
                raw_text=text,
                edus=edus,
                relations=[],
                root_nucleus_id=0 if edus else -1,
            )

        # Parse relations between consecutive EDUs
        for i in range(len(edus) - 1):
            left_edu = edus[i]
            right_edu = edus[i + 1]
            right_lower = right_edu.text.lower()

            detected_rel = "Elaboration"  # Default canonical relation
            matched_conn = None
            conf = 0.60

            for rel, conns in self.RELATION_CONNECTORS.items():
                for c in conns:
                    if right_lower.startswith(c) or f", {c}" in right_lower or f" {c} " in right_lower:
                        detected_rel = rel
                        matched_conn = c
                        conf = 0.88
                        break
                if matched_conn:
                    break

            # Nuclearity assignment
            if detected_rel in {"Contrast", "Elaboration", "Cause", "Condition", "Concession"}:
                # Left is usually Nucleus, Right is Satellite
                nuc_id = left_edu.edu_id
                sat_id = right_edu.edu_id
            else:
                nuc_id = left_edu.edu_id
                sat_id = right_edu.edu_id

            relations.append(
                RhetoricalRelation(
                    relation_name=detected_rel,
                    nucleus_id=nuc_id,
                    satellite_id=sat_id,
                    connector_lexical=matched_conn,
                    confidence=conf,
                )
            )

        return DiscourseTree(
            raw_text=text,
            edus=edus,
            relations=relations,
            root_nucleus_id=edus[0].edu_id if edus else -1,
        )
