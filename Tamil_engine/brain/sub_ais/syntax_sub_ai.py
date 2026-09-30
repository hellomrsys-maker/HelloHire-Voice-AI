"""
Tamil Syntax Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 18 (0x12): Syntax Capability Status / SOV Bitfield
- Byte 52 (0x34): Syntax Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Tamil_engine.brain.skills.pos_tagging import tag_pos
from Tamil_engine.brain.skills.tokenization import tokenize_tamil
from Tamil_engine.brain.analysis.sov_word_order_analyzer import SovWordOrderAnalyzer

class TamilSyntaxSubAI:
    """
    Sub-AI dedicated to Tamil head-final SOV syntax and postpositional structure.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.sov_analyzer = SovWordOrderAnalyzer()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes syntax and writes directly to physical memory offsets."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tokens = tokenize_tamil(text.rstrip(".,!?"))
        tagged = tag_pos(tokens)
        sov_res = self.sov_analyzer.analyze(text)
        
        has_verb = any(pos in {"VERB", "PART"} for _, pos in tagged)
        has_subject = any(pos in {"NOUN", "PRON"} for _, pos in tagged)
        has_postposition = any(pos == "ADP" for _, pos in tagged)
        is_sov = sov_res["is_sov"]
        
        # Byte 18 Bitfield:
        # Bit 0: Has Verb
        # Bit 1: Has Subject/Noun
        # Bit 2: Has Postposition
        # Bit 3: Is Canonical SOV
        byte_18_val = 0
        if has_verb: byte_18_val |= 0x01
        if has_subject: byte_18_val |= 0x02
        if has_postposition: byte_18_val |= 0x04
        if is_sov: byte_18_val |= 0x08
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[18] = byte_18_val
            target_buf[52] = 0x01  # Syntax Sub-AI Active
            
        return {
            "sub_ai": "TamilSyntaxSubAI",
            "has_verb": has_verb,
            "has_subject": has_subject,
            "is_sov": is_sov,
            "byte_18": byte_18_val,
            "byte_52": 0x01
        }
