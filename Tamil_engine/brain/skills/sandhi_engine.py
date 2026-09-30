"""
Tamil Sandhi (Puṇarcci) Engine.
Audits external sandhi, particularly the doubling of initial plosives
(Valikattal வலிமிகல்: k, c, t, p) following accusative and dative cases.
"""

from typing import Dict, List, Tuple

PLOSIVE_MAP = {
    "க": "க்க",
    "ச": "ச்ச",
    "த": "த்த",
    "ப": "ப்ப"
}

PLOSIVE_DOUBLED_STARTS = {"க்க", "ச்ச", "த்த", "ப்ப", "க்", "ச்", "த்", "ப்"}

def audit_sandhi(text: str) -> Dict[str, any]:
    """
    Checks if plosive doubling is properly observed after accusative and dative markers.
    """
    words = text.split()
    violations = []
    corrections = []
    
    for i in range(len(words) - 1):
        w1 = words[i]
        w2 = words[i + 1]
        
        # Check if w1 ends with accusative -ai (ை) or dative -ku (க்கு)
        triggers_sandhi = w1.endswith("ை") or w1.endswith("க்கு") or w1.endswith("உக்கு") or w1 in ["இனி", "அங்கு", "இங்கு"]
        
        if triggers_sandhi:
            # Check if w2 starts with a hard plosive (க, ச, த, ப) without doubling
            first_char = w2[0] if len(w2) > 0 else ""
            if first_char in PLOSIVE_MAP:
                # Check if w1 already has the virama or w2 already has the doubled plosive
                geminate_char = {"க": "க்", "ச": "ச்", "த": "த்", "ப": "ப்"}[first_char]
                if not w1.endswith(geminate_char) and not any(w2.startswith(p) for p in PLOSIVE_DOUBLED_STARTS):
                    # Violation: e.g. "புத்தகத்தை படி" -> should be "புத்தகத்தைப் படி"
                    corrected_pair = f"{w1}{geminate_char} {w2}"
                    violations.append(f"Missing sandhi plosive doubling between '{w1}' and '{w2}' (expected '{w1}{geminate_char} {w2}')")
                    corrections.append((f"{w1} {w2}", corrected_pair))
                    
    is_valid = len(violations) == 0
    return {
        "text": text,
        "is_sandhi_valid": is_valid,
        "violations": violations,
        "corrections": corrections,
        "sandhi_concord_flag": 1 if is_valid else 0
    }

def apply_sandhi(text: str) -> str:
    """Applies valid sandhi doubling to a phrase."""
    audit_res = audit_sandhi(text)
    res = text
    for old_pair, new_pair in audit_res["corrections"]:
        res = res.replace(old_pair, new_pair)
    return res
