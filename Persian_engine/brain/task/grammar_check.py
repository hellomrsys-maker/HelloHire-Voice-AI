"""
Persian Grammar Checking Task Pipeline
Multi-layer linguistic proofreader auditing SOV word order, Ezafe realization,
DOM 'rā' placement, verbal agreement, and orthography.
"""

from typing import Dict, Any, List
from Persian_engine.brain.skills.tokenization import PersianTokenizer
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger
from Persian_engine.brain.analysis.ezafe_attachment_analyzer import EzafeAttachmentAnalyzer
from Persian_engine.brain.analysis.dom_concord_analyzer import DOMConcordAnalyzer
from Persian_engine.brain.analysis.taarof_deference_analyzer import TaarofDeferenceAnalyzer

class PersianGrammarChecker:
    """
    Unified proofreading engine for Persian text.
    """

    def __init__(self):
        self.tokenizer = PersianTokenizer()
        self.tagger = PersianPOSTagger()
        self.ezafe_analyzer = EzafeAttachmentAnalyzer()
        self.dom_analyzer = DOMConcordAnalyzer()
        self.deference_analyzer = TaarofDeferenceAnalyzer()

    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-layer audit on input Persian text.
        """
        normalized = self.tokenizer.normalize_script(text)
        tokens = self.tokenizer.tokenize_words(normalized)
        tagged = self.tagger.tag_sentence(normalized)
        
        # 1. Word Order / Head-Final predicate check
        sov_valid = True
        sov_issues = []
        if tagged:
            last_word, last_pos = tagged[-1]
            if last_pos == "PUNCT" and len(tagged) > 1:
                last_word, last_pos = tagged[-2]
            # In canonical Persian, the finite verb is clause-final
            has_verb = any(pos == "VERB" for _, pos in tagged)
            if has_verb and last_pos not in {"VERB", "AUX"}:
                # Verb is not head-final
                sov_valid = False
                sov_issues.append({
                    "type": "non_head_final_verb",
                    "message": f"Canonical Persian is SOV; expected finite verb at sentence end, found '{last_word}' ({last_pos})."
                })

        # 2. Ezafe Analysis
        ezafe_res = self.ezafe_analyzer.analyze_ezafe_chains(normalized)
        
        # 3. DOM 'rā' Analysis
        dom_res = self.dom_analyzer.audit_sentence_dom(normalized)
        
        # 4. Deference and Colloquial Analysis
        def_res = self.deference_analyzer.audit_deference_and_register(normalized, target_register="formal")
        
        # Aggregate all issues
        all_issues = sov_issues + ezafe_res["issues"] + dom_res["issues"] + [
            {"type": "colloquial_leak", "message": item["message"]}
            for item in def_res["colloquial_findings"]
        ]
        
        # Compute overall grammatical confidence score (0.0 .. 1.0)
        penalty = len(all_issues) * 0.15
        confidence = max(0.0, round(1.0 - penalty, 2))
        
        return {
            "text": text,
            "normalized": normalized,
            "total_tokens": len(tokens),
            "sov_valid": sov_valid,
            "ezafe_analysis": ezafe_res,
            "dom_analysis": dom_res,
            "deference_analysis": def_res,
            "total_issues": len(all_issues),
            "issues": all_issues,
            "confidence_score": confidence,
            "is_valid": len(all_issues) == 0
        }
