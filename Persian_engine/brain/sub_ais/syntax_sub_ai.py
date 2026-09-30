"""
Persian Syntax Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 18 (0x12): Syntax Capability Status / Flag
- Byte 52 (0x34): Syntax Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger
from Persian_engine.brain.analysis.ezafe_attachment_analyzer import EzafeAttachmentAnalyzer

class PersianSyntaxSubAI:
    """
    Sub-AI dedicated to Persian SOV word order, head-final verb verification,
    and Ezafe attachment validation.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.tagger = PersianPOSTagger()
        self.ezafe_analyzer = EzafeAttachmentAnalyzer()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes syntax and writes in-place to physical AMSV memory offsets."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tagged = self.tagger.tag_sentence(text)
        
        # 1. Verify SOV / Head-final verb
        is_head_final = False
        if tagged:
            last_word, last_pos = tagged[-1]
            if last_pos == "PUNCT" and len(tagged) > 1:
                last_word, last_pos = tagged[-2]
            is_head_final = (last_pos in {"VERB", "AUX"})
            
        # 2. Ezafe Analysis
        ezafe_res = self.ezafe_analyzer.analyze_ezafe_chains(text)
        
        # Compute bitfield for Byte 18
        # Bit 0: Head-final verb
        # Bit 1: Ezafe valid
        # Bit 2: Has Ezafe chain
        # Bit 3: Non-empty valid sentence
        byte_18_val = 0
        if is_head_final:
            byte_18_val |= 0x01
        if ezafe_res["is_valid"]:
            byte_18_val |= 0x02
        if ezafe_res["total_chains"] > 0:
            byte_18_val |= 0x04
        if len(tagged) > 0:
            byte_18_val |= 0x08
            
        # Direct Zero-Bridge Memory Synchronization
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[18] = byte_18_val
            target_buf[52] = 0x01  # Syntax Sub-AI Active
            
        return {
            "sub_ai": "PersianSyntaxSubAI",
            "is_head_final": is_head_final,
            "ezafe_valid": ezafe_res["is_valid"],
            "ezafe_chains_count": ezafe_res["total_chains"],
            "byte_18": byte_18_val,
            "byte_52": 0x01
        }
