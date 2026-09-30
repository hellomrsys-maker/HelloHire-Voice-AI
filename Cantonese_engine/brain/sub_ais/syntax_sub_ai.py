"""
Cantonese Syntax Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 18 (0x12): Syntax Capability Status / DOC Inversion Bitfield
- Byte 52 (0x34): Syntax Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Cantonese_engine.brain.skills.pos_tagging import tag_pos
from Cantonese_engine.brain.skills.tokenization import tokenize_cantonese
from Cantonese_engine.brain.skills.doc_inversion_engine import analyze_doc_structure

class CantoneseSyntaxSubAI:
    """
    Sub-AI dedicated to Cantonese isolating SVO word order,
    Double Object Construction (V + DO + IO), and postverbal adverbs.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes syntax and writes directly to physical memory offsets."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tokens = tokenize_cantonese(text)
        tagged = tag_pos(tokens)
        doc_analysis = analyze_doc_structure(text)
        
        has_verb = any(pos in {"VERB", "AUX"} for _, pos in tagged)
        has_noun = any(pos in {"NOUN", "PRON"} for _, pos in tagged)
        has_clf = any(pos == "CLF" for _, pos in tagged)
        has_canonical_doc = doc_analysis["is_canonical"] and doc_analysis["verb"] is not None
        
        # Byte 18 Bitfield:
        # Bit 0: Has Verb
        # Bit 1: Has Subject/Object Noun or Pronoun
        # Bit 2: Has Classifier
        # Bit 3: Has Canonical DOC (V + DO + IO)
        byte_18_val = 0
        if has_verb: byte_18_val |= 0x01
        if has_noun: byte_18_val |= 0x02
        if has_clf:  byte_18_val |= 0x04
        if has_canonical_doc: byte_18_val |= 0x08
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[18] = byte_18_val
            target_buf[52] = 0x01  # Syntax Sub-AI Active
            
        return {
            "sub_ai": "CantoneseSyntaxSubAI",
            "has_verb": has_verb,
            "has_noun": has_noun,
            "has_classifier": has_clf,
            "has_canonical_doc": has_canonical_doc,
            "byte_18": byte_18_val,
            "byte_52": 0x01
        }
