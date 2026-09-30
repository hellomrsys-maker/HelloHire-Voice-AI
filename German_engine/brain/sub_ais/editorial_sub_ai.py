"""
German Engine — Editorial Sub-AI
Responsible for morphological concord, case government, adjective inflection, and overall style score.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 19, 21, 24..27, and 55.
"""

import struct
from typing import Dict, Any
from ..analysis.case_government_analyzer import CaseGovernmentAnalyzer
from ..analysis.adjective_agreement_analyzer import AdjectiveAgreementAnalyzer

class GermanEditorialSubAI:
    """Sub-AI dedicated to editorial correction, morphological concord, and quality scoring."""

    def __init__(self):
        self.case_gov = CaseGovernmentAnalyzer()
        self.adj_agree = AdjectiveAgreementAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process German grammar and synchronously update AMSV buffer.
        Byte 19: case_error_flags
          Bit 0: Nom error, Bit 1: Akk error, Bit 2: Dat error, Bit 3: Gen error
        Byte 21: adjective_decl_flags
          Bit 0: Weak error, Bit 1: Strong error, Bit 2: Mixed error
        Bytes 24..27: sub_ai_confidence (float32)
        Byte 55: editorial_sub_ai_id = 1 (active)
        """
        case_res = self.case_gov.analyze(text)
        adj_res = self.adj_agree.analyze(text)
        
        case_flags = 0
        for v in case_res["violations"]:
            gov = v.get("governed_case", "")
            if "accusative" in gov:
                case_flags |= (1 << 1)
            elif "dative" in gov:
                case_flags |= (1 << 2)
            elif "genitive" in gov:
                case_flags |= (1 << 3)
            else:
                case_flags |= (1 << 0)
                
        adj_flags = 0
        if not adj_res["is_valid"]:
            adj_flags |= (1 << 0) # Weak or general declension error
            
        total_errors = len(case_res["violations"]) + len(adj_res["violations"])
        confidence = max(0.0, 1.0 - (total_errors * 0.2))
        
        # Zero-bridge synchronous write to buffer
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[19] = case_flags
            amsv_buffer[21] = adj_flags
            # Write float32 confidence at 24..27
            struct.pack_into("<f", amsv_buffer, 24, float(confidence))
            amsv_buffer[55] = 1 # Active
            
        return {
            "sub_ai": "GermanEditorialSubAI",
            "status": "success",
            "case_violations": case_res["violations"],
            "adjective_violations": adj_res["violations"],
            "confidence": round(confidence, 3),
            "is_valid": total_errors == 0
        }
