"""
Arabic Engine — Pragmatic Sub-AI
Responsible for Islamic ceremonial greetings, MSA vs colloquial diglossia, and root classification.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pragmatics_engine import audit_letter_etiquette, COLLOQUIAL_MARKERS
from ..skills.root_pattern_engine import extract_root_heuristic

ROOT_MAP = {
    "ktb": 1, "drs": 2, "slm": 3, "'lm": 4, "ksr": 5, "jm'": 6, "xrj": 7
}

class ArabicPragmaticSubAI:
    """Sub-AI dedicated to Arabic pragmatic registers, greetings, and root categorization."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Arabic pragmatics and synchronously update AMSV buffer.
        Byte 22: root_class (1..7, 0=None)
        Byte 23: pragmatic_flags
          Bit 0: Islamic greeting present
          Bit 1: MSA formal register confirmed
          Bit 2: Dialectal colloquial intrusion or greeting clash
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        t_lower = text.lower()
        
        has_islamic_greeting = (
            "salamu 'alaykum" in t_lower or "salam" in t_lower or
            "السلام عليكم" in t_lower or "وعليكم السلام" in t_lower
        )
        
        colloquials = [cm for cm in COLLOQUIAL_MARKERS if cm in t_lower]
        is_msa = len(colloquials) == 0
        
        # Detect root class
        root_code = 0
        for t in tokens:
            r = extract_root_heuristic(t)
            if r and r in ROOT_MAP:
                root_code = ROOT_MAP[r]
                break
                
        flags = 0
        if has_islamic_greeting:
            flags |= (1 << 0)
        if is_msa:
            flags |= (1 << 1)
        if len(colloquials) > 0:
            flags |= (1 << 2) # Clash / dialect incursion
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = root_code & 0xFF
            amsv_buffer[23] = flags
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "ArabicPragmaticSubAI",
            "status": "success",
            "has_islamic_greeting": has_islamic_greeting,
            "is_pure_msa": is_msa,
            "colloquial_intrusions": colloquials,
            "root_class": root_code,
            "flags": flags,
            "is_valid": is_msa
        }
