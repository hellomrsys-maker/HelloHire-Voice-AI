"""
Swahili Engine — Editorial Sub-AI
Responsible for concordial agreement audit, verbal extension tracking, error synthesis, and confidence scoring.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any, List
from ..analysis.concord_agreement_analyzer import ConcordAgreementAnalyzer
from ..skills.tokenization import tokenize_words

class SwahiliEditorialSubAI:
    """Sub-AI dedicated to Swahili concord verification, verbal extensions, and editorial scoring."""

    def __init__(self):
        self.concord_analyzer = ConcordAgreementAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Swahili grammar and synchronously update AMSV buffer.
        Byte 19: concord_error_flags
          Bit 0: Adjective concord error
          Bit 1: Demonstrative concord error
          Bit 2: Verb SP concord error
        Byte 21: verbal_extension_flags
          Bit 0: Applicative (-ia/-ea)
          Bit 1: Causative (-isha/-esha)
          Bit 2: Passive (-wa)
          Bit 3: Reciprocal (-ana)
        Bytes 24..27: sub_ai_confidence (float32)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        c_res = self.concord_analyzer.analyze(text)
        violations = c_res.get("violations", [])
        
        concord_flags = 0
        for v in violations:
            err_type = v.get("type", "")
            if err_type == "adjective_concord_error":
                concord_flags |= (1 << 0)
            elif err_type == "demonstrative_concord_error":
                concord_flags |= (1 << 1)
            elif err_type == "verb_concord_error":
                concord_flags |= (1 << 2)
            else:
                concord_flags |= (1 << 0)
                
        # Check verbal extension suffixes
        tokens = tokenize_words(text)
        ext_flags = 0
        for t in tokens:
            t_lower = t.lower()
            if any(t_lower.endswith(sfx) or sfx in t_lower for sfx in ["ana", "anapo", "aneni"]):
                ext_flags |= (1 << 3) # Reciprocal
            if any(t_lower.endswith(sfx) or sfx in t_lower for sfx in ["isha", "esha", "iza", "eza"]):
                ext_flags |= (1 << 1) # Causative
            if any(t_lower.endswith(sfx) for sfx in ["wa", "iwa", "ewa"]):
                ext_flags |= (1 << 2) # Passive
            if any(sfx in t_lower for sfx in ["ia", "ea"]) and not (ext_flags & (1 << 1)):
                ext_flags |= (1 << 0) # Applicative
                
        confidence = max(0.0, 1.0 - (len(violations) * 0.15))
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = concord_flags
            amsv_buffer[21] = ext_flags
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "SwahiliEditorialSubAI",
            "status": "success",
            "violations": violations,
            "concord_error_flags": concord_flags,
            "verbal_extension_flags": ext_flags,
            "confidence": round(confidence, 3),
            "is_valid": len(violations) == 0
        }
