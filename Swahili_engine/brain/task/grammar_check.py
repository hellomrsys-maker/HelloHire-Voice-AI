"""
Swahili Engine — Grammar Check Task Pipeline
Conducts end-to-end multi-layer Swahili grammar verification:
- Noun class concordial agreement across adjectives, demonstratives, possessives
- Verbal agglutinative template validation
- Monosyllabic verb dummy 'ku-' retention
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences, tokenize_words
from ..analysis.concord_agreement_analyzer import ConcordAgreementAnalyzer
from ..analysis.verbal_template_analyzer import VerbalTemplateAnalyzer

class SwahiliGrammarChecker:
    """End-to-end task pipeline for comprehensive Swahili linguistic validation."""

    def __init__(self):
        self.concord_analyzer = ConcordAgreementAnalyzer()
        self.verbal_analyzer = VerbalTemplateAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        total_tokens = 0
        all_concord_errors = []
        all_verbal_errors = []
        
        for s in sentences:
            tokens = tokenize_words(s)
            total_tokens += len(tokens)
            
            c_res = self.concord_analyzer.analyze(s)
            if not c_res["is_valid"]:
                all_concord_errors.extend(c_res["violations"])
                
            v_res = self.verbal_analyzer.analyze(s)
            if not v_res["is_valid"]:
                all_verbal_errors.extend(v_res["violations"])
                
        total_errors = len(all_concord_errors) + len(all_verbal_errors)
        confidence = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "concord_errors": all_concord_errors,
            "verbal_template_errors": all_verbal_errors,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(confidence, 3)
        }
