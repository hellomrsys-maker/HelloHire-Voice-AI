"""
German Engine — Phonology & Orthography Sub-AI
Responsible for Substantive Capitalization (Großschreibung), ß vs ss, and Umlauts.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 20 and 53.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words, normalize_orthography
from ..skills.pos_tagging import tag_pos
from ..skills.pragmatics_engine import validate_substantive_capitalization

class GermanPhonologySubAI:
    """Sub-AI dedicated to German orthography, phonology, and substantive capitalization."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray, swiss_mode: bool = False) -> Dict[str, Any]:
        """
        Process German orthography and synchronously update AMSV buffer.
        Byte 20: orthography_flags
          Bit 0: Substantive capitalization violation
          Bit 1: ss/ß violation
        Byte 53: phonology_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        cap_violations = validate_substantive_capitalization(tokens, tags)
        
        # Check ss / ß consistency
        ss_violations = []
        if swiss_mode and "ß" in text:
            ss_violations.append("Swiss orthography disallows 'ß'; use 'ss' instead.")
            
        flags = 0
        if len(cap_violations) > 0:
            flags |= (1 << 0)
        if len(ss_violations) > 0:
            flags |= (1 << 1)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[20] = flags
            amsv_buffer[53] = 1 # Active
            
        return {
            "sub_ai": "GermanPhonologySubAI",
            "status": "success",
            "token_count": len(tokens),
            "capitalization_violations": cap_violations,
            "ss_violations": ss_violations,
            "flags": flags,
            "is_valid": flags == 0
        }
