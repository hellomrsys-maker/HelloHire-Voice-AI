"""
Vietnamese Pragmatic Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 22 (0x16): Kinship Deixis Register Tier (1=Peer/Informal, 2=Formal, 3=High Deference)
- Byte 23 (0x17): Politeness Particle Concord Flag
- Byte 54 (0x36): Pragmatic Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.brain.skills.pragmatics_engine import VietnamesePragmaticsEngine

class VietnamesePragmaticSubAI:
    """
    Sub-AI dedicated to kinship address deixis, deference tiers,
    and sentence-final politeness particles (ạ, dạ).
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.pragmatics = VietnamesePragmaticsEngine()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Audits pragmatics and writes directly to physical memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        reg = self.pragmatics.detect_register(text)
        politeness = self.pragmatics.audit_politeness_particle(text)
        
        tier = reg["tier_level"]  # 1, 2, or 3
        byte_23_val = 0
        if politeness["is_polite"]:
            byte_23_val |= 0x01
        if politeness["has_particle_a"]:
            byte_23_val |= 0x02
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[22] = tier
            target_buf[23] = byte_23_val
            target_buf[54] = 0x01  # Pragmatic Sub-AI Active
            
        return {
            "sub_ai": "VietnamesePragmaticSubAI",
            "tier_level": tier,
            "dominant_register": reg["dominant_register"],
            "is_polite": politeness["is_polite"],
            "has_a": politeness["has_particle_a"],
            "byte_22": tier,
            "byte_23": byte_23_val,
            "byte_54": 0x01
        }
