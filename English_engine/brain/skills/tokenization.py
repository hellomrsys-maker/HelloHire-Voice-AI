"""
tokenization.py - Word/sentence splitting, subword BPE, and multilingual tokenization.
Supports character-level, word-level, regex clitic-aware tokenization, and UniversalSubwordTokenizer.
"""

from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional, Iterator

# Clitic splitting regex for English: splits "don't" -> "do", "n't"; "we'll" -> "we", "'ll"
CLITIC_RE = re.compile(r"(?i)\b(?:can|won|shan)'t\b|'(?:[dms]|re|ve|ll)\b|n't\b|[\w]+|[^\s\w]")
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'“])")


@dataclass
class Token:
    text: str
    char_start: int
    char_end: int
    is_word: bool

    def __str__(self) -> str:
        return self.text

    def __getitem__(self, item):
        if item == "text":
            return self.text
        if item == "char_start":
            return self.char_start
        if item == "char_end":
            return self.char_end
        if item == "is_word":
            return self.is_word
        raise KeyError(item)


class EnglishTokenizer:
    """
    Production-grade English tokenizer supporting word, sentence, and subword BPE levels.
    """

    def __init__(self, vocab: Optional[Dict[str, int]] = None):
        self.vocab = vocab or {}
        self._special_tokens = ["<PAD>", "<UNK>", "<BOS>", "<EOS>", "<SEP>"]

    def split_sentences(self, text: str) -> List[str]:
        """Splits raw text into sentences while respecting abbreviation boundaries."""
        if not text or not text.strip():
            return []
        raw_sentences = SENTENCE_BOUNDARY_RE.split(text.strip())
        refined = []
        abbrevs = {"dr.", "mr.", "mrs.", "ms.", "prof.", "e.g.", "i.e.", "vs.", "etc."}
        buf = ""
        for s in raw_sentences:
            if buf:
                buf += " " + s
            else:
                buf = s
            last_word = buf.strip().split()[-1].lower() if buf.strip() else ""
            if last_word not in abbrevs:
                refined.append(buf.strip())
                buf = ""
        if buf:
            refined.append(buf.strip())
        return refined

    def tokenize_words(self, text: str) -> List[str]:
        """Clitic-aware word and punctuation tokenization returning strings."""
        normalized = unicodedata.normalize("NFC", text)
        return CLITIC_RE.findall(normalized)

    def tokenize(self, text: str) -> List[Token]:
        """Tokenizes text into a list of Token objects with exact character spans."""
        normalized = unicodedata.normalize("NFC", text)
        tokens: List[Token] = []
        for m in CLITIC_RE.finditer(normalized):
            t_str = m.group(0)
            is_word = bool(re.match(r"^[A-Za-z0-9]+$", t_str))
            tokens.append(
                Token(
                    text=t_str,
                    char_start=m.start(),
                    char_end=m.end(),
                    is_word=is_word,
                )
            )
        return tokens

    def subword_bpe(self, word: str) -> List[str]:
        """Subword greedy morpheme/character breakdown."""
        if len(word) <= 3:
            return [word]
        prefixes = ["un", "re", "dis", "pre", "post", "mis", "in", "im", "non"]
        suffixes = ["ing", "ed", "ness", "tion", "sion", "ment", "able", "ible", "ly", "ful", "less", "est", "er", "s"]

        w = word.lower()
        subwords = []
        for p in prefixes:
            if w.startswith(p) and len(w) > len(p) + 2:
                subwords.append(p)
                w = w[len(p):]
                break

        rest_suffix = None
        for s in sorted(suffixes, key=len, reverse=True):
            if w.endswith(s) and len(w) > len(s) + 1:
                rest_suffix = s
                w = w[:-len(s)]
                break

        subwords.append(w)
        if rest_suffix:
            subwords.append("##" + rest_suffix)
        return subwords
