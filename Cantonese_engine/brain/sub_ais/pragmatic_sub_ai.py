"""
Cantonese Pragmatic Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 22 (0x16): Register Tier (1=Colloquial Hau2 Jyu5, 2=Formal Syu1 Min6 Jyu5)
- Byte 23 (0x17): Sentence-Final Particle (SFP) Concord Flag
- Byte 54 (0x36): Pragmatic Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Cantonese_engine.brain.skills.pragmatics_engine import detect_register
from Cantonese_engine.brain.skills.sfp_engine import extract_sfps

class CantonesePragmaticSubAI:
    """
    Sub-AI dedicated to Cantonese diglossic register balance,
    pragmatic nuances, and sentence-final particle (SFP) concord.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Audits pragmatics and writes directly to physical AMSV memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        reg_info = detect_register(text)
        sfps = extract_sfps(text)
        
        tier = reg_info["tier_code"]  # 1 or 2
        has_sfps = len(sfps) > 0
        cluster_valid = len(sfps) <= 3
        
        # Byte 23 Bitfield:
        # Bit 0: Has SFP
        # Bit 1: Cluster valid (<= 3)
        byte_23_val = 0
        if has_sfps:
            byte_23_val |= 0x01
        if cluster_valid and has_sfps:
            byte_23_val |= 0x02
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[22] = tier
            target_buf[23] = byte_23_val
            target_buf[54] = 0x01  # Pragmatic Sub-AI Active
            
        return {
            "sub_ai": "CantonesePragmaticSubAI",
            "tier_level": tier,
            "register": reg_info["register"],
            "has_sfps": has_sfps,
            "sfp_count": len(sfps),
            "byte_22": tier,
            "byte_23": byte_23_val,
            "byte_54": 0x01
        }
