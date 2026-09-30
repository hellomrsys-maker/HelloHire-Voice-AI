"""
German Engine — Grammar Check Task Pipeline
Conducts end-to-end linguistic audit of German text:
- Substantive capitalization (Großschreibung)
- Preposition case government (Akk, Dat, Gen)
- Adjective declension concord (strong, weak, mixed)
- Topological field (Satzklammer) V2/V-End structure
- Register consistency (Duzen vs Siezen)
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words, split_sentences
from ..skills.pos_tagging import tag_pos
from ..skills.pragmatics_engine import validate_substantive_capitalization, analyze_register
from ..analysis.satzklammer_analyzer import SatzklammerAnalyzer
from ..analysis.case_government_analyzer import CaseGovernmentAnalyzer
from ..analysis.adjective_agreement_analyzer import AdjectiveAgreementAnalyzer

class GermanGrammarChecker:
    """End-to-end task pipeline for comprehensive German grammar validation."""

    def __init__(self):
        self.satzklammer = SatzklammerAnalyzer()
        self.case_gov = CaseGovernmentAnalyzer()
        self.adj_agree = AdjectiveAgreementAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        total_tokens = 0
        all_capitalization_issues = []
        all_case_issues = []
        all_adj_issues = []
        all_syntax_issues = []
        
        full_tokens = tokenize_words(text)
        full_tags = tag_pos(full_tokens)
        reg_info = analyze_register(text, full_tokens)
        
        # Substantive capitalization audit
        cap_violations = validate_substantive_capitalization(full_tokens, full_tags)
        all_capitalization_issues.extend(cap_violations)
        
        for s in sentences:
            s_tokens = tokenize_words(s)
            total_tokens += len(s_tokens)
            
            # Satzklammer check
            sk_res = self.satzklammer.analyze(s)
            if not sk_res["is_valid"]:
                all_syntax_issues.extend(sk_res["errors"])
                
            # Case government check
            cg_res = self.case_gov.analyze(s)
            if not cg_res["is_valid"]:
                all_case_issues.extend(cg_res["violations"])
                
            # Adjective agreement check
            aa_res = self.adj_agree.analyze(s)
            if not aa_res["is_valid"]:
                all_adj_issues.extend(aa_res["violations"])
                
        total_errors = (
            len(all_capitalization_issues) +
            len(all_case_issues) +
            len(all_adj_issues) +
            len(all_syntax_issues) +
            (1 if not reg_info["is_consistent"] else 0)
        )
        
        score = max(0.0, 1.0 - (total_errors * 0.15))
        
        return {
            "text": text,
            "sentence_count": len(sentences),
            "token_count": total_tokens,
            "register": reg_info["register"],
            "register_consistent": reg_info["is_consistent"],
            "capitalization_issues": all_capitalization_issues,
            "case_government_issues": all_case_issues,
            "adjective_agreement_issues": all_adj_issues,
            "syntax_issues": all_syntax_issues,
            "total_errors": total_errors,
            "passed": total_errors == 0,
            "confidence_score": round(score, 3)
        }
