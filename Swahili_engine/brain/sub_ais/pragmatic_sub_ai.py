"""
Swahili Engine — Pragmatic Sub-AI
Responsible for greeting protocols, deference deixis (Shikamoo/Marahaba), head noun class detection, and social etiquette.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.noun_class_engine import identify_noun_class
from ..skills.pos_tagging import tag_pos

class SwahiliPragmaticSubAI:
    """Sub-AI dedicated to Swahili pragmatic registers, greeting exchanges, and social deixis."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Swahili pragmatics and synchronously update AMSV buffer.
        Byte 22: noun_class_head (1..18, 0=None)
        Byte 23: pragmatic_flags
          Bit 0: Shikamoo present
          Bit 1: Marahaba present
          Bit 2: Greeting clash or improper register
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        text_lower = text.lower()
        
        # Detect head noun class from first noun in sentence
        head_class = 0
        for t in tags:
            if t["upos"] in {"NOUN", "PROPN"}:
                head_class = identify_noun_class(t["word"])
                break
                
        has_shikamoo = "shikamoo" in text_lower
        has_marahaba = "marahaba" in text_lower
        has_hujambo = "hujambo" in text_lower
        
        flags = 0
        if has_shikamoo:
            flags |= (1 << 0)
        if has_marahaba:
            flags |= (1 << 1)
            
        # Greeting clash detection: e.g. using shikamoo and informal slang like 'mambo' simultaneously
        is_clash = False
        if has_shikamoo and ("mambo" in text_lower or "sasa" in text_lower):
            is_clash = True
            flags |= (1 << 2)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = head_class & 0xFF
            amsv_buffer[23] = flags
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "SwahiliPragmaticSubAI",
            "status": "success",
            "noun_class_head": head_class,
            "has_shikamoo": has_shikamoo,
            "has_marahaba": has_marahaba,
            "is_clash": is_clash,
            "flags": flags,
            "is_valid": not is_clash
        }
