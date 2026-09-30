"""
Italian Engine — Pragmatics Engine Skill
Evaluates social deixis (tu vs Lei), bureaucratic epistolary formulas, and diplomatic honorifics.
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
    """Classify text into 'informal' (tu) or 'formal' (Lei)."""
    t_lower = text.lower()
    
    formal_score = 0
    informal_score = 0
    
    formal_markers = [
        "lei", "la sua", "il suo", "la ringrazio", "le scrivo", "le porgo",
        "cordiali saluti", "distinti saluti", "gentile", "egregio", "dottore", "dottoressa"
    ]
    informal_markers = [
        "tu", "ti", "il tuo", "la tua", "ciao", "a presto", "un abbraccio", "baci", "stammi bene"
    ]
    
    for m in formal_markers:
        if m in t_lower:
            formal_score += 1
            
    for m in informal_markers:
        if m in t_lower:
            informal_score += 1
            
    if formal_score > informal_score:
        register = "formal"
    elif informal_score > formal_score:
        register = "informal"
    else:
        register = "neutral"
        
    return {
        "register": register,
        "formal_score": formal_score,
        "informal_score": informal_score
    }

def format_salutation(title: str, recipient_surname: str, formal: bool = True) -> str:
    """Format formal Italian epistolary salutation."""
    if not formal:
        return f"Caro {recipient_surname}," if not title else f"Ciao {recipient_surname},"
        
    t_clean = title.strip()
    if not t_clean:
        t_clean = "Signore"
        
    if t_clean.lower() in {"dottore", "dott."}:
        sal = f"Gentile Dottor {recipient_surname},"
    elif t_clean.lower() in {"dottoressa", "dott.ssa"}:
        sal = f"Gentile Dottoressa {recipient_surname},"
    elif t_clean.lower() in {"professore", "prof."}:
        sal = f"Chiarissimo Professor {recipient_surname},"
    elif t_clean.lower() in {"avvocato", "avv."}:
        sal = f"Egregio Avvocato {recipient_surname},"
    else:
        sal = f"Gentile {t_clean} {recipient_surname},"
        
    return sal

def format_closing(formal: bool = True) -> str:
    """Generate appropriate epistolary closing formula."""
    if formal:
        return "In attesa di un Suo cortese riscontro, Le porgo i miei più cordiali saluti.\nCordiali saluti,"
    return "Un caro saluto e a presto."
