"""
Indonesian Engine — Tokenization Skill
Handles standard tokenization while strictly preserving hyphenated reduplication (anak-anak, buku-buku),
pronominal enclitics (-ku, -mu, -nya), and formal abbreviations.
"""

import re
from typing import List

# Captures hyphenated reduplicated words (buku-buku), standard words, digits, and punctuation
INDONESIAN_WORD_RE = re.compile(r"[a-zA-Z]+(?:-[a-zA-Z]+)+|[a-zA-Z]+|\d+|[^\w\s]")

def tokenize_words(text: str) -> List[str]:
    """Tokenize Indonesian text preserving hyphenated reduplication."""
    if not text:
        return []
    tokens = INDONESIAN_WORD_RE.findall(text)
    return [t.strip() for t in tokens if t.strip()]

def split_sentences(text: str) -> List[str]:
    """Split text into sentences while respecting common Indonesian titles and abbreviations."""
    if not text:
        return []
    safe_text = re.sub(r"\b(Yth|Bpk|Dr|Drs|Ir|Prof|Sdr|Sdri|Ny|Tn|dll|dsb|dst)\.", r"\1<DOT>", text)
    raw = re.split(r"[.!?]+(?:\s+|$)", safe_text)
    sentences = []
    for s in raw:
        clean = s.replace("<DOT>", ".").strip()
        if clean:
            sentences.append(clean)
    return sentences

def is_reduplicated(token: str) -> bool:
    """Check if token is a hyphenated reduplicated form."""
    return "-" in token and len(token.split("-")) == 2 and all(part.isalpha() for part in token.split("-"))
