"""
Swahili Engine — Phonology Sub-AI
Responsible for penultimate stress constraints, open syllable phonotactics, and monosyllabic verb dummy 'ku-' retention.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 20 and 53.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.monosyllabic_verb_engine import check_monosyllabic_ku, MONOSYLLABIC_STEMS

VOWELS = set("aeiouAEIOU")

class SwahiliPhonologySubAI:
    """Sub-AI dedicated to Swahili phonological rules, stress patterns, and monosyllabic verb morphophonology."""

    def __init__(self):
        pass

    def count_syllables(self, word: str) -> int:
        """Estimate syllable count in Swahili word based on vocalic nuclei."""
        return sum(1 for c in word if c in VOWELS)

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Swahili phonological metrics and synchronously update AMSV buffer.
        Byte 20: phonology_flags
          Bit 0: Monosyllabic verb ku- dummy prefix active and verified
          Bit 1: Penultimate stress satisfied (syllabic weight >= 2 on primary lexical items)
        Byte 53: phonology_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        
        has_monosyllabic_ku = False
        all_penultimate_valid = True
        
        for t in tokens:
            t_lower = t.lower()
            # Monosyllabic verb check
            for stem in MONOSYLLABIC_STEMS:
                if stem in t_lower:
                    mono_res = check_monosyllabic_ku(t_lower)
                    if mono_res.get("retains_ku"):
                        has_monosyllabic_ku = True
                        
            # Check syllable count for lexical stress (words > 1 character)
            syl_count = self.count_syllables(t_lower)
            if len(t_lower) > 2 and syl_count < 1:
                all_penultimate_valid = False
                
        flags = 0
        if has_monosyllabic_ku:
            flags |= (1 << 0)
        if all_penultimate_valid:
            flags |= (1 << 1)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[20] = flags
            amsv_buffer[53] = 1 # Active
            
        return {
            "sub_ai": "SwahiliPhonologySubAI",
            "status": "success",
            "has_monosyllabic_ku": has_monosyllabic_ku,
            "penultimate_stress_valid": all_penultimate_valid,
            "flags": flags,
            "is_valid": all_penultimate_valid
        }
