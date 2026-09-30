"""
Persian Pragmatic Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 22 (0x16): Ta'arof Register Tier (1=Informal, 2=Formal, 3=High Ta'arof)
- Byte 23 (0x17): Deference Concord & Social Distance Flag
- Byte 54 (0x36): Pragmatic Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Persian_engine.brain.analysis.taarof_deference_analyzer import TaarofDeferenceAnalyzer

class PersianPragmaticSubAI:
    """
    Sub-AI dedicated to Ta'arof socio-cultural deference, register tiers,
    and epistolary formality.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.analyzer = TaarofDeferenceAnalyzer()

    def process(self, text: str, buffer: Optional[bytearray] = None, target_register: str = "formal") -> Dict[str, Any]:
        """Audits pragmatics and updates physical memory offsets in-place."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        
        audit = self.analyzer.audit_deference_and_register(text, target_register=target_register)
        tier_level = audit["tier_level"]  # 1, 2, or 3
        
        # Deference flag (Byte 23): Bit 0 = Register Aligned, Bit 1 = Zero Colloquial Leaks
        byte_23_val = 0
        if audit["is_aligned"]:
            byte_23_val |= 0x01
        if len(audit["colloquial_findings"]) == 0:
            byte_23_val |= 0x02
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[22] = tier_level
            target_buf[23] = byte_23_val
            target_buf[54] = 0x01  # Pragmatic Sub-AI Active
            
        return {
            "sub_ai": "PersianPragmaticSubAI",
            "tier_level": tier_level,
            "detected_register": audit["detected_register"],
            "deference_score": audit["deference_score"],
            "colloquial_count": len(audit["colloquial_findings"]),
            "byte_22": tier_level,
            "byte_23": byte_23_val,
            "byte_54": 0x01
        }
