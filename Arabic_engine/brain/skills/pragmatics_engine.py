"""
Arabic Engine — Pragmatics & Etiquette Skill
Handles greetings adjacency pairs (As-Salamu 'Alaykum / Wa-'Alaykum As-Salam),
formal correspondence protocol, and diglossic colloquial marker detection.
"""

from typing import Dict, Any, List

GREETING_PAIRS = {
    "salam": {
        "call_triggers": ["as-salamu 'alaykum", "as-salamu alaykum", "alsalamu alaykum", "السلام عليكم"],
        "expected": "wa-'alaykum as-salam",
        "expected_triggers": ["wa-'alaykum", "wa alaykum", "وعليكم"],
        "protocol": "islamic_salam"
    },
    "sabah": {
        "call_triggers": ["sabah al-khayr", "sabah el-kheir", "صباح الخير"],
        "expected": "sabah an-nur",
        "expected_triggers": ["sabah an-nur", "sabah el-noor", "صباح النور"],
        "protocol": "sabah_greeting"
    },
    "masa": {
        "call_triggers": ["masa' al-khayr", "masaa el-kheir", "مساء الخير"],
        "expected": "masa' an-nur",
        "expected_triggers": ["masa' an-nur", "masaa el-noor", "مساء النور"],
        "protocol": "masa_greeting"
    },
    "ahlan": {
        "call_triggers": ["ahlan wa-sahlan", "ahlan wa sahlan", "أهلا وسهلا", "أهلاً وسهلاً"],
        "expected": "ahlan bika",
        "expected_triggers": ["ahlan bika", "ahlan biki", "ahlan bik", "marhaban", "أهلا بك"],
        "protocol": "ahlan_welcome"
    }
}

HONORIFIC_TITLES = [
    "fakhamat", "ma'ali", "sa'adat", "fadilat", "samahat", "al-ustadh", "al-muhtaram", "as-sayyid"
]

FORMAL_OPENINGS = [
    "tahiyya tayyiba wa-ba'd", "tahiyyatan tayyibatan wa-ba'd", "tahiyya 'atira", "تحية طيبة وبعد"
]

FORMAL_CLOSINGS = [
    "wa-tafaddalu bi-qabuli fa'iq al-ihtiram", "ma'a fa'iq al-ihtiram", "dumtum bi-khayr",
    "وتفضلوا بقبول فائق الاحترام والتقدير"
]

COLLOQUIAL_MARKERS = [
    "kwayyis", "biddi", "shu", "esh", "daba", "dilwa'ti", "barsha", "zwin", "mashi", "keda"
]

def validate_greeting_turn(call: str, response: str) -> Dict[str, Any]:
    """Validate conversational turn against ceremonial Arabic greeting etiquette."""
    c_lower = call.lower().strip()
    r_lower = response.lower().strip()
    
    for key, p_info in GREETING_PAIRS.items():
        if any(trig in c_lower for trig in p_info["call_triggers"]):
            valid = any(ans in r_lower for ans in p_info["expected_triggers"])
            return {
                "valid": valid,
                "call": call,
                "response": response,
                "expected": p_info["expected"],
                "protocol": p_info["protocol"]
            }
            
    return {"valid": True, "call": call, "response": response, "protocol": "general"}

def audit_letter_etiquette(text: str) -> Dict[str, Any]:
    """Audit formal correspondence for proper salutation, honorific titles, and closings."""
    t_lower = text.lower()
    
    has_opening = any(op in t_lower for op in FORMAL_OPENINGS) or "tahiyya" in t_lower
    has_closing = any(cl in t_lower for cl in FORMAL_CLOSINGS) or "al-ihtiram" in t_lower
    has_title = any(ti in t_lower for ti in HONORIFIC_TITLES)
    
    colloquials = [cm for cm in COLLOQUIAL_MARKERS if cm in t_lower]
    
    passed = has_opening and has_closing and len(colloquials) == 0
    
    return {
        "has_opening": has_opening,
        "has_closing": has_closing,
        "has_honorific_title": has_title,
        "colloquial_intrusions": colloquials,
        "is_pure_msa": len(colloquials) == 0,
        "passed": passed
    }
