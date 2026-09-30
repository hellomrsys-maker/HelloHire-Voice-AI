"""
Indonesian Engine — Reduplication Engine Skill
Synthesizes and analyzes Indonesian reduplication:
- Full reduplication (dwilingga): anak-anak, buku-buku
- Sound-shift / imitative (dwilingga salin suara): sayur-mayur, bolak-balik
- Partial collective (dwipurwa): pepohonan, dedaunan
- Invariable lexical roots: kupu-kupu, laba-laba
"""

from typing import Dict, Any, Optional

IMITATIVE_PAIRS = {
    "sayur": "sayur-mayur",
    "balik": "bolak-balik",
    "warna": "warna-warni",
    "ramah": "ramah-tamah",
    "gerak": "gerak-gerik",
    "lauk": "lauk-pauk"
}

PARTIAL_COLLECTIVES = {
    "pohon": "pepohonan",
    "daun": "dedaunan",
    "rumput": "rerumputan"
}

LEXICALIZED_INVARIABLE = {
    "kupu-kupu", "laba-laba", "pura-pura", "kura-kura", "paru-paru", "cita-cita", "tiba-tiba", "sia-sia"
}

def reduplicate_word(root: str, redup_type: str = "full") -> str:
    """Synthesize reduplicated form for a root."""
    r = root.lower().strip()
    if redup_type == "imitative" and r in IMITATIVE_PAIRS:
        return IMITATIVE_PAIRS[r]
    if redup_type == "partial" and r in PARTIAL_COLLECTIVES:
        return PARTIAL_COLLECTIVES[r]
    # Default: full hyphenated reduplication
    return f"{r}-{r}"

def analyze_reduplication(token: str) -> Dict[str, Any]:
    """Analyze reduplicated token structure and semantics."""
    t = token.lower().strip()
    if t in LEXICALIZED_INVARIABLE:
        return {
            "is_reduplicated": True,
            "type": "lexicalized_invariable",
            "base_root": t.split("-")[0],
            "plurality": False,
            "valid": True
        }
        
    for base, form in IMITATIVE_PAIRS.items():
        if t == form:
            return {
                "is_reduplicated": True,
                "type": "imitative_sound_shift",
                "base_root": base,
                "plurality": True,
                "valid": True
            }
            
    for base, form in PARTIAL_COLLECTIVES.items():
        if t == form:
            return {
                "is_reduplicated": True,
                "type": "partial_collective",
                "base_root": base,
                "plurality": True,
                "valid": True
            }
            
    if "-" in t:
        parts = t.split("-")
        if len(parts) == 2 and parts[0] == parts[1]:
            return {
                "is_reduplicated": True,
                "type": "full_dwilingga",
                "base_root": parts[0],
                "plurality": True,
                "valid": True
            }
            
    return {
        "is_reduplicated": False,
        "type": "none",
        "base_root": t,
        "plurality": False,
        "valid": True
    }
