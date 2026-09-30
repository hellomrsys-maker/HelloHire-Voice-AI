"""
Cantonese Double Object Construction (DOC) & Word Order Engine.
Enforces the Cantonese invariant V + DO + IO (e.g. 畀本書我) over Mandarin calque V + IO + DO (畀我本書),
postverbal adverbs (行先 vs 先行), and post-adjectival comparatives with gwo3 (我大過你 vs 我比你大).
"""

from typing import Dict, List, Optional, Tuple
import re

DITRANSITIVE_VERBS = ["畀", "送", "借", "還", "派", "賣", "教"]
PRONOUNS = ["我", "你", "佢", "我哋", "你哋", "佢哋", "大家"]

def analyze_doc_structure(sentence: str) -> Dict[str, any]:
    """
    Analyzes ditransitive predicate word order in Cantonese.
    Detects whether canonical V + DO + IO is used or unnatural Mandarin calque V + IO + DO.
    """
    for verb in DITRANSITIVE_VERBS:
        if verb in sentence:
            # Check for Mandarin calque: V + PRON + [CLF/NOUN] (e.g., 畀我本書, 送佢禮物)
            for pron in PRONOUNS:
                calque_pattern = f"{verb}{pron}"
                if calque_pattern in sentence:
                    # Look for trailing direct object
                    idx = sentence.find(calque_pattern)
                    trailing = sentence[idx + len(calque_pattern):].rstrip("，。！？,.!? ")
                    if len(trailing) > 0:
                        suggested_canonical = f"{verb}{trailing}{pron}"
                        return {
                            "is_canonical": False,
                            "verb": verb,
                            "detected_order": "V + IO + DO (Mandarin Calque)",
                            "recipient_io": pron,
                            "theme_do": trailing,
                            "suggested_canonical": suggested_canonical,
                            "rule_violation": "In Cantonese, ditransitive predicates canonically require V + DO + IO (e.g. 畀本書我, not 畀我本書)"
                        }
            
            # Check for canonical Cantonese: V + [CLF/NOUN] + PRON (e.g., 畀本書我)
            for pron in PRONOUNS:
                if sentence.endswith(pron) or f"{pron}，" in sentence or f"{pron}。" in sentence or f"{pron} " in sentence or f"{pron}喇" in sentence or f"{pron}啦" in sentence:
                    v_idx = sentence.find(verb)
                    p_idx = sentence.find(pron, v_idx + len(verb))
                    if p_idx > v_idx + len(verb):
                        theme_do = sentence[v_idx + len(verb):p_idx]
                        return {
                            "is_canonical": True,
                            "verb": verb,
                            "detected_order": "V + DO + IO (Canonical Cantonese)",
                            "recipient_io": pron,
                            "theme_do": theme_do,
                            "suggested_canonical": sentence,
                            "rule_violation": None
                        }
                        
    return {
        "is_canonical": True,
        "verb": None,
        "detected_order": "Non-ditransitive or indeterminate",
        "recipient_io": None,
        "theme_do": None,
        "suggested_canonical": sentence,
        "rule_violation": None
    }

def analyze_postverbal_adverb(sentence: str) -> Dict[str, any]:
    """
    Validates postverbal adverb positioning (e.g. 行先 vs 先行, 飲多杯 vs 多飲杯).
    """
    # Check '先'
    if "先行" in sentence:
        return {
            "is_canonical": False,
            "marker": "先",
            "detected_order": "Preverbal 先行 (Mandarin calque)",
            "suggested_canonical": sentence.replace("先行", "行先"),
            "rule_violation": "Adverb '先' must follow the main verb in spoken Cantonese (行先)"
        }
    if "行先" in sentence:
        return {
            "is_canonical": True,
            "marker": "先",
            "detected_order": "Postverbal 行先 (Canonical Cantonese)",
            "suggested_canonical": sentence,
            "rule_violation": None
        }
        
    # Check comparative '比' vs '過'
    if "比" in sentence and any(adj in sentence for adj in ["大", "細", "高", "肥", "長"]):
        # Match pattern A + 比 + B + Adj
        m = re.search(r"(\S+)比(\S+)([大細高肥長])", sentence)
        if m:
            subj, comp, adj = m.group(1), m.group(2), m.group(3)
            suggested = sentence.replace(m.group(0), f"{subj}{adj}過{comp}")
            return {
                "is_canonical": False,
                "marker": "過",
                "detected_order": "Pre-adjectival 比 (Mandarin calque)",
                "suggested_canonical": suggested,
                "rule_violation": "Comparative in Cantonese uses post-adjectival '過' (A + Adj + 過 + B)"
            }
            
    if "過" in sentence and any(adj in sentence for adj in ["大", "細", "高", "肥", "長"]):
        return {
            "is_canonical": True,
            "marker": "過",
            "detected_order": "Post-adjectival 過 (Canonical Cantonese)",
            "suggested_canonical": sentence,
            "rule_violation": None
        }

    return {
        "is_canonical": True,
        "marker": None,
        "detected_order": "Canonical or neutral",
        "suggested_canonical": sentence,
        "rule_violation": None
    }

def invert_to_canonical_cantonese(sentence: str) -> str:
    """
    Normalizes a sentence by converting Mandarin ditransitive, adverbial, and comparative
    calques into natural, canonical Cantonese.
    """
    res = sentence
    doc_res = analyze_doc_structure(res)
    if not doc_res["is_canonical"] and doc_res["suggested_canonical"]:
        # Replace the calqued substring
        calque = f"{doc_res['verb']}{doc_res['recipient_io']}{doc_res['theme_do']}"
        res = res.replace(calque, doc_res["suggested_canonical"])
        
    adv_res = analyze_postverbal_adverb(res)
    if not adv_res["is_canonical"] and adv_res["suggested_canonical"]:
        res = adv_res["suggested_canonical"]
        
    return res
