"""
Arabic Engine — Editorial Sub-AI
Responsible for Idafa case governance, morphological derivation tracking, and confidence scoring.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.broken_plural_engine import analyze_plural
from ..analysis.idafa_construct_analyzer import IdafaConstructAnalyzer

class ArabicEditorialSubAI:
    """Sub-AI dedicated to Arabic case governance, Idafa error tracking, and editorial scoring."""

    def __init__(self):
        self.idafa_analyzer = IdafaConstructAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Arabic editorial constraints and synchronously update AMSV buffer.
        Byte 19: case_error_flags
          Bit 0: Nominative error
          Bit 1: Accusative error
          Bit 2: Idafa construct error (Mudāf al- or tanwīn)
        Byte 21: morphology_flags
          Bits 0..3: Verb Form number (1..10)
          Bit 4: Broken plural detected
          Bit 5: Dual number detected
        Bytes 24..27: sub_ai_confidence (float32)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        i_res = self.idafa_analyzer.analyze(text)
        tokens = tokenize_words(text)
        
        has_broken_plural = False
        has_dual = False
        
        for t in tokens:
            p_res = analyze_plural(t)
            if p_res["is_plural"] and p_res.get("pattern") in {"fu'ul", "af'al", "mafa'il", "fi'al", "fu''al"}:
                has_broken_plural = True
            if t.lower().endswith("ani") or t.lower().endswith("ayni"):
                has_dual = True
                
        case_flags = 0
        if not i_res["is_valid"]:
            case_flags |= (1 << 2) # Idafa error
            
        morph_flags = 1 # Form I default
        if has_broken_plural:
            morph_flags |= (1 << 4)
        if has_dual:
            morph_flags |= (1 << 5)
            
        total_violations = len(i_res["violations"])
        confidence = max(0.0, 1.0 - (total_violations * 0.15))
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = case_flags
            amsv_buffer[21] = morph_flags
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "ArabicEditorialSubAI",
            "status": "success",
            "idafa_violations": i_res["violations"],
            "has_broken_plural": has_broken_plural,
            "has_dual": has_dual,
            "confidence": round(confidence, 3),
            "is_valid": total_violations == 0,
            "flags": case_flags
        }
