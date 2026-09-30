"""
Tamil Pragmatic Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 22 (0x16): Register Tier (1=Centamiḻ, 2=Koṭuntamiḻ)
- Byte 23 (0x17): Sandhi Concord Flag (0x01 if valid)
- Byte 54 (0x36): Pragmatic Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Tamil_engine.brain.skills.pragmatics_engine import detect_register
from Tamil_engine.brain.skills.sandhi_engine import audit_sandhi

class TamilPragmaticSubAI:
    """
    Sub-AI dedicated to Tamil diglossic register alignment and sandhi euphonic rules.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Audits pragmatics and writes directly to physical memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        reg_info = detect_register(text)
        sandhi_info = audit_sandhi(text)
        
        tier = reg_info["tier_level"]  # 1 or 2
        sandhi_flag = sandhi_info["sandhi_concord_flag"]
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[22] = tier
            target_buf[23] = sandhi_flag
            target_buf[54] = 0x01  # Pragmatic Sub-AI Active
            
        return {
            "sub_ai": "TamilPragmaticSubAI",
            "tier_level": tier,
            "register": reg_info["register"],
            "is_sandhi_valid": sandhi_info["is_sandhi_valid"],
            "byte_22": tier,
            "byte_23": sandhi_flag,
            "byte_54": 0x01
        }
