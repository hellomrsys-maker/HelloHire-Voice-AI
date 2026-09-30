"""
Italian Engine — Phonology Sub-AI
Responsible for elisions (l'amico, c'è), truncations (buon giorno, dottore -> dottor),
and syntactic doubling / gemination.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 20 and 53.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words

class ItalianPhonologySubAI:
    """Sub-AI dedicated to Italian phonology, elision, truncation, and gemination."""

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Italian phonology and synchronously update AMSV buffer.
        Byte 20: phonology_flags
          Bit 0: Elision present (l', c', d', un')
          Bit 1: Truncation present (buon, bel, dottor, professor)
          Bit 2: Syntactic doubling / geminate
        Byte 53: phonology_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        
        has_elision = any("'" in t for t in tokens)
        has_truncation = any(
            t.lower() in {"buon", "bel", "dottor", "professor", "ingegner", "gran", "san"}
            for t in tokens
        )
        has_geminate = any(
            t.lower().startswith(("dammi", "dimmi", "fallo", "dallo", "fammi")) or "gn" in t.lower() or "gli" in t.lower()
            for t in tokens
        )
        
        flags = 0
        if has_elision:
            flags |= (1 << 0)
        if has_truncation:
            flags |= (1 << 1)
        if has_geminate:
            flags |= (1 << 2)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[20] = flags
            amsv_buffer[53] = 1 # Active
            
        return {
            "sub_ai": "ItalianPhonologySubAI",
            "status": "success",
            "has_elision": has_elision,
            "has_truncation": has_truncation,
            "has_geminate": has_geminate,
            "flags": flags,
            "is_valid": True
        }
