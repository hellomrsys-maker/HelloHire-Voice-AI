"""
Indonesian Engine — Voice & Affix Engine Skill
Derives and validates Indonesian voice affixes:
- Active: meN-
- Passive: di-
- Stative/accidental: ter-
- Intransitive: ber- (with r-drop rules)
- Suffixes: -kan, -i
- Circumfixes: ke-an, peN-an
"""

from typing import Dict, Any, Optional
from .nasal_assimilation_engine import apply_men_prefix

def derive_verb(
    root: str,
    voice: str = "active",
    suffix: Optional[str] = None
) -> str:
    """
    Derive Indonesian verb with voice prefix and optional causative/locative suffix.
    Example: derive_verb('tulis', 'active') -> 'menulis'
             derive_verb('tulis', 'passive') -> 'ditulis'
             derive_verb('bersih', 'active', 'kan') -> 'membersihkan'
             derive_verb('kerja', 'intransitive') -> 'bekerja'
    """
    r = root.lower().strip()
    sfx = suffix.lower().strip() if suffix else ""
    
    # 1. Base + suffix
    base_suffixed = r + sfx
    
    # 2. Voice prefixation
    if voice == "active":
        return apply_men_prefix(base_suffixed)
    elif voice == "passive":
        return f"di{base_suffixed}"
    elif voice == "accidental" or voice == "stative":
        return f"ter{base_suffixed}"
    elif voice == "intransitive":
        # ber- r-dropping rule:
        # If root starts with 'r' or has first syllable with '-er-' (e.g. kerja -> bekerja)
        if r.startswith("r"):
            return f"be{r}{sfx}"
        if r in {"kerja", "ternak", "terbang"}:
            return f"be{r}{sfx}"
        if r == "ajar":
            return "belajar"
        return f"ber{r}{sfx}"
        
    return base_suffixed

def derive_circumfix(root: str, circumfix_type: str = "ke_an") -> str:
    """
    Derive nominal circumfixes:
    Example: derive_circumfix('adil', 'ke_an') -> 'keadilan'
             derive_circumfix('didik', 'pen_an') -> 'pendidikan'
    """
    r = root.lower().strip()
    if circumfix_type == "ke_an":
        return f"ke{r}an"
    elif circumfix_type in {"pen_an", "peng_an"}:
        # peN- follows same nasal assimilation as meN-
        men_form = apply_men_prefix(r)
        if men_form.startswith("menge"):
            return f"penge{r}an"
        elif men_form.startswith("meny"):
            return f"peny{r[1:]}an"
        elif men_form.startswith("meng"):
            stem = men_form[4:]
            return f"peng{stem}an"
        elif men_form.startswith("mem"):
            stem = men_form[3:]
            return f"pem{stem}an"
        elif men_form.startswith("men"):
            stem = men_form[3:]
            return f"pen{stem}an"
        elif men_form.startswith("me"):
            return f"pe{r}an"
        return f"pe{r}an"
    elif circumfix_type == "per_an":
        return f"per{r}an"
    return r
