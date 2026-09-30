"""
Italian Engine — Editorial Sub-AI
Responsible for auxiliary validation (essere vs avere), participle concord, and holistic confidence scoring.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..analysis.auxiliary_agreement_analyzer import AuxiliaryAgreementAnalyzer

class ItalianEditorialSubAI:
    """Sub-AI dedicated to Italian auxiliary choice, agreement, and editorial confidence scoring."""

    def __init__(self):
        self.aux_analyzer = AuxiliaryAgreementAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Italian editorial constraints and synchronously update AMSV buffer.
        Byte 19: auxiliary_flags
          Bit 0: Avere selected
          Bit 1: Essere selected
          Bit 2: Participle concord error
        Byte 21: morphology_flags
          Bits 0..2: Conjugation class (1: -are, 2: -ere, 3: -ire)
          Bit 3: Irregular verb detected
          Bit 4: Inchoative (-isc-)
        Bytes 24..27: sub_ai_confidence (float32 LE)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        a_res = self.aux_analyzer.analyze(text)
        tokens = tokenize_words(text)
        
        has_essere = any(c["aux_type"] == "essere" for c in a_res.get("checked_constructions", []))
        has_avere = any(c["aux_type"] == "avere" for c in a_res.get("checked_constructions", []))
        has_concord_error = len(a_res.get("violations", [])) > 0
        
        aux_flags = 0
        if has_avere:
            aux_flags |= (1 << 0)
        if has_essere:
            aux_flags |= (1 << 1)
        if has_concord_error:
            aux_flags |= (1 << 2)
            
        # Morphology flags
        morph_flags = 1 # default 1st conj
        t_lower = [t.lower() for t in tokens]
        if any(w in {"essere", "avere", "andare", "fare", "dire", "venire", "potere", "volere", "dovere"} for w in t_lower):
            morph_flags |= (1 << 3)
            
        total_violations = len(a_res["violations"])
        confidence = max(0.0, 1.0 - (total_violations * 0.2))
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = aux_flags
            amsv_buffer[21] = morph_flags
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "ItalianEditorialSubAI",
            "status": "success",
            "auxiliary_violations": a_res["violations"],
            "has_essere": has_essere,
            "has_avere": has_avere,
            "confidence": round(confidence, 3),
            "is_valid": total_violations == 0,
            "flags": aux_flags
        }
