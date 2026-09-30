"""
Portuguese Tokenizer: Handles Unicode normalization, hyphenated enclitics/mesoclitics,
prepositional contractions, and character span tracking.
"""

from typing import List, Dict, Any, Tuple
import re
import unicodedata


class PortugueseTokenizer:
    """
    Tokenizer for Portuguese text with support for hyphenated clitics and contractions.
    """

    CLITIC_SUFFIXES = [
        "-me", "-te", "-se", "-o", "-a", "-lhe", "-nos", "-vos", "-os", "-as", "-lhes",
        "-lo", "-la", "-los", "-las", "-no", "-na", "-nos", "-nas"
    ]

    CONTRACTION_MAP = {
        "do": ("de", "o"), "da": ("de", "a"), "dos": ("de", "os"), "das": ("de", "as"),
        "dum": ("de", "um"), "duma": ("de", "uma"), "duns": ("de", "uns"), "dumas": ("de", "umas"),
        "dele": ("de", "ele"), "dela": ("de", "ela"), "deles": ("de", "eles"), "delas": ("de", "elas"),
        "deste": ("de", "este"), "desta": ("de", "esta"), "destes": ("de", "estes"), "destas": ("de", "estas"),
        "desse": ("de", "esse"), "dessa": ("de", "essa"), "desses": ("de", "esses"), "dessas": ("de", "essas"),
        "daquele": ("de", "aquele"), "daquela": ("de", "aquela"), "daqueles": ("de", "aqueles"), "daquelas": ("de", "aquelas"),
        "disto": ("de", "isto"), "disso": ("de", "isso"), "daquilo": ("de", "aquilo"),
        "no": ("em", "o"), "na": ("em", "a"), "nos": ("em", "os"), "nas": ("em", "as"),
        "num": ("em", "um"), "numa": ("em", "uma"), "nuns": ("em", "uns"), "numas": ("em", "umas"),
        "nele": ("em", "ele"), "nela": ("em", "ela"), "neles": ("em", "eles"), "nelas": ("em", "elas"),
        "neste": ("em", "este"), "nesta": ("em", "esta"), "nestes": ("em", "estes"), "nestas": ("em", "estas"),
        "nesse": ("em", "esse"), "nessa": ("em", "essa"), "nesses": ("em", "esses"), "nessas": ("em", "essas"),
        "naquele": ("em", "aquele"), "naquela": ("em", "aquela"), "naqueles": ("em", "aqueles"), "naquelas": ("em", "aquelas"),
        "nisto": ("em", "isto"), "nisso": ("em", "isso"), "naquilo": ("em", "aquilo"),
        "ao": ("a", "o"), "aos": ("a", "os"), "à": ("a", "a"), "às": ("a", "as"),
        "àquele": ("a", "aquele"), "àquela": ("a", "aquela"), "àqueles": ("a", "aqueles"), "àquelas": ("a", "aquelas"),
        "àquilo": ("a", "aquilo"),
        "pelo": ("por", "o"), "pela": ("por", "a"), "pelos": ("por", "os"), "pelas": ("por", "as")
    }

    def __init__(self):
        self.punct_pattern = re.compile(r"([,\.!?;:\"'()\[\]{}—])")

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text into a clean list of lexical tokens.
        Preserves internal hyphens for clitics (e.g. 'disse-me', 'fazê-lo').
        """
        if not text:
            return []
        
        normalized = unicodedata.normalize("NFC", text.strip())
        spaced = self.punct_pattern.sub(r" \1 ", normalized)
        tokens = [t for t in spaced.split() if t]
        return tokens

    def tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """Tokenizes text while tracking start and end character offsets."""
        if not text:
            return []

        normalized = unicodedata.normalize("NFC", text)
        tokens = self.tokenize(normalized)
        spans = []
        current_idx = 0

        for token in tokens:
            idx = normalized.find(token, current_idx)
            if idx != -1:
                start = idx
                end = idx + len(token)
                current_idx = end
            else:
                start = current_idx
                end = current_idx + len(token)
            spans.append({
                "token": token,
                "start": start,
                "end": end
            })
        return spans

    def split_clitic(self, token: str) -> Tuple[str, str | None]:
        """
        Splits a verb token into stem and hyphenated clitic if present.
        Example: 'disse-me' -> ('disse', 'me'), 'fazê-lo' -> ('fazê', 'lo')
        """
        for sfx in self.CLITIC_SUFFIXES:
            if token.endswith(sfx) and len(token) > len(sfx):
                base_stem = token[:-len(sfx)]
                clitic = sfx.lstrip("-")
                return base_stem, clitic
        return token, None

    def expand_contraction(self, token: str) -> Tuple[str, str] | None:
        """
        Expands a prepositional contraction into constituent words.
        Example: 'do' -> ('de', 'o'), 'na' -> ('em', 'a'), 'à' -> ('a', 'a')
        """
        low = token.lower()
        return self.CONTRACTION_MAP.get(low)
