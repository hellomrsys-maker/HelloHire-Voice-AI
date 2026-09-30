"""
Italian Engine — Grammar Check Task Pipeline
Conducts comprehensive multi-layer verification:
- Auxiliary selection (essere vs avere)
- Past participle gender/number concord
- Clitic cluster transformations (me lo, glielo)
- Subjunctive mood concord in subordinate clauses
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences, tokenize_words
from ..analysis.auxiliary_agreement_analyzer import AuxiliaryAgreementAnalyzer
from ..analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from ..analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer

class ItalianGrammarChecker:
    """End-to-end task pipeline for Italian linguistic validation."""

    def __init__(self):
        self.aux_analyzer = AuxiliaryAgreementAnalyzer()
        self.clitic_analyzer = CliticPlacementAnalyzer()
        self.subj_analyzer = SubjunctiveConcordAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        total_tokens = 0
        all_aux_errors = []
        all_clitic_errors = []
        all_subj_errors = []
        
        for s in sentences:
            toks = tokenize_words(s)
            total_tokens += len(toks)
            
            # 1. Auxiliary & participle agreement
            a_res = self.aux_analyzer.analyze(s)
            if not a_res["is_valid"]:
                all_aux_errors.extend(a_res["violations"])
                
            # 2. Clitic clusters
            c_res = self.clitic_analyzer.analyze(s)
            if not c_res["is_valid"]:
                all_clitic_errors.extend(c_res["violations"])
                
            # 3. Subjunctive concord
            s_res = self.subj_analyzer.analyze(s)
            if not s_res["is_valid"]:
                all_subj_errors.extend(s_res["violations"])
                
        total_errors = len(all_aux_errors) + len(all_clitic_errors) + len(all_subj_errors)
        confidence = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "auxiliary_errors": all_aux_errors,
            "clitic_errors": all_clitic_errors,
            "subjunctive_errors": all_subj_errors,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(confidence, 3)
        }
