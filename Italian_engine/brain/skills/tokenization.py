"""
Italian Engine — Tokenization Skill
Handles standard tokenization with Italian apostrophe elisions (l'amico -> [l', amico] or [l'amico]),
contractions, and punctuation preservation.
"""

import re
from typing import List

# Regex capturing Italian words, elided prefixes (l', un', d', c', all', dell'), and punctuation
ITALIAN_WORD_RE = re.compile(r"[a-zA-ZÀ-ÿ]+'[a-zA-ZÀ-ÿ]+|[a-zA-ZÀ-ÿ]+'|[a-zA-ZÀ-ÿ]+|\d+|[^\w\s]")

def tokenize_words(text: str) -> List[str]:
    """Tokenize Italian text preserving elisions and contractions."""
    if not text:
        return []
    tokens = ITALIAN_WORD_RE.findall(text)
    return [t.strip() for t in tokens if t.strip()]

def split_sentences(text: str) -> List[str]:
    """Split Italian text into sentences while respecting common abbreviations."""
    if not text:
        return []
    # Avoid splitting on common titles (Dott., Prof., Sig., Ing., Avv.)
    safe_text = re.sub(r"\b(Dott|Prof|Sig|Ing|Avv|Cap)\.", r"\1<DOT>", text)
    raw_sentences = re.split(r"[.!?]+(?:\s+|$)", safe_text)
    sentences = []
    for s in raw_sentences:
        clean = s.replace("<DOT>", ".").strip()
        if clean:
            sentences.append(clean)
    return sentences

def split_elision(token: str) -> List[str]:
    """
    Split an elided token into article/particle and base noun/verb if applicable.
    Example: "l'amico" -> ["l'", "amico"], "c'è" -> ["c'", "è"], "d'accordo" -> ["d'", "accordo"]
    """
    if "'" in token:
        parts = token.split("'", 1)
        return [parts[0] + "'", parts[1]]
    return [token]
