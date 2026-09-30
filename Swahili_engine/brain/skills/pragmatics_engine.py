"""
Swahili Engine — Pragmatics & Etiquette Skill
Handles greetings (Shikamoo/Marahaba, Hujambo/Sijambo), honorific titles, and epistolary formulas.
"""

from typing import Dict, Any, List

GREETING_PAIRS = {
    "shikamoo": "marahaba",
    "hujambo": "sijambo",
    "hamjambo": "hatujambo",
    "habari gani": "nzuri"
}

HONORIFIC_TITLES = {
    "mzee", "bwana", "bibi", "mheshimiwa", "ndugu", "ustadh", "mama", "baba", "kaka", "dada"
}

FORMAL_CLOSINGS = [
    "wako mtiifu", "wako mwaminifu", "wasalaam", "wako katika ujenzi wa taifa", "wako katika kazi"
]

def validate_greeting_turn(call: str, response: str) -> Dict[str, Any]:
    """
    Validate whether the response appropriately answers the Swahili greeting call.
    Critically verifies the asymmetric Shikamoo -> Marahaba etiquette.
    """
    c_clean = call.lower().strip()
    r_clean = response.lower().strip()
    
    if "shikamoo" in c_clean:
        valid = "marahaba" in r_clean
        return {
            "valid": valid,
            "call": call,
            "response": response,
            "expected_response": "Marahaba",
            "type": "intergenerational_respect",
            "protocol": "shikamoo_marahaba"
        }
    elif "hujambo" in c_clean:
        valid = "sijambo" in r_clean
        return {
            "valid": valid,
            "call": call,
            "response": response,
            "expected_response": "Sijambo",
            "type": "state_inquiry_singular",
            "protocol": "jambo_salutation"
        }
    elif "hamjambo" in c_clean:
        valid = "hatujambo" in r_clean
        return {
            "valid": valid,
            "call": call,
            "response": response,
            "expected_response": "Hatujambo",
            "type": "state_inquiry_plural",
            "protocol": "jambo_salutation_plural"
        }
    elif "habari" in c_clean:
        valid = any(ans in r_clean for ans in ["nzuri", "salama", "njema", "safi"])
        return {
            "valid": valid,
            "call": call,
            "response": response,
            "expected_response": "Nzuri / Salama",
            "type": "news_inquiry",
            "protocol": "habari_salutation"
        }
        
    return {"valid": True, "call": call, "response": response, "protocol": "general"}


def audit_letter_etiquette(text: str) -> Dict[str, Any]:
    """Audit formal business correspondence for proper salutation, titles, and closing."""
    lower = text.lower()
    has_title = any(title in lower for title in HONORIFIC_TITLES)
    has_closing = any(closing in lower for closing in FORMAL_CLOSINGS)
    
    has_salutation = any(sal in lower for sal in ["kwa mheshimiwa", "kwa bwana", "kwa bibi", "ndugu", "mpendwa"])
    
    passed = has_salutation and has_closing
    
    return {
        "has_salutation": has_salutation,
        "has_title": has_title,
        "has_closing": has_closing,
        "passed": passed
    }
