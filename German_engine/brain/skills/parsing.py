"""
German Engine — Topological Field (Satzklammer) Parsing Skill
Parses German sentences into topological fields:
Vorfeld (VF), Linke Satzklammer (LK), Mittelfeld (MF), Rechte Satzklammer (RK), Nachfeld (NF).
"""

from typing import List, Dict, Any, Optional
from .separable_verb_engine import SEPARABLE_PREFIXES

SUBORDINATING_CONJUNCTIONS = {
    "weil", "dass", "daß", "wenn", "ob", "obwohl", "obgleich",
    "während", "bevor", "nachdem", "damit", "sodass", "falls", "seitdem"
}

FINITE_VERB_TAGS = {"VVFIN", "VAFIN", "VMFIN"}
NON_FINITE_VERB_TAGS = {"VVINF", "VAINF", "VMINF", "VVPP", "VAPP"}

def parse_topological_fields(tokens: List[str], pos_tags: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Segment tokens into topological fields: Vorfeld, Linke Klammer, Mittelfeld, Rechte Klammer, Nachfeld.
    """
    if not tokens:
        return {"clause_type": "empty", "fields": {}}
        
    clean_tokens = []
    clean_tags = []
    for t, tag in zip(tokens, pos_tags):
        if t not in {".", "!", "?", ";"}:
            clean_tokens.append(t)
            clean_tags.append(tag)
            
    if not clean_tokens:
        return {"clause_type": "empty", "fields": {}}
        
    first_word = clean_tokens[0].lower()
    
    # 1. Subordinate clause check (V-End)
    if first_word in SUBORDINATING_CONJUNCTIONS:
        clause_type = "subordinate_v_end"
        lk = [clean_tokens[0]]
        # Find verbs at the end of the clause (RK)
        rk_idx = len(clean_tokens) - 1
        while rk_idx > 0 and (clean_tags[rk_idx]["upos"] in {"VERB", "AUX"} or clean_tokens[rk_idx].lower() in SEPARABLE_PREFIXES):
            rk_idx -= 1
        rk_idx += 1
        
        mf = clean_tokens[1:rk_idx]
        rk = clean_tokens[rk_idx:]
        vf = []
        nf = []
        return {
            "clause_type": clause_type,
            "fields": {
                "vorfeld": vf,
                "linke_klammer": lk,
                "mittelfeld": mf,
                "rechte_klammer": rk,
                "nachfeld": nf
            },
            "verb_second": False
        }
        
    # 2. V1 Clause (Yes/No Question or Imperative)
    if clean_tags[0]["upos"] in {"VERB", "AUX"}:
        clause_type = "v1_clause"
        lk = [clean_tokens[0]]
        vf = []
        
        # Check for separable prefix or non-finite verb at end (RK)
        if len(clean_tokens) > 1 and (clean_tokens[-1].lower() in SEPARABLE_PREFIXES or clean_tags[-1]["upos"] in {"VERB", "AUX"}):
            rk = [clean_tokens[-1]]
            mf = clean_tokens[1:-1]
        else:
            rk = []
            mf = clean_tokens[1:]
        nf = []
        return {
            "clause_type": clause_type,
            "fields": {
                "vorfeld": vf,
                "linke_klammer": lk,
                "mittelfeld": mf,
                "rechte_klammer": rk,
                "nachfeld": nf
            },
            "verb_second": False
        }
        
    # 3. Standard V2 Main Clause
    # Vorfeld is typically the constituent preceding the finite verb
    lk_pos = -1
    for i, tag in enumerate(clean_tags):
        if tag["upos"] in {"VERB", "AUX"}:
            lk_pos = i
            break
            
    if lk_pos != -1:
        clause_type = "main_v2"
        vf = clean_tokens[:lk_pos]
        lk = [clean_tokens[lk_pos]]
        
        # Scan for Rechte Satzklammer (RK): last element if non-finite verb or separable prefix
        if len(clean_tokens) > lk_pos + 1 and (clean_tokens[-1].lower() in SEPARABLE_PREFIXES or clean_tags[-1]["upos"] in {"VERB", "AUX"}):
            # Check if there is a multi-word predicate (e.g. "hat angerufen" or "muss gehen")
            rk_start = len(clean_tokens) - 1
            while rk_start > lk_pos and (clean_tags[rk_start]["upos"] in {"VERB", "AUX"} or clean_tokens[rk_start].lower() in SEPARABLE_PREFIXES):
                rk_start -= 1
            rk_start += 1
            rk = clean_tokens[rk_start:]
            mf = clean_tokens[lk_pos + 1:rk_start]
        else:
            rk = []
            mf = clean_tokens[lk_pos + 1:]
            
        nf = []
        return {
            "clause_type": clause_type,
            "fields": {
                "vorfeld": vf,
                "linke_klammer": lk,
                "mittelfeld": mf,
                "rechte_klammer": rk,
                "nachfeld": nf
            },
            "verb_second": True
        }
        
    # Fallback
    return {
        "clause_type": "fragment",
        "fields": {
            "vorfeld": clean_tokens,
            "linke_klammer": [],
            "mittelfeld": [],
            "rechte_klammer": [],
            "nachfeld": []
        },
        "verb_second": False
    }
