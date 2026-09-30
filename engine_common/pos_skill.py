"""
pos_skill.py — Shared Neural POS-Tagging Skill for all engines.
================================================================

Provides ``NeuralPOSSkill`` — a drop-in part-of-speech tagger that every engine
can use. It loads that engine's trained UD POS checkpoint
(``checkpoints/<engine>_pos_tagger.pt``) and assigns one of the 17 Universal POS
tags to each word. When no checkpoint exists (or torch is unavailable), it falls
back to a deterministic, language-neutral heuristic tagger so the skill is always
callable and never breaks the pipeline.

This is what makes the UD-trained POS capability actually flow into the engines:
the base orchestrator calls this skill and surfaces the tags in its output.
"""

from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .ud_pos_data import UPOS_TAGS

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class POSResult:
    words: List[str]
    tags: List[str]            # UD-17 tag per word
    source: str                # "neural" | "heuristic"
    checkpoint: Optional[str] = None
    val_token_accuracy: Optional[float] = None

    def pairs(self) -> List[Tuple[str, str]]:
        return list(zip(self.words, self.tags))


# Language-neutral heuristic fallback: closed-class hints (Latin) + shape rules.
_PUNCT = set(".,;:!?()[]{}\"'`—–…،。！？")
_LATIN_FUNCTION = {
    "the": "DET", "a": "DET", "an": "DET", "this": "DET", "that": "DET",
    "and": "CCONJ", "or": "CCONJ", "but": "CCONJ",
    "in": "ADP", "on": "ADP", "at": "ADP", "of": "ADP", "to": "ADP", "for": "ADP",
    "with": "ADP", "from": "ADP", "by": "ADP",
    "i": "PRON", "you": "PRON", "he": "PRON", "she": "PRON", "it": "PRON",
    "we": "PRON", "they": "PRON", "me": "PRON", "him": "PRON", "her": "PRON",
    "is": "AUX", "are": "AUX", "was": "AUX", "were": "AUX", "be": "AUX",
    "am": "AUX", "been": "AUX", "will": "AUX", "would": "AUX", "can": "AUX",
    "could": "AUX", "should": "AUX", "must": "AUX", "may": "AUX", "might": "AUX",
}


def _heuristic_tag(words: List[str]) -> List[str]:
    tags: List[str] = []
    for i, w in enumerate(words):
        wl = w.lower()
        if all(ch in _PUNCT for ch in w) and w:
            tags.append("PUNCT")
        elif re.match(r"^\d+([.,]\d+)?$", w):
            tags.append("NUM")
        elif wl in _LATIN_FUNCTION:
            tags.append(_LATIN_FUNCTION[wl])
        elif wl.endswith(("ing", "ed", "ise", "ize", "ate")):
            tags.append("VERB")
        elif wl.endswith(("ly",)):
            tags.append("ADV")
        elif wl.endswith(("tion", "ment", "ness", "ity", "ism")):
            tags.append("NOUN")
        elif wl.endswith(("able", "ible", "ous", "ive", "ful", "al")):
            tags.append("ADJ")
        elif w[:1].isupper() and i > 0:
            tags.append("PROPN")
        else:
            tags.append("NOUN")
    return tags


class NeuralPOSSkill:
    """POS tagging skill: neural (from checkpoint) with heuristic fallback."""

    def __init__(self, engine_dir: str, workspace_root: Optional[str] = None) -> None:
        self.engine_dir = engine_dir
        root = workspace_root or WORKSPACE_ROOT
        self.checkpoint_path = os.path.join(root, "checkpoints",
                                            f"{engine_dir.lower()}_pos_tagger.pt")
        self._loaded = None
        self.mode = "heuristic"
        self.val_token_accuracy = None
        if os.path.exists(self.checkpoint_path):
            try:
                from .pos_tagger import LoadedPOSTagger
                self._loaded = LoadedPOSTagger(self.checkpoint_path)
                self.mode = "neural"
                self.val_token_accuracy = self._loaded.val_token_accuracy
            except Exception:
                self._loaded = None
                self.mode = "heuristic"

    @staticmethod
    def _split(text: str) -> List[str]:
        # Split words and standalone punctuation (Unicode-aware).
        return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

    def tag(self, text_or_words) -> POSResult:
        words = text_or_words if isinstance(text_or_words, list) else self._split(text_or_words)
        if not words:
            return POSResult(words=[], tags=[], source=self.mode,
                             checkpoint=self.checkpoint_path if self.mode == "neural" else None,
                             val_token_accuracy=self.val_token_accuracy)
        if self._loaded is not None:
            try:
                tags = self._loaded.tag(words)
                return POSResult(words=words, tags=tags, source="neural",
                                 checkpoint=self.checkpoint_path,
                                 val_token_accuracy=self.val_token_accuracy)
            except Exception:
                pass
        return POSResult(words=words, tags=_heuristic_tag(words), source="heuristic")
