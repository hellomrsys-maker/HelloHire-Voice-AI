"""Russian Grammar Check Pipeline.

Multi-pass cognitive grammar and style checker combining
case government validation, aspectual harmony inspection,
and numeral-noun paucal concord auditing.
"""

from typing import Dict, Any, List
from ..skills.tokenization import RussianTokenizer
from ..skills.pos_tagging import RussianPOSTagger
from ..skills.case_engine import RussianCaseEngine
from ..skills.verb_aspect_conjugator import RussianVerbAspectConjugator
from ..skills.numeral_concord_engine import RussianNumeralConcordEngine
from ..analysis.case_government_analyzer import RussianCaseGovernmentAnalyzer
from ..analysis.aspect_choice_analyzer import RussianAspectChoiceAnalyzer
from ..analysis.numeral_concord_analyzer import RussianNumeralConcordAnalyzer


class RussianGrammarChecker:
    def __init__(self):
        self.tokenizer = RussianTokenizer()
        self.pos_tagger = RussianPOSTagger()
        self.case_engine = RussianCaseEngine()
        self.verb_conjugator = RussianVerbAspectConjugator()
        self.numeral_engine = RussianNumeralConcordEngine(self.case_engine)

        self.case_analyzer = RussianCaseGovernmentAnalyzer(
            self.tokenizer, self.pos_tagger, self.case_engine
        )
        self.aspect_analyzer = RussianAspectChoiceAnalyzer(
            self.tokenizer, self.pos_tagger, self.verb_conjugator
        )
        self.numeral_analyzer = RussianNumeralConcordAnalyzer(
            self.tokenizer, self.pos_tagger, self.numeral_engine
        )

    def check(self, text: str) -> Dict[str, Any]:
        """Performs comprehensive grammatical and stylistic inspection."""
        case_res = self.case_analyzer.analyze(text)
        aspect_res = self.aspect_analyzer.analyze(text)
        numeral_res = self.numeral_analyzer.analyze(text)

        all_issues = []
        all_issues.extend(case_res.get("issues", []))
        all_issues.extend(aspect_res.get("issues", []))
        all_issues.extend(numeral_res.get("concord_issues", []))

        # Calculate overall quality score (0..100)
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
            "case_analysis": case_res,
            "aspect_analysis": aspect_res,
            "numeral_analysis": numeral_res
        }
