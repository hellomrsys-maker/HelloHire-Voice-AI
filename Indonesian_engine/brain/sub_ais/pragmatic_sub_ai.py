"""
Indonesian Engine — Pragmatic Sub-AI
Responsible for social deixis (Bapak/Ibu vs Kamu/Anda), surat resmi epistolary protocol, and peribahasa proverbs.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any, List
from ..skills.pragmatics_engine import classify_register

PERIBAHASA_LIST = [
    "ada udang di balik batu", "sambil menyelam minum air", "tong kosong nyaring bunyinya",
    "besar pasak daripada tiang", "air tenang menghanyutkan"
]

class IndonesianPragmaticSubAI:
    """Sub-AI dedicated to Indonesian pragmatic register, honorifics, and proverbs."""

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Indonesian pragmatics and synchronously update AMSV buffer.
        Byte 22: register_tier
          0: Informal (Bahasa Gaul)
          1: Formal (Bahasa Baku)
          2: Diplomatic / Surat Resmi
        Byte 23: pragmatic_flags
          Bit 0: Bapak/Ibu honorific present
          Bit 1: Formal surat resmi closing formula
          Bit 2: Peribahasa (proverb) detected
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        reg_info = classify_register(text)
        reg_tier = 1 if reg_info["register"] == "formal" else 0
        
        t_clean = text.lower()
        has_honorific = any(h in t_clean for h in ["bapak", "ibu", "saudara", "saudari"])
        has_closing = any(c in t_clean for c in ["hormat kami", "hormat saya", "terima kasih"])
        has_proverb = any(p in t_clean for p in PERIBAHASA_LIST)
        
        if has_closing and has_honorific:
            reg_tier = 2 # Diplomatic / Surat Resmi
            
        flags = 0
        if has_honorific:
            flags |= (1 << 0)
        if has_closing:
            flags |= (1 << 1)
        if has_proverb:
            flags |= (1 << 2)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = reg_tier
            amsv_buffer[23] = flags
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "IndonesianPragmaticSubAI",
            "status": "success",
            "register": reg_info["register"],
            "register_tier": reg_tier,
            "has_honorific": has_honorific,
            "has_closing": has_closing,
            "has_proverb": has_proverb,
            "flags": flags,
            "is_valid": True
        }
