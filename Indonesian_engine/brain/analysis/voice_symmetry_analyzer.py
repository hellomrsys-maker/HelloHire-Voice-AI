"""
Indonesian Engine — Voice Symmetry Analyzer
Audits active voice (meN-) nasal assimilation and passive voice (di-) symmetry,
detecting unassimilated voiceless stop errors (e.g. *mempakai -> memakai, *mentulis -> menulis).
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.nasal_assimilation_engine import apply_men_prefix

# Common roots with voiceless initial stops that must delete: p, t, s, k
VOICELESS_STOP_ROOTS = {
    "pakai": "memakai", "potong": "memotong", "pilih": "memilih",
    "tulis": "menulis", "tarik": "menarik", "tolong": "menolong",
    "sapu": "menyapu", "sewa": "menyewa", "simpan": "menyimpan",
    "kirim": "mengirim", "kejar": "mengejar", "kunci": "mengunci"
}

class VoiceSymmetryAnalyzer:
    """Cognitive analyzer for Indonesian voice affixation and nasal assimilation."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        violations = []
        voice_forms_found = []
        
        for tok in tokens:
            w = tok.lower()
            
            # Check for unassimilated active prefix errors (e.g. mempakai, mentulis, menyapu is ok, mengkirim)
            if w.startswith("memp") and len(w) > 4:
                root_cand = w[3:]
                if root_cand in VOICELESS_STOP_ROOTS:
                    violations.append({
                        "token": tok,
                        "rule": "nasal_assimilation_p_deletion",
                        "error": f"Active verb '{tok}' must delete root-initial 'p' and assimilate into 'mem{root_cand[1:]}' (expected '{VOICELESS_STOP_ROOTS[root_cand]}')."
                    })
            elif w.startswith("ment") and len(w) > 4:
                root_cand = w[3:]
                if root_cand in VOICELESS_STOP_ROOTS:
                    violations.append({
                        "token": tok,
                        "rule": "nasal_assimilation_t_deletion",
                        "error": f"Active verb '{tok}' must delete root-initial 't' and assimilate into 'men{root_cand[1:]}' (expected '{VOICELESS_STOP_ROOTS[root_cand]}')."
                    })
            elif w.startswith("mengk") and len(w) > 5 and not w.startswith("mengkh"):
                root_cand = w[4:]
                if root_cand in VOICELESS_STOP_ROOTS:
                    violations.append({
                        "token": tok,
                        "rule": "nasal_assimilation_k_deletion",
                        "error": f"Active verb '{tok}' must delete root-initial 'k' and assimilate into 'meng{root_cand[1:]}' (expected '{VOICELESS_STOP_ROOTS[root_cand]}')."
                    })
                    
            # Record detected voice
            if w.startswith(("me", "mem", "men", "meny", "meng", "menge")):
                voice_forms_found.append({"token": tok, "voice": "active"})
            elif w.startswith("di") and len(w) > 2:
                voice_forms_found.append({"token": tok, "voice": "passive"})
                
        return {
            "text": text,
            "voice_forms_found": voice_forms_found,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
