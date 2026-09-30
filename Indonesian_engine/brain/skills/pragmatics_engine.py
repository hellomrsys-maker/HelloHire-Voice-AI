"""
Indonesian Engine — Pragmatics Engine Skill
Evaluates social deixis (Bapak/Ibu vs Kamu/Anda), surat resmi protocol, and dialect register adaptation.
"""

import json
import os
from typing import Dict, Any, List

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
PRAG_FILE = os.path.join(RULES_DIR, "pragmatic_register_matrix.json")

def load_pragmatic_matrix() -> Dict[str, Any]:
    if os.path.exists(PRAG_FILE):
        with open(PRAG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def classify_register(text: str) -> Dict[str, Any]:
    """Classify Indonesian text as 'formal' (Bahasa Baku) or 'informal' (Bahasa Gaul)."""
    t_clean = text.lower()
    
    formal_markers = ["dengan hormat", "hormat kami", "bapak", "ibu", "saudara", "saudari", "terima kasih", "sehubungan"]
    informal_markers = ["nggak", "gak", "kagak", "banget", "udah", "belom", "gue", "lu", "dong", "sih", "kok", "deh", "bikin"]
    
    f_score = sum(1 for m in formal_markers if m in t_clean)
    i_score = sum(1 for m in informal_markers if m in t_clean)
    
    if f_score > i_score:
        reg = "formal"
    elif i_score > f_score:
        reg = "informal"
    else:
        reg = "neutral"
        
    return {
        "register": reg,
        "formal_score": f_score,
        "informal_score": i_score
    }

def format_salutation(title: str, recipient_name: str, formal: bool = True) -> str:
    """Format formal Indonesian salutation."""
    if not formal:
        return f"Halo {recipient_name}," if recipient_name else "Halo kawan,"
        
    t = title.strip() if title else "Bapak/Ibu"
    if recipient_name:
        return f"Yang terhormat {t} {recipient_name},"
    return "Dengan hormat,"

def format_closing(formal: bool = True) -> str:
    """Format formal Indonesian closing formula."""
    if formal:
        return "Demikian surat ini kami sampaikan. Atas perhatian Bapak/Ibu, kami ucapkan terima kasih.\n\nHormat kami,"
    return "Sampai jumpa dan salam hangat."

def adapt_gaul_to_baku(text: str) -> str:
    """Normalize informal Jakartan slang (Bahasa Gaul) to standard formal Bahasa Baku."""
    matrix = load_pragmatic_matrix()
    mappings = matrix.get("dialect_mappings_gaul_to_baku", {})
    
    words = text.split()
    adapted_words = []
    for w in words:
        pfx = ""
        sfx = ""
        core = w
        while core and core[0] in ".,!?;:\"'()«»":
            pfx += core[0]
            core = core[1:]
        while core and core[-1] in ".,!?;:\"'()«»":
            sfx = core[-1] + sfx
            core = core[:-1]
            
        c_lower = core.lower()
        if c_lower in mappings:
            replacement = mappings[c_lower]
            if core and core[0].isupper():
                replacement = replacement.capitalize()
            adapted_words.append(pfx + replacement + sfx)
        else:
            adapted_words.append(w)
            
    return " ".join(adapted_words)
