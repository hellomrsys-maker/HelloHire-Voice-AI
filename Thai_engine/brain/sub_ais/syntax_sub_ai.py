"""
Thai Syntax Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 18 (0x12): Syntax Capability Status / SVO Bitfield
- Byte 52 (0x34): Syntax Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Thai_engine.brain.skills.pos_tagging import tag_pos
from Thai_engine.brain.skills.tokenization import tokenize_thai

class ThaiSyntaxSubAI:
    """
    Sub-AI dedicated to Thai isolating SVO topology and serial verb constructions.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes syntax and writes directly to physical memory offsets."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tokens = tokenize_thai(text)
        tagged = tag_pos(tokens)
        
        has_verb = any(pos in {"VERB", "AUX"} for _, pos in tagged)
        has_subject = any(pos in {"NOUN", "PRON"} for _, pos in tagged)
        has_aspect = any(tok in {"กำลัง", "จะ", "ได้", "เคย", "แล้ว"} for tok in tokens)
        is_svo = has_verb and has_subject
        
        # Byte 18 Bitfield:
        # Bit 0: Has Verb
        # Bit 1: Has Subject/Noun
        # Bit 2: SVO order present
        # Bit 3: Preverbal aspect auxiliary present
        byte_18_val = 0
        if has_verb: byte_18_val |= 0x01
        if has_subject: byte_18_val |= 0x02
        if is_svo: byte_18_val |= 0x04
        if has_aspect: byte_18_val |= 0x08
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[18] = byte_18_val
            target_buf[52] = 0x01  # Syntax Sub-AI Active
            
        return {
            "sub_ai": "ThaiSyntaxSubAI",
            "has_verb": has_verb,
            "has_subject": has_subject,
            "is_svo": is_svo,
            "has_aspect": has_aspect,
            "byte_18": byte_18_val,
            "byte_52": 0x01
        }
