"""
Italian Engine — Pragmatic Sub-AI
Responsible for social deixis (tu vs Lei), epistolary honorifics, and classical idioms.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any, List
from ..skills.pragmatics_engine import classify_register

CLASSICAL_IDIOMS = [
    "in bocca al lupo", "non vedere l'ora", "prendere lucciole per lanterne",
    "fare fiasco", "costare un occhio della testa"
]

class ItalianPragmaticSubAI:
    """Sub-AI dedicated to Italian pragmatic registers, deference deixis, and idioms."""

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Italian pragmatics and synchronously update AMSV buffer.
        Byte 22: register_tier
          0: Informal (tu)
          1: Formal (Lei)
          2: Plural Formal (Loro / Voi)
        Byte 23: pragmatic_flags
          Bit 0: Formal salutation
          Bit 1: Polite closing formula
          Bit 2: Rhetorical idiom found
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        reg_info = classify_register(text)
        reg_tier = 1 if reg_info["register"] == "formal" else 0
        
        t_clean = text.lower()
        has_salutation = any(s in t_clean for s in ["gentile", "egregio", "chiarissimo"])
        has_closing = any(c in t_clean for c in ["cordiali saluti", "distinti saluti", "cortese riscontro"])
        has_idiom = any(idm in t_clean for idm in CLASSICAL_IDIOMS) or any(
            v in t_clean for v in ["non vedere l'ora", "non vedo l'ora", "non vede l'ora", "non vediamo l'ora"]
        )
        
        flags = 0
        if has_salutation:
            flags |= (1 << 0)
        if has_closing:
            flags |= (1 << 1)
        if has_idiom:
            flags |= (1 << 2)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = reg_tier
            amsv_buffer[23] = flags
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "ItalianPragmaticSubAI",
            "status": "success",
            "register": reg_info["register"],
            "register_tier": reg_tier,
            "has_salutation": has_salutation,
            "has_closing": has_closing,
            "has_idiom": has_idiom,
            "flags": flags,
            "is_valid": True
        }
