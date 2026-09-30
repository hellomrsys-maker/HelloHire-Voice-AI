"""
Thai Phonology Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 20 (0x14): 5-Tone Orthography Bitfield
- Byte 53 (0x35): Phonology Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Thai_engine.brain.skills.tone_engine import calculate_syllable_tone
from Thai_engine.brain.skills.tokenization import tokenize_thai

class ThaiPhonologySubAI:
    """
    Sub-AI dedicated to 5-tone pitch calculation and consonant class conformity.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes tones and writes directly to physical memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tokens = tokenize_thai(text)
        tone_profiles = [calculate_syllable_tone(t) for t in tokens if any('\u0e01' <= c <= '\u0e2e' for c in t)]
        
        has_text = len(tone_profiles) > 0
        has_tone_marks = any(any(m in t for m in "่้๊๋") for t in tokens)
        distinct_tones = len(set(p["tone_name"] for p in tone_profiles if p["tone_name"] != "unknown"))
        
        # Byte 20 Bitfield:
        # Bit 0: Valid text
        # Bit 1: Tone marks present
        # Bit 2: Multiple distinct tones present (>= 2)
        byte_20_val = 0
        if has_text: byte_20_val |= 0x01
        if has_tone_marks: byte_20_val |= 0x02
        if distinct_tones >= 2: byte_20_val |= 0x04
        
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[20] = byte_20_val
            target_buf[53] = 0x01  # Phonology Sub-AI Active
            
        return {
            "sub_ai": "ThaiPhonologySubAI",
            "syllable_count": len(tone_profiles),
            "distinct_tones": distinct_tones,
            "has_tone_marks": has_tone_marks,
            "byte_20": byte_20_val,
            "byte_53": 0x01
        }
