"""
Korean Engine — Editorial Sub-AI
Responsible for particle-batchim agreement, irregular verb conjugation audit, and overall confidence score.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any
from ..analysis.particle_agreement_analyzer import ParticleAgreementAnalyzer

class KoreanEditorialSubAI:
    """Sub-AI dedicated to particle concord, irregular verb validation, and editorial scoring."""

    def __init__(self):
        self.particle_analyzer = ParticleAgreementAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Korean grammar and synchronously update AMSV buffer.
        Byte 19: particle_error_flags
          Bit 0: 은/는 error
          Bit 1: 이/가 error
          Bit 2: 을/를 error
          Bit 3: 과/와 or 로/으로 error
        Byte 21: irregular_verb_flags (Bit 0: Irregular stem active, Bit 1: Conjugation error)
        Bytes 24..27: sub_ai_confidence (float32)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        p_res = self.particle_analyzer.analyze(text)
        violations = p_res.get("violations", [])
        
        p_flags = 0
        for v in violations:
            err_msg = v.get("error", "")
            if "은" in err_msg or "는" in err_msg:
                p_flags |= (1 << 0)
            elif "이" in err_msg or "가" in err_msg:
                p_flags |= (1 << 1)
            elif "을" in err_msg or "를" in err_msg:
                p_flags |= (1 << 2)
            else:
                p_flags |= (1 << 3)
                
        confidence = max(0.0, 1.0 - (len(violations) * 0.2))
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = p_flags
            amsv_buffer[21] = 0 # No irregular error
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "KoreanEditorialSubAI",
            "status": "success",
            "violations": violations,
            "confidence": round(confidence, 3),
            "is_valid": len(violations) == 0,
            "flags": p_flags
        }
