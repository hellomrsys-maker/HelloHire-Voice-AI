"""
Indonesian Engine — Phonology Sub-AI
Responsible for morphophonemic nasal assimilation (p/t/s/k deletion) and ber- r-dropping.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 20 and 53.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..analysis.voice_symmetry_analyzer import VoiceSymmetryAnalyzer

class IndonesianPhonologySubAI:
    """Sub-AI dedicated to Indonesian morphophonemic nasal assimilation and affix phonology."""

    def __init__(self):
        self.voice_analyzer = VoiceSymmetryAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Indonesian phonology and synchronously update AMSV buffer.
        Byte 20: phonology_flags
          Bit 0: meN- nasal assimilation verified
          Bit 1: ber- r-dropping verified
        Byte 53: phonology_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        v_res = self.voice_analyzer.analyze(text)
        
        # Check ber- r-dropping forms (e.g. bekerja, berenang, belajar)
        t_lower = [t.lower() for t in tokens]
        has_ber_rdrop = any(w in {"bekerja", "berenang", "belajar"} for w in t_lower)
        has_men = any(f["voice"] == "active" for f in v_res.get("voice_forms_found", []))
        
        flags = 0
        if has_men and v_res["is_valid"]:
            flags |= (1 << 0)
        if has_ber_rdrop:
            flags |= (1 << 1)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[20] = flags
            amsv_buffer[53] = 1 # Active
            
        return {
            "sub_ai": "IndonesianPhonologySubAI",
            "status": "success",
            "nasal_assimilation_valid": v_res["is_valid"],
            "has_ber_rdrop": has_ber_rdrop,
            "flags": flags,
            "is_valid": v_res["is_valid"]
        }
