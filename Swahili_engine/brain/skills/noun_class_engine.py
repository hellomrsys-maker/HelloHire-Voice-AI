"""
Swahili Engine — Noun Class Engine Skill
Identifies Swahili noun classes (Ngeli 1–18) and extracts class prefixes and stems.
"""

from typing import Dict, Any, Optional

NOUN_CLASS_LEXICON = {
    # Class 1 (M/WA Singular)
    "mtu": 1, "mtoto": 1, "mwalimu": 1, "mwanafunzi": 1, "mgeni": 1,
    "msichana": 1, "mvulana": 1, "mwanaume": 1, "mwanamke": 1, "mzee": 1,
    "daktari": 1, "rais": 1, "bwana": 1, "bibi": 1, "kaka": 1, "dada": 1,
    # Class 2 (M/WA Plural)
    "watu": 2, "watoto": 2, "walimu": 2, "wanafunzi": 2, "wageni": 2,
    "wasichana": 2, "wavulana": 2, "wanaume": 2, "wanawake": 2, "wazee": 2,
    "madaktari": 2,
    # Class 3 (M/MI Singular)
    "mti": 3, "mto": 3, "mkono": 3, "mji": 3, "mpira": 3, "mwezi": 3, "mwili": 3, "mlango": 3,
    # Class 4 (M/MI Plural)
    "miti": 4, "mito": 4, "mikono": 4, "miji": 4, "mipira": 4, "miezi": 4, "miili": 4, "milango": 4,
    # Class 5 (JI/MA Singular)
    "jicho": 5, "jina": 5, "neno": 5, "gari": 5, "duka": 5, "embe": 5, "yai": 5, "tawi": 5,
    # Class 6 (JI/MA Plural & Collectives)
    "macho": 6, "majina": 6, "maneno": 6, "magari": 6, "maduka": 6, "maembe": 6, "mayai": 6, "matawi": 6,
    "maji": 6, "mafuta": 6, "maziwa": 6,
    # Class 7 (KI/VI Singular)
    "kitabu": 7, "kiti": 7, "kisu": 7, "chumba": 7, "chakula": 7, "choo": 7, "kioo": 7, "kiswahili": 7,
    # Class 8 (KI/VI Plural)
    "vitabu": 8, "viti": 8, "visu": 8, "vyumba": 8, "vyakula": 8, "vyoo": 8, "vioo": 8,
    # Class 9/10 (N/N)
    "nyumba": 9, "safari": 9, "barabara": 9, "meza": 9, "kalamu": 9, "ndege": 9, "barua": 9, "kazi": 9, "saa": 9,
    # Class 11 (U)
    "uhuru": 11, "ukuta": 11, "ufunguo": 11, "wimbo": 11, "uzuri": 11, "upendo": 11,
    # Class 15 (KU - Infinitives)
    "kusoma": 15, "kuimba": 15, "kucheza": 15, "kuandika": 15, "kula": 15, "kunywa": 15
}

def identify_noun_class(noun: str) -> int:
    """
    Identify the noun class (1..18) of a Swahili noun.
    Uses lexical lookup with morphological prefix heuristics.
    """
    lower = noun.lower().strip()
    if lower in NOUN_CLASS_LEXICON:
        return NOUN_CLASS_LEXICON[lower]
        
    # Morphological heuristics
    if lower.startswith("wa") and len(lower) > 3:
        return 2
    elif lower.startswith("mi") and len(lower) > 3:
        return 4
    elif lower.startswith("ma") and len(lower) > 3:
        return 6
    elif lower.startswith("vi") or lower.startswith("vy"):
        return 8
    elif lower.startswith("ki") or lower.startswith("ch"):
        return 7
    elif lower.startswith("ku") and len(lower) > 3:
        return 15
    elif lower.startswith("u") and len(lower) > 3:
        return 11
    elif (lower.startswith("m") or lower.startswith("mw")) and len(lower) > 3:
        return 1 # Default to human singular if ambiguous
        
    return 9 # Default to Class 9 (N-class / loanwords)
