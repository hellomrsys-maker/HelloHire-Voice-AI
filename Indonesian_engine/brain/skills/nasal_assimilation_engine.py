"""
Indonesian Engine — Nasal Assimilation Engine Skill
Implements morphophonemic nasal assimilation for active verbal prefix 'meN-' and nominal 'peN-':
- p -> m, t -> n, s -> ny, k -> ng (deletion)
- b -> mem-b, d -> men-d, j -> men-j, c -> men-c, g -> meng-g (retention)
- vowels/h -> meng-
- liquids/nasals -> me-
- monosyllables -> menge-
"""

from typing import Dict, Any

VOWELS = set("aeiou")
LIQUIDS_NASALS = set("lrmnwy")

def apply_men_prefix(root: str) -> str:
    """Derive active verb with prefix 'meN-' according to Indonesian phonological rules."""
    r = root.lower().strip()
    if not r:
        return ""
        
    # Check for monosyllabic roots
    # Standard heuristic: <= 3 characters with 1 vowel (e.g. cat, bom, lap, klik, tes)
    vowel_count = sum(1 for ch in r if ch in VOWELS)
    if vowel_count == 1 and len(r) <= 4 and not r.startswith(tuple(VOWELS)):
        if r in {"cat", "bom", "lap", "klik", "tes", "sah", "cek", "cap"}:
            return f"menge{r}"
            
    first_char = r[0]
    
    # 1. Voiceless stops / sibilants (p, t, s, k): deletion & nasal substitution
    if first_char == "p":
        return f"mem{r[1:]}"
    elif first_char == "t":
        return f"men{r[1:]}"
    elif first_char == "s":
        return f"meny{r[1:]}"
    elif first_char == "k":
        # Exception: 'kh' cluster retains: khusus -> mengkhususkan
        if r.startswith("kh"):
            return f"meng{r}"
        return f"meng{r[1:]}"
        
    # 2. Voiced stops & affricates (b, d, j, c, g): retention with homorganic nasal
    elif first_char == "b":
        return f"mem{r}"
    elif first_char in {"d", "j", "c"}:
        return f"men{r}"
    elif first_char == "g":
        return f"meng{r}"
        
    # 3. Vowels & glottal (a, e, i, o, u, h)
    elif first_char in VOWELS or first_char == "h":
        return f"meng{r}"
        
    # 4. Liquids and nasals (l, r, m, n, w, y)
    elif first_char in LIQUIDS_NASALS:
        return f"me{r}"
        
    return f"me{r}"

def verify_men_derivation(derived_word: str, root: str) -> Dict[str, Any]:
    """Audit whether a derived verb complies with standard meN- nasal assimilation."""
    expected = apply_men_prefix(root)
    actual = derived_word.lower().strip()
    is_valid = actual == expected
    
    violations = []
    if not is_valid:
        violations.append({
            "root": root,
            "actual": actual,
            "expected": expected,
            "rule": "nasal_assimilation_mismatch",
            "error": f"Derived verb '{actual}' does not match expected nasal assimilation '{expected}' for root '{root}'."
        })
        
    return {
        "valid": is_valid,
        "root": root,
        "derived": actual,
        "expected": expected,
        "violations": violations
    }
