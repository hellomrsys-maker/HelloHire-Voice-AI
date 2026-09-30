"""
Arabic Engine — Syntax Sub-AI
Responsible for VSO partial concord, SVO full agreement, non-human plural deflected concord, and Idafa detection.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 18 and 52.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..analysis.vso_svo_agreement_analyzer import VsoSvoAgreementAnalyzer
from ..analysis.deflected_agreement_analyzer import DeflectedAgreementAnalyzer
from ..analysis.idafa_construct_analyzer import IdafaConstructAnalyzer

class ArabicSyntaxSubAI:
    """Sub-AI dedicated to Arabic clausal syntax, VSO/SVO agreement, and deflected concord."""

    def __init__(self):
        self.vso_svo_analyzer = VsoSvoAgreementAnalyzer()
        self.deflected_analyzer = DeflectedAgreementAnalyzer()
        self.idafa_analyzer = IdafaConstructAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Arabic syntactic structure and synchronously update AMSV buffer.
        Byte 18: syntax_flags
          Bit 0: VSO valid agreement verified
          Bit 1: Deflected agreement verified
          Bit 2: Idafa construct active
          Bit 3: Relative clause
        Byte 52: syntax_sub_ai_id = 1 (active)
        """
        v_res = self.vso_svo_analyzer.analyze(text)
        d_res = self.deflected_analyzer.analyze(text)
        i_res = self.idafa_analyzer.analyze(text)
        
        has_vso_valid = v_res.get("clause_order") == "VSO" and v_res["is_valid"]
        has_deflected_valid = len(d_res.get("checked_pairs", [])) > 0 and d_res["is_valid"]
        has_idafa = len(i_res.get("constructs_found", [])) > 0
        has_relative = any(rel in text.lower() for rel in ["alladhi", "allati", "alladhina", "الذي", "التي", "الذين"])
        
        flags = 0
        if has_vso_valid or (v_res.get("clause_order") == "SVO" and v_res["is_valid"]):
            flags |= (1 << 0)
        if has_deflected_valid:
            flags |= (1 << 1)
        if has_idafa:
            flags |= (1 << 2)
        if has_relative:
            flags |= (1 << 3)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[18] = flags
            amsv_buffer[52] = 1 # Active
            
        is_valid = v_res["is_valid"] and d_res["is_valid"] and i_res["is_valid"]
        
        return {
            "sub_ai": "ArabicSyntaxSubAI",
            "status": "success",
            "clause_order": v_res.get("clause_order"),
            "vso_svo": v_res,
            "deflected_agreement": d_res,
            "idafa": i_res,
            "flags": flags,
            "is_valid": is_valid
        }
