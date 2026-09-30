"""
pos_tagging.py - Sequence labeling across Penn Treebank 36 and Universal Dependencies 17 tagsets.
Disambiguates VBG/VBN, NN/VB, IN/RB, and determiners.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Union

from .tokenization import Token

PENN_TO_UD = {
    "NN": "NOUN", "NNS": "NOUN", "NNP": "PROPN", "NNPS": "PROPN",
    "VB": "VERB", "VBD": "VERB", "VBG": "VERB", "VBN": "VERB", "VBP": "VERB", "VBZ": "VERB",
    "MD": "AUX", "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ",
    "RB": "ADV", "RBR": "ADV", "RBS": "ADV", "WRB": "ADV",
    "PRP": "PRON", "PRP$": "PRON", "WP": "PRON", "WP$": "PRON",
    "DT": "DET", "WDT": "DET", "PDT": "DET",
    "IN": "ADP", "TO": "ADP",
    "CC": "CCONJ",
    "CD": "NUM",
    "UH": "INTJ",
    "POS": "PART", "RP": "ADP",
    ".": "PUNCT", ",": "PUNCT", ":": "PUNCT", "``": "PUNCT", "''": "PUNCT", "(": "PUNCT", ")": "PUNCT"
}

# Closed-class lexicon
CLOSED_CLASSES = {
    "determiners": {"the", "a", "an", "this", "that", "these", "those", "every", "each", "all", "some", "any", "no"},
    "pronouns": {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "their", "our", "its", "who", "whom", "whose"},
    "prepositions": {"in", "on", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "over", "under"},
    "conjunctions": {"and", "but", "or", "nor", "so", "yet", "for"},
    "modals": {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
}


@dataclass
class TaggedToken:
    token: Token
    penn_tag: str
    ud_tag: str

    def __getitem__(self, item):
        if item == "token":
            return self.token.text if isinstance(self.token, Token) else str(self.token)
        if item == "penn_tag":
            return self.penn_tag
        if item == "ud_tag":
            return self.ud_tag
        raise KeyError(item)


class EnglishPOSTagger:
    """
    Morphosyntactic Part-of-Speech tagger mapping tokens to Penn 36 and UD 17 tags.
    """

    def tag_tokens(self, tokens: Union[List[Token], List[str]]) -> List[TaggedToken]:
        # Convert str to Token if needed
        norm_tokens: List[Token] = []
        for i, t in enumerate(tokens):
            if isinstance(t, Token):
                norm_tokens.append(t)
            else:
                s_tok = str(t)
                is_w = bool(re.match(r"^[A-Za-z0-9]+$", s_tok))
                norm_tokens.append(Token(text=s_tok, char_start=0, char_end=len(s_tok), is_word=is_w))

        tagged: List[TaggedToken] = []
        for i, token_obj in enumerate(norm_tokens):
            token_str = token_obj.text
            lower = token_str.lower()
            prev_token = norm_tokens[i - 1].text.lower() if i > 0 else ""
            next_token = norm_tokens[i + 1].text.lower() if i < len(norm_tokens) - 1 else ""

            penn_tag = self._predict_tag(token_str, lower, prev_token, next_token)
            ud_tag = PENN_TO_UD.get(penn_tag, "X")

            tagged.append(TaggedToken(token=token_obj, penn_tag=penn_tag, ud_tag=ud_tag))
        return tagged

    def _predict_tag(self, token: str, lower: str, prev: str, nxt: str) -> str:
        if token in {".", "!", "?"}:
            return "."
        if token in {",", ";", ":"}:
            return ","
        if token in {"(", ")", "[", "]"}:
            return "("
        if lower in CLOSED_CLASSES["determiners"]:
            return "DT"
        if lower in CLOSED_CLASSES["modals"]:
            return "MD"
        if lower in CLOSED_CLASSES["pronouns"]:
            if lower in {"my", "your", "his", "her", "its", "our", "their"}:
                return "PRP$"
            if lower in {"who", "whom", "whose"}:
                return "WP"
            return "PRP"
        if lower in CLOSED_CLASSES["conjunctions"]:
            return "CC"
        if lower in CLOSED_CLASSES["prepositions"]:
            return "IN"
        if lower == "to":
            return "TO"

        # Numerical tokens
        if re.match(r"^\d+(?:\.\d+)?$", token):
            return "CD"

        # Proper Nouns
        if token[0].isupper() and prev not in {"", ".", "!", "?"}:
            return "NNP"

        # Suffix morphology rules
        if lower.endswith("ly"):
            return "RB"
        if lower.endswith("ing"):
            return "VBG"
        if lower.endswith("ed"):
            return "VBD" if nxt in {"the", "a", "an", "to"} else "VBN"
        if lower.endswith(("tion", "sion", "ness", "ment", "ity", "ance", "ence")):
            return "NN"
        if lower.endswith(("able", "ible", "ous", "ive", "ful", "less", "al")):
            return "JJ"
        # Common verbs
        common_vbz = {"jumps", "runs", "walks", "talks", "eats", "thinks", "writes", "reads", "learns", "executes", "converges", "speaks", "operates", "causes", "gives", "is", "has", "does"}
        if lower in common_vbz:
            return "VBZ"

        if lower.endswith("s") and not lower.endswith("ss"):
            if prev in {"he", "she", "it"} or nxt in CLOSED_CLASSES["prepositions"] or nxt in {"the", "a", "an"}:
                return "VBZ"
            return "NNS"

        # Position heuristics
        if prev in CLOSED_CLASSES["determiners"] or prev in {"my", "your", "his", "her", "its", "our", "their"}:
            if nxt in CLOSED_CLASSES["determiners"] or nxt in {".", ",", ";"} or not nxt:
                return "NN"
            return "JJ"

        if prev in {"i", "you", "he", "she", "it", "we", "they"} or prev in CLOSED_CLASSES["modals"]:
            return "VB"

        return "NN"
