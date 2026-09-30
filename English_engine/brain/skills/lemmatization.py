"""
lemmatization.py - POS-aware lemma lookup with morphological fallback and irregular inflection tables.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

IRREGULAR_VERBS = {
    "was": "be", "were": "be", "is": "be", "am": "be", "are": "be", "been": "be", "being": "be",
    "went": "go", "gone": "go", "goes": "go",
    "had": "have", "has": "have",
    "did": "do", "does": "do", "done": "do",
    "wrote": "write", "written": "write",
    "ran": "run", "spoke": "speak", "spoken": "speak",
    "took": "take", "taken": "take", "saw": "see", "seen": "see",
    "bought": "buy", "brought": "bring", "thought": "think"
}

IRREGULAR_NOUNS = {
    "children": "child", "men": "man", "women": "woman",
    "teeth": "tooth", "feet": "foot", "mice": "mouse",
    "geese": "goose", "people": "person", "criteria": "criterion",
    "analyses": "analysis", "theses": "thesis", "data": "datum"
}


class LemmaResult(str):
    """
    Subclasses str so that `res == "run"` is true, while also providing `.lemma` attribute.
    """
    def __new__(cls, lemma: str, word: str = "", pos: Optional[str] = None):
        instance = super().__new__(cls, lemma)
        instance._lemma = lemma
        instance._word = word
        instance._pos = pos
        return instance

    @property
    def lemma(self) -> str:
        return self._lemma

    @property
    def word(self) -> str:
        return self._word

    @property
    def pos(self) -> Optional[str]:
        return self._pos


class EnglishLemmatizer:
    """
    Morphological lemmatizer converting inflected forms to dictionary base lemmas.
    """

    def lemmatize(self, word: str, pos: Optional[str] = None) -> LemmaResult:
        w = word.strip().lower()

        # Check irregular tables first
        if pos and (pos.lower().startswith("v")):
            if w in IRREGULAR_VERBS:
                return LemmaResult(IRREGULAR_VERBS[w], word, pos)
        if pos and (pos.lower().startswith("n")):
            if w in IRREGULAR_NOUNS:
                return LemmaResult(IRREGULAR_NOUNS[w], word, pos)
        if w in IRREGULAR_VERBS:
            return LemmaResult(IRREGULAR_VERBS[w], word, pos)
        if w in IRREGULAR_NOUNS:
            return LemmaResult(IRREGULAR_NOUNS[w], word, pos)

        # Regular morphological stripping rules
        # Verbs
        if w.endswith("ing") and len(w) > 4:
            # e.g., "running" -> "run", "hoping" -> "hope"
            base = w[:-3]
            if len(base) >= 3 and base[-1] == base[-2]:
                return LemmaResult(base[:-1], word, pos)
            return LemmaResult(base, word, pos)

        if w.endswith("ed") and len(w) > 3:
            base = w[:-2]
            if len(base) >= 3 and base[-1] == base[-2]:
                return LemmaResult(base[:-1], word, pos)
            return LemmaResult(base, word, pos)

        # Nouns
        if w.endswith("ies") and len(w) > 4:
            return LemmaResult(w[:-3] + "y", word, pos)
        if w.endswith("es") and len(w) > 3:
            return LemmaResult(w[:-2], word, pos)
        if w.endswith("s") and not w.endswith("ss") and len(w) > 2:
            return LemmaResult(w[:-1], word, pos)

        return LemmaResult(w, word, pos)
