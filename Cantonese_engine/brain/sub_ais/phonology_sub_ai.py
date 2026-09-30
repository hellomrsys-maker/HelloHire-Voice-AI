"""
Cantonese Phonology Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 20 (0x14): 9-Tone & Jyutping Phonological Orthography Flag
- Byte 53 (0x35): Phonology Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Cantonese_engine.brain.skills.tone_engine import text_to_jyutping, is_entering_tone

class CantonesePhonologySubAI:
    """
    Sub-AI dedicated to Cantonese 9-tone pitch contours (including checked tones on -p, -t, -k)
    and LSHK Jyutping phonological consistency.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes tones and writes directly to physical AMSV memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        profiles = text_to_jyutping(text)
        
        has_text = len(profiles) > 0
        has_entering = any(p["is_checked_tone"] for p in profiles)
        distinct_tones = len(set(p["tone_number"] for p in profiles if p["tone_number"] > 0))
        
        # Byte 20 Bitfield:
        # Bit 0: Valid text present
        # Bit 1: Contains entering tone (入聲 7, 8, 9 on -p, -t, -k)
        # Bit 2: Multiple distinct tones present (>= 2)
        byte_20_val = 0
        if has_text:
            byte_20_val |= 0x01
        if has_entering:
            byte_20_val |= 0x02
        if distinct_tones >= 2:
            byte_20_val |= 0x04
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[20] = byte_20_val
            target_buf[53] = 0x01  # Phonology Sub-AI Active
            
        return {
            "sub_ai": "CantonesePhonologySubAI",
            "syllable_count": len(profiles),
            "has_entering_tone": has_entering,
            "distinct_tones": distinct_tones,
            "byte_20": byte_20_val,
            "byte_53": 0x01
        }
