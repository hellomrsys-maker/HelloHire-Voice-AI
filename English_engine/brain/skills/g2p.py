"""
g2p.py - Grapheme-to-Phoneme (G2P) conversion front-end for English TTS.
Maps English spelling to ARPAbet phoneme sequences and resolves homographs.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Lexicon of common irregulars and homographs
HOMOGRAPH_LEXICON = {
    "read": {"VBD": "R EH1 D", "VBN": "R EH1 D", "VB": "R IY1 D", "VBP": "R IY1 D", "NN": "R IY1 D"},
    "lead": {"NN": "L EH1 D", "VB": "L IY1 D", "VBP": "L IY1 D"},
    "live": {"VBP": "L IH1 V", "VB": "L IH1 V", "JJ": "L AY1 V"},
    "tear": {"VB": "T EH1 R", "NN": "T IH1 R"},
    "wind": {"NN": "W IH1 N D", "VB": "W AY1 N D"},
    "bass": {"NN": "B EY1 S", "JJ": "B AE1 S"},
    "thought": {"*": "TH AO1 T"},
}

BASIC_G2P_MAP = {
    "a": "AE1", "b": "B", "c": "K", "d": "D", "e": "EH1", "f": "F", "g": "G",
    "h": "HH", "i": "IH1", "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N",
    "o": "AA1", "p": "P", "q": "K", "r": "R", "s": "S", "t": "T", "u": "AH1",
    "v": "V", "w": "W", "x": "K S", "y": "Y", "z": "Z"
}

DIGRAPH_MAP = {
    "th": "TH", "sh": "SH", "ch": "CH", "ph": "F", "wh": "W", "ck": "K",
    "ee": "IY1", "oo": "UW1", "ea": "IY1", "ai": "EY1", "oa": "OW1", "ou": "AW1"
}


@dataclass
class G2PResult:
    word: str
    phonemes: List[str]

    def __iter__(self):
        return iter(self.phonemes)


class EnglishG2PConverter:
    """
    Grapheme-to-Phoneme converter for speech synthesis and phonological analysis.
    """

    def convert_word(self, word: str, pos: Optional[str] = None) -> G2PResult:
        phonemes = self.word_to_phonemes(word, pos)
        return G2PResult(word=word, phonemes=phonemes)

    def word_to_phonemes(self, word: str, pos: Optional[str] = None) -> List[str]:
        w = word.strip().lower()
        # 1. Homograph / specific irregular lookup
        if w in HOMOGRAPH_LEXICON:
            options = HOMOGRAPH_LEXICON[w]
            if pos and pos in options:
                return options[pos].split()
            if "*" in options:
                return options["*"].split()
            return next(iter(options.values())).split()

        # 2. Digraph and letter-to-sound rule application
        phonemes = []
        i = 0
        n = len(w)
        while i < n:
            if i + 1 < n:
                pair = w[i:i + 2]
                if pair in DIGRAPH_MAP:
                    phonemes.extend(DIGRAPH_MAP[pair].split())
                    i += 2
                    continue
            ch = w[i]
            if ch in BASIC_G2P_MAP:
                phonemes.extend(BASIC_G2P_MAP[ch].split())
            i += 1

        return phonemes
