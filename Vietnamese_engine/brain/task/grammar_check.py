"""
Vietnamese Grammar Checking Task Pipeline
Multi-layer linguistic proofreader auditing SVO order, numeral classifier concord,
preverbal TAM particle logic, tone diacritics, and politeness particles.
"""

from typing import Dict, Any, List
from Vietnamese_engine.brain.skills.tokenization import VietnameseTokenizer
from Vietnamese_engine.brain.skills.pos_tagging import VietnamesePOSTagger
from Vietnamese_engine.brain.skills.tone_engine import VietnameseToneEngine
from Vietnamese_engine.brain.analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer
from Vietnamese_engine.brain.analysis.tam_concord_analyzer import TAMConcordAnalyzer
from Vietnamese_engine.brain.analysis.kinship_deference_analyzer import KinshipDeferenceAnalyzer

class VietnameseGrammarChecker:
    """
    Unified linguistic proofreading engine for Vietnamese.
    """

    def __init__(self):
        self.tokenizer = VietnameseTokenizer()
        self.tagger = VietnamesePOSTagger()
        self.tone_engine = VietnameseToneEngine()
        self.clf_analyzer = ClassifierConcordAnalyzer()
        self.tam_analyzer = TAMConcordAnalyzer()
        self.kinship_analyzer = KinshipDeferenceAnalyzer()

    def check_text(self, text: str, speaker_term: Optional[str] = None, listener_term: Optional[str] = None) -> Dict[str, Any]:
        """Runs end-to-end multi-layer audit on input Vietnamese text."""
        norm_text = self.tokenizer.normalize_text(text)
        words = self.tokenizer.tokenize_words(norm_text)
        tagged = self.tagger.tag_sentence(norm_text)
        
        # 1. Tone analysis
        tones = self.tone_engine.analyze_text_tones(norm_text)
        
        # 2. Classifier Concord
        clf_res = self.clf_analyzer.audit_classifier_usage(norm_text)
        
        # 3. TAM sequencing
        tam_res = self.tam_analyzer.audit_tam_particles(norm_text)
        
        # 4. Kinship / Deference
        kin_res = self.kinship_analyzer.audit_dialogue_deixis(norm_text, speaker_term, listener_term)
        
        # Aggregate issues
        all_issues = clf_res["issues"] + tam_res["issues"]
        if not kin_res["is_valid"] and (speaker_term or listener_term):
            all_issues.append({
                "type": "kinship_deference_issue",
                "message": "Kinship address symmetry or politeness particle requirement violated."
            })
            
        penalty = len(all_issues) * 0.15
        confidence = max(0.0, round(1.0 - penalty, 2))
        
        return {
            "text": text,
            "normalized": norm_text,
            "total_words": len(words),
            "tones": tones,
            "classifier_analysis": clf_res,
            "tam_analysis": tam_res,
            "kinship_analysis": kin_res,
            "total_issues": len(all_issues),
            "issues": all_issues,
            "confidence_score": confidence,
            "is_valid": len(all_issues) == 0
        }
