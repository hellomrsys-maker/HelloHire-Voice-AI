"""
Vietnamese Syntax Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 18 (0x12): Syntax Capability Status / SVO Flag
- Byte 52 (0x34): Syntax Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.brain.skills.pos_tagging import VietnamesePOSTagger

class VietnameseSyntaxSubAI:
    """
    Sub-AI dedicated to Vietnamese isolating SVO topology,
    head-initial noun phrases, and serial verb chaining.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.tagger = VietnamesePOSTagger()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes syntax and writes directly to physical memory offsets."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tagged = self.tagger.tag_sentence(text)
        
        has_verb = any(pos == "VERB" for _, pos in tagged)
        has_noun = any(pos in {"NOUN", "PRON"} for _, pos in tagged)
        has_clf = any(pos == "CLF" for _, pos in tagged)
        has_tam = any(pos == "PART" for _, pos in tagged)
        
        # Byte 18 Bitfield:
        # Bit 0: Has Verb
        # Bit 1: Has Subject/Object Noun
        # Bit 2: Has Classifier
        # Bit 3: Has TAM Particle
        byte_18_val = 0
        if has_verb: byte_18_val |= 0x01
        if has_noun: byte_18_val |= 0x02
        if has_clf:  byte_18_val |= 0x04
        if has_tam:  byte_18_val |= 0x08
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[18] = byte_18_val
            target_buf[52] = 0x01  # Syntax Sub-AI Active
            
        return {
            "sub_ai": "VietnameseSyntaxSubAI",
            "has_verb": has_verb,
            "has_noun": has_noun,
            "has_classifier": has_clf,
            "has_tam": has_tam,
            "byte_18": byte_18_val,
            "byte_52": 0x01
        }
