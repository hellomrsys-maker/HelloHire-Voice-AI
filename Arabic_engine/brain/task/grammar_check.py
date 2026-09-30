"""
Arabic Engine — Grammar Check Task Pipeline
Conducts end-to-end multi-layer Arabic linguistic verification:
- VSO partial agreement (singular verb before subject)
- SVO full agreement
- Non-human plural deflected agreement (Feminine singular concord)
- Idafa construct constraints (no al-, no tanwin on mudaf)
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences, tokenize_words
from ..analysis.vso_svo_agreement_analyzer import VsoSvoAgreementAnalyzer
from ..analysis.deflected_agreement_analyzer import DeflectedAgreementAnalyzer
from ..analysis.idafa_construct_analyzer import IdafaConstructAnalyzer

class ArabicGrammarChecker:
    """End-to-end task pipeline for comprehensive Arabic linguistic validation."""

    def __init__(self):
        self.vso_svo_analyzer = VsoSvoAgreementAnalyzer()
        self.deflected_analyzer = DeflectedAgreementAnalyzer()
        self.idafa_analyzer = IdafaConstructAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        total_tokens = 0
        all_vso_errors = []
        all_deflected_errors = []
        all_idafa_errors = []
        
        for s in sentences:
            tokens = tokenize_words(s)
            total_tokens += len(tokens)
            
            # 1. VSO/SVO agreement
            v_res = self.vso_svo_analyzer.analyze(s)
            if not v_res["is_valid"]:
                all_vso_errors.extend(v_res["violations"])
                
            # 2. Deflected agreement
            d_res = self.deflected_analyzer.analyze(s)
            if not d_res["is_valid"]:
                all_deflected_errors.extend(d_res["violations"])
                
            # 3. Idafa construct
            i_res = self.idafa_analyzer.analyze(s)
            if not i_res["is_valid"]:
                all_idafa_errors.extend(i_res["violations"])
                
        total_errors = len(all_vso_errors) + len(all_deflected_errors) + len(all_idafa_errors)
        confidence = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "vso_svo_errors": all_vso_errors,
            "deflected_errors": all_deflected_errors,
            "idafa_errors": all_idafa_errors,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(confidence, 3)
        }
