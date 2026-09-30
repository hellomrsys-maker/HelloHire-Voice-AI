"""Turkish Grammar Check Pipeline.

Multi-pass cognitive grammar and harmony checker combining
vowel harmony auditing, consonant mutation checks,
and case-postposition government validation.
"""

from typing import Dict, Any, List
from ..skills.tokenization import TurkishTokenizer
from ..skills.pos_tagging import TurkishPOSTagger
from ..skills.vowel_harmony_engine import TurkishVowelHarmonyEngine
from ..skills.case_engine import TurkishCaseEngine
from ..analysis.vowel_harmony_analyzer import TurkishVowelHarmonyAnalyzer
from ..analysis.case_postposition_analyzer import TurkishCasePostpositionAnalyzer
from ..analysis.evidentiality_analyzer import TurkishEvidentialityAnalyzer


class TurkishGrammarChecker:
    def __init__(self):
        self.tokenizer = TurkishTokenizer()
        self.pos_tagger = TurkishPOSTagger()
        self.harmony = TurkishVowelHarmonyEngine()
        self.case_engine = TurkishCaseEngine(self.harmony)

        self.harmony_analyzer = TurkishVowelHarmonyAnalyzer(self.tokenizer, self.harmony)
        self.case_analyzer = TurkishCasePostpositionAnalyzer(self.tokenizer, self.pos_tagger, self.harmony)
        self.evidential_analyzer = TurkishEvidentialityAnalyzer(self.tokenizer, self.pos_tagger)

    def check(self, text: str) -> Dict[str, Any]:
        """Performs comprehensive grammatical and harmonic inspection."""
        harm_res = self.harmony_analyzer.analyze(text)
        case_res = self.case_analyzer.analyze(text)
        evid_res = self.evidential_analyzer.analyze(text)

        all_issues = []
        all_issues.extend(harm_res.get("violations", []))
        all_issues.extend(case_res.get("issues", []))

        base_score = 100
        for issue in all_issues:
            sev = issue.get("severity", "warning")
            deduction = 15 if sev == "error" else 5
            base_score = max(0, base_score - deduction)

        is_clean = len(all_issues) == 0

        return {
            "text": text,
            "is_clean": is_clean,
            "quality_score": base_score,
            "issues_count": len(all_issues),
            "issues": all_issues,
            "vowel_harmony_analysis": harm_res,
            "case_analysis": case_res,
            "evidentiality_analysis": evid_res
        }
