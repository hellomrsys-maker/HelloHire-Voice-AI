"""
Indonesian Engine — Editorial Sub-AI
Responsible for morphology validation, reduplication auditing, aspect particles, and holistic confidence scoring.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.aspect_negation_engine import detect_aspect
from ..analysis.reduplication_analyzer import ReduplicationAnalyzer

class IndonesianEditorialSubAI:
    """Sub-AI dedicated to Indonesian morphological completeness, reduplication, and confidence scoring."""

    def __init__(self):
        self.redup_analyzer = ReduplicationAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Indonesian editorial constraints and synchronously update AMSV buffer.
        Byte 19: morphology_flags
          Bit 0: Affix valid
          Bit 1: Circumfix ke-an/pe-an detected
          Bit 2: Reduplication detected
        Byte 21: aspect_flags
          Bit 0: sudah/telah (perfective)
          Bit 1: belum (negative perfective)
          Bit 2: sedang/tengah (progressive)
          Bit 3: akan (prospective)
        Bytes 24..27: sub_ai_confidence (float32 LE)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        r_res = self.redup_analyzer.analyze(text)
        asp_res = detect_aspect(text)
        tokens = tokenize_words(text)
        
        has_redup = len(r_res.get("reduplications_found", [])) > 0
        has_circumfix = any(
            t.lower().startswith("ke") and t.lower().endswith("an") or
            t.lower().startswith(("pen", "pem", "peng", "peny", "pe")) and t.lower().endswith("an")
            for t in tokens
        )
        
        morph_flags = 0
        if len(tokens) > 0:
            morph_flags |= (1 << 0) # Affix valid base
        if has_circumfix:
            morph_flags |= (1 << 1)
        if has_redup:
            morph_flags |= (1 << 2)
            
        aspect_flags = 0
        aspects = asp_res.get("aspects", [])
        if "perfective" in aspects:
            aspect_flags |= (1 << 0)
        if "negative_perfective" in aspects:
            aspect_flags |= (1 << 1)
        if "progressive" in aspects:
            aspect_flags |= (1 << 2)
        if "prospective" in aspects:
            aspect_flags |= (1 << 3)
            
        total_violations = len(r_res["violations"])
        confidence = max(0.0, 1.0 - (total_violations * 0.2))
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = morph_flags
            amsv_buffer[21] = aspect_flags
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "IndonesianEditorialSubAI",
            "status": "success",
            "reduplication_analysis": r_res,
            "has_reduplication": has_redup,
            "has_circumfix": has_circumfix,
            "aspects": aspects,
            "confidence": round(confidence, 3),
            "is_valid": total_violations == 0,
            "flags": morph_flags
        }
