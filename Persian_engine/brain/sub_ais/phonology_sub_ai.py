"""
Persian Phonology Sub-AI
Operating under The Zero-Bridge Synchronous Memory Rule.
Syncs directly to AMSV physical offsets:
- Byte 20 (0x14): ZWNJ & Orthographic Conformity Flag
- Byte 53 (0x35): Phonology Sub-AI Active Flag
"""

from typing import Dict, Any, Optional
from Persian_engine.brain.skills.tokenization import PersianTokenizer, ZWNJ

class PersianPhonologySubAI:
    """
    Sub-AI dedicated to Persian phonology, ZWNJ boundary integrity,
    and Perso-Arabic character normalization.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.memory_buffer = memory_buffer
        self.tokenizer = PersianTokenizer()

    def process(self, text: str, buffer: Optional[bytearray] = None) -> Dict[str, Any]:
        """Audits orthography/phonology and writes directly to physical memory."""
        target_buf = buffer if buffer is not None else self.memory_buffer
        
        has_zwnj = ZWNJ in text
        tokens = self.tokenizer.tokenize_words(text)
        
        # Check for non-standard Arabic characters (e.g. Arabic Kaf or Yeh)
        has_arabic_kaf = '\u0643' in text
        has_arabic_yeh = '\u064A' in text or '\u0649' in text
        is_normalized = not (has_arabic_kaf or has_arabic_yeh)
        
        # Byte 20: Bit 0 = Normalized, Bit 1 = Contains ZWNJ, Bit 2 = Valid Token Count
        byte_20_val = 0
        if is_normalized:
            byte_20_val |= 0x01
        if has_zwnj:
            byte_20_val |= 0x02
        if len(tokens) > 0:
            byte_20_val |= 0x04
            
        if target_buf is not None and len(target_buf) >= 64:
            target_buf[20] = byte_20_val
            target_buf[53] = 0x01  # Phonology Sub-AI Active
            
        return {
            "sub_ai": "PersianPhonologySubAI",
            "is_normalized": is_normalized,
            "has_zwnj": has_zwnj,
            "token_count": len(tokens),
            "byte_20": byte_20_val,
            "byte_53": 0x01
        }
