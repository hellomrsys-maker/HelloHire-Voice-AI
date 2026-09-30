"""
Hindustani Sentence Parsing Skill.
Analyzes SOV (Subject-Object-Verb) constituent order, postpositional phrases,
and identifies ergative vs. nominative clause structure.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class HindustaniSentenceStructure:
    has_subject: bool
    subject_tokens: List[str]
    is_ergative_subject: bool
    object_tokens: List[str]
    has_ko_marked_object: bool
    verb_tokens: List[str]
    is_canonical_sov: bool
    postpositions: List[str]


class HindustaniParser:
    """
    Parser for Hindustani clauses evaluating head-final SOV structure and case markers.
    """

    POSTPOSITIONS = {
        "ne", "ko", "se", "mein", "par", "ka", "ke", "ki", "tak",
        "ने", "को", "से", "में", "पर", "का", "के", "की", "तक"
    }

    ERGATIVE_MARKERS = {"ne", "ने", "maine", "tune", "usne", "isne", "humne", "tumne", "aapne", "unhonne", "inhonne", "मैंने", "तूने", "उसने", "इसने", "हमने", "तुमने", "आपने", "उन्होंने", "इन्होंने"}

    def parse(self, tagged_tokens: List[Tuple[str, str]]) -> HindustaniSentenceStructure:
        if not tagged_tokens:
            return HindustaniSentenceStructure(
                has_subject=False, subject_tokens=[], is_ergative_subject=False,
                object_tokens=[], has_ko_marked_object=False, verb_tokens=[],
                is_canonical_sov=False, postpositions=[]
            )

        # Filter out trailing punctuation
        words = [t[0] for t in tagged_tokens if t[1] != "PUNCT"]
        tags = [t[1] for t in tagged_tokens if t[1] != "PUNCT"]

        # Collect postpositions
        found_postps: List[str] = [w for w in words if w.lower() in self.POSTPOSITIONS]

        # Find verbal cluster (usually at the end in SOV)
        verb_indices = [i for i, tag in enumerate(tags) if tag in {"VERB", "AUX"}]
        verb_tokens = [words[i] for i in verb_indices]

        # Check SOV: is the last content word a verb or auxiliary?
        is_sov = len(verb_indices) > 0 and (verb_indices[-1] >= len(words) - 2)

        # Segment subject and object
        subject_tokens: List[str] = []
        object_tokens: List[str] = []
        is_erg = False

        if len(words) > 0:
            # Check for ergative marker in first half of sentence
            first_verb_idx = verb_indices[0] if verb_indices else len(words)
            pre_verbal = words[:first_verb_idx]

            # Look for postpositional boundary of subject
            ne_idx = -1
            for i, w in enumerate(pre_verbal):
                if w.lower() in {"ne", "ने"}:
                    ne_idx = i
                    break

            if ne_idx != -1:
                subject_tokens = pre_verbal[:ne_idx + 1]
                object_tokens = pre_verbal[ne_idx + 1:]
                is_erg = True
            elif len(pre_verbal) > 0 and pre_verbal[0].lower() in self.ERGATIVE_MARKERS:
                subject_tokens = [pre_verbal[0]]
                object_tokens = pre_verbal[1:]
                is_erg = True
            else:
                # Default heuristic: first 1 or 2 tokens form subject
                if len(pre_verbal) >= 2:
                    subject_tokens = pre_verbal[:1]
                    object_tokens = pre_verbal[1:]
                else:
                    subject_tokens = pre_verbal

        has_ko = any(w.lower() in {"ko", "को"} for w in object_tokens)

        return HindustaniSentenceStructure(
            has_subject=len(subject_tokens) > 0,
            subject_tokens=subject_tokens,
            is_ergative_subject=is_erg,
            object_tokens=object_tokens,
            has_ko_marked_object=has_ko,
            verb_tokens=verb_tokens,
            is_canonical_sov=is_sov,
            postpositions=found_postps
        )
