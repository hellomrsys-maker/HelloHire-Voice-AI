"""
Korean Engine — Phonology Sub-AI
Responsible for Jaso decomposition, batchim detection, neutralization, and phonological alternations.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 20 and 53.
"""

from typing import Dict, Any
from ..skills.jaso_engine import has_batchim, is_hangul_syllable
from ..skills.batchim_engine import neutralize_batchim

class KoreanPhonologySubAI:
    """Sub-AI dedicated to Korean phonology, batchim, and Hangul unicode processing."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Korean phonology and synchronously update AMSV buffer.
        Byte 20: phonology_flags
          Bit 0: Batchim present in text
          Bit 1: Neutralization applied
        Byte 53: phonology_sub_ai_id = 1 (active)
        """
        has_any_batchim = False
        neutralized_chars = []
        
        for ch in text:
            if is_hangul_syllable(ch):
                if has_batchim(ch):
                    has_any_batchim = True
                    neutral = neutralize_batchim(ch)
                    if neutral != ch:
                        neutralized_chars.append((ch, neutral))
                        
        flags = 0
        if has_any_batchim:
            flags |= (1 << 0)
        if len(neutralized_chars) > 0:
            flags |= (1 << 1)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[20] = flags
            amsv_buffer[53] = 1 # Active
            
        return {
            "sub_ai": "KoreanPhonologySubAI",
            "status": "success",
            "has_batchim": has_any_batchim,
            "neutralizations": neutralized_chars,
            "flags": flags,
            "is_valid": True
        }
