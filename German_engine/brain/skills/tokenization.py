"""
German Engine — Tokenization & Orthography Skill
Handles word tokenization, punctuation, abbreviations, compounds, and Swiss ss-normalization.
"""

import re
from typing import List, Dict, Any

ABBREVIATIONS = {
    "z.b.", "d.h.", "u.a.", "usw.", "etc.", "bzw.", "ca.", "dr.", "prof.",
    "str.", "nr.", "mglw.", "vgl.", "inkl.", "exkl.", "ggf.", "evtl."
}

def tokenize_words(text: str) -> List[str]:
    """Tokenize German text into words and punctuation tokens."""
    if not text:
        return []
    
    # Pattern matching words (including German umlauts and eszett), numbers, and individual punctuation
    pattern = r'[A-ZÄÖÜa-zäöüß]+|\d+(?:[.,]\d+)*|[^\w\s]'
    tokens = re.findall(pattern, text)
    return tokens

def split_sentences(text: str) -> List[str]:
    """Split German text into sentences respecting abbreviations."""
    if not text:
        return []
    
    # Replace period in common abbreviations with placeholder while preserving casing
    protected_text = text
    for abbr in ABBREVIATIONS:
        pattern = re.compile(r'\b' + re.escape(abbr), re.IGNORECASE)
        protected_text = pattern.sub(lambda m: m.group(0).replace(".", "§DOT§"), protected_text)
        
    # Also protect titles like Dr. Schmidt, Prof. Müller
    protected_text = re.sub(r'\b(Dr|Prof|Hr|Fr)\.\s+', lambda m: m.group(1) + '§DOT§ ', protected_text)
    
    # Split on sentence terminals: . ! ?
    raw_sentences = re.split(r'(?<=[.!?])\s+', protected_text)
    
    sentences = []
    for s in raw_sentences:
        s_restored = s.replace("§DOT§", ".").strip()
        if s_restored:
            sentences.append(s_restored)
            
    return sentences

def normalize_orthography(text: str, swiss_mode: bool = False) -> str:
    """
    Normalize German text.
    If swiss_mode is True, converts 'ß' to 'ss'.
    """
    if swiss_mode:
        text = text.replace("ß", "ss")
    return text

def detect_compounds(token: str) -> List[str]:
    """
    Heuristic compound splitter for German substantive compounds.
    Recognizes common Fugenlaute (-s-, -en-, -er-).
    """
    fugen = ["s", "es", "en", "n", "er"]
    # If token is sufficiently long, attempt heuristic segmentation
    if len(token) > 10 and token[0].isupper():
        for fuge in fugen:
            idx = token.lower().find(fuge, 4)
            if idx != -1 and idx + len(fuge) < len(token) - 3:
                first = token[:idx]
                second = token[idx + len(fuge):]
                return [first, second]
    return [token]
