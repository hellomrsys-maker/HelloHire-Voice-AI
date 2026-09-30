"""
Vietnamese Phonology Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 20 (0x14): Tone Orthography & Diacritic Conformity Flag
- Byte 53 (0x35): Phonology Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.brain.skills.tone_engine import VietnameseToneEngine

class VietnamesePhonologySubAI:
    """
    Sub-AI dedicated to 6-tone pitch contours and Quốc Ngữ diacritic orthography.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.tone_engine = VietnameseToneEngine()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Analyzes tones and writes directly to physical AMSV memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        tones = self.tone_engine.analyze_text_tones(text)
        
        # Byte 20 Bitfield:
        # Bit 0: Valid text
        # Bit 1: Contains tone diacritics
        # Bit 2: Multiple distinct tones present
        byte_20_val = 0
        if tones["total_syllables"] > 0:
            byte_20_val |= 0x01
        if tones["has_tones"]:
            byte_20_val |= 0x02
            
        distinct_tones = sum(1 for cnt in tones["tone_counts"].values() if cnt > 0)
        if distinct_tones >= 2:
            byte_20_val |= 0x04
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[20] = byte_20_val
            target_buf[53] = 0x01  # Phonology Sub-AI Active
            
        return {
            "sub_ai": "VietnamesePhonologySubAI",
            "distinct_tones": distinct_tones,
            "tone_counts": tones["tone_counts"],
            "byte_20": byte_20_val,
            "byte_53": 0x01
        }
