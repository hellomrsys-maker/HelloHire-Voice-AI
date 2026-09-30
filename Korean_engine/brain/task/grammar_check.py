"""
Korean Engine — Grammar Check Task Pipeline
Conducts end-to-end multi-layer Korean grammar verification:
- Postpositional particle-batchim concord (은/는, 이/가, 을/를, 과/와, 으로/로)
- Tripartite honorific harmony
- Speech level consistency
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences, tokenize_eojeol
from ..analysis.particle_agreement_analyzer import ParticleAgreementAnalyzer
from ..analysis.honorific_concord_analyzer import HonorificConcordAnalyzer
from ..analysis.speech_level_analyzer import SpeechLevelAnalyzer

class KoreanGrammarChecker:
    """End-to-end task pipeline for comprehensive Korean linguistic validation."""

    def __init__(self):
        self.particle_analyzer = ParticleAgreementAnalyzer()
        self.honorific_analyzer = HonorificConcordAnalyzer()
        self.speech_analyzer = SpeechLevelAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        total_tokens = 0
        all_particle_errors = []
        all_honorific_errors = []
        
        for s in sentences:
            tokens = tokenize_eojeol(s)
            total_tokens += len(tokens)
            
            p_res = self.particle_analyzer.analyze(s)
            if not p_res["is_valid"]:
                all_particle_errors.extend(p_res["violations"])
                
            h_res = self.honorific_analyzer.analyze(s)
            if not h_res["is_harmonious"]:
                all_honorific_errors.extend(h_res["violations"])
                
        sl_res = self.speech_analyzer.analyze(text)
        speech_clash = sl_res["is_clash"]
        
        total_errors = len(all_particle_errors) + len(all_honorific_errors) + (1 if speech_clash else 0)
        confidence = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "particle_errors": all_particle_errors,
            "honorific_errors": all_honorific_errors,
            "speech_level": sl_res["primary_level"],
            "speech_clash": speech_clash,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(confidence, 3)
        }
