"""
Indonesian Engine — Grammar Check Task Pipeline
Conducts end-to-end multi-layer linguistic verification:
- Voice symmetry & nasal assimilation (*mempakai -> memakai)
- Reduplication hyphenation and numeric shorthand (*buku2 -> buku-buku)
- Numeral classifier semantic concord (*sebuah guru -> seorang guru)
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences, tokenize_words
from ..analysis.voice_symmetry_analyzer import VoiceSymmetryAnalyzer
from ..analysis.reduplication_analyzer import ReduplicationAnalyzer
from ..analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer

class IndonesianGrammarChecker:
    """End-to-end task pipeline for Indonesian linguistic validation."""

    def __init__(self):
        self.voice_analyzer = VoiceSymmetryAnalyzer()
        self.redup_analyzer = ReduplicationAnalyzer()
        self.clf_analyzer = ClassifierConcordAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        total_tokens = 0
        all_voice_errors = []
        all_redup_errors = []
        all_clf_errors = []
        
        for s in sentences:
            toks = tokenize_words(s)
            total_tokens += len(toks)
            
            # 1. Voice symmetry & nasal assimilation
            v_res = self.voice_analyzer.analyze(s)
            if not v_res["is_valid"]:
                all_voice_errors.extend(v_res["violations"])
                
            # 2. Reduplication
            r_res = self.redup_analyzer.analyze(s)
            if not r_res["is_valid"]:
                all_redup_errors.extend(r_res["violations"])
                
            # 3. Classifier concord
            c_res = self.clf_analyzer.analyze(s)
            if not c_res["is_valid"]:
                all_clf_errors.extend(c_res["violations"])
                
        total_errors = len(all_voice_errors) + len(all_redup_errors) + len(all_clf_errors)
        confidence = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "voice_errors": all_voice_errors,
            "reduplication_errors": all_redup_errors,
            "classifier_errors": all_clf_errors,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(confidence, 3)
        }
