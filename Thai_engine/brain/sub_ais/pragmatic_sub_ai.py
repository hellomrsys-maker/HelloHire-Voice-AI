"""
Thai Pragmatic Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 22 (0x16): Register Tier (1=Colloquial, 2=Formal, 3=Monastic, 4=Rachasap)
- Byte 23 (0x17): Scriptio Continua Segmentation Validity Flag
- Byte 54 (0x36): Pragmatic Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Thai_engine.brain.skills.rachasap_engine import detect_register
from Thai_engine.brain.skills.tokenization import tokenize_thai

class ThaiPragmaticSubAI:
    """
    Sub-AI dedicated to multi-tier registers (Rachasap, Monastic, Formal)
    and scriptio continua segmentability.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Audits pragmatics and writes directly to physical memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        reg_info = detect_register(text)
        tokens = tokenize_thai(text)
        
        tier = reg_info["tier_level"]
        is_segmented = len(tokens) > 0
        seg_flag = 0x01 if is_segmented else 0x00
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[22] = tier
            target_buf[23] = seg_flag
            target_buf[54] = 0x01  # Pragmatic Sub-AI Active
            
        return {
            "sub_ai": "ThaiPragmaticSubAI",
            "tier_level": tier,
            "register": reg_info["register"],
            "token_count": len(tokens),
            "byte_22": tier,
            "byte_23": seg_flag,
            "byte_54": 0x01
        }
