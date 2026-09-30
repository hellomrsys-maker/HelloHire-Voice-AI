"""
Hindustani Grammar Checker Task Pipeline.
Unified proofreading suite validating split-ergativity, oblique nominal case,
canonical SOV word order, and honorific agreement.
"""

from typing import Dict, Any, List
from ..skills.tokenization import HindustaniTokenizer
from ..skills.pos_tagging import HindustaniPOSTagger
from ..skills.parsing import HindustaniParser, HindustaniSentenceStructure
from ..analysis.oblique_concord_analyzer import ObliqueConcordAnalyzer
from ..analysis.honorific_agreement_analyzer import HonorificAgreementAnalyzer


class HindustaniGrammarChecker:
    """
    Grammar checker and proofreading pipeline for Hindustani text.
    """

    def __init__(self):
        self.tokenizer = HindustaniTokenizer()
        self.tagger = HindustaniPOSTagger()
        self.parser = HindustaniParser()
        self.oblique_analyzer = ObliqueConcordAnalyzer()
        self.honorific_analyzer = HonorificAgreementAnalyzer()

    def check(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed: HindustaniSentenceStructure = self.parser.parse(tagged)

        oblique_res = self.oblique_analyzer.analyze(text)
        hon_res = self.honorific_analyzer.analyze(text)

        issues: List[Dict[str, Any]] = []

        # 1. Oblique Case Check
        if not oblique_res["is_valid"]:
            for v in oblique_res["violations"]:
                issues.append({
                    "type": "oblique_case_error",
                    "severity": "error",
                    "message": v["message"],
                    "expected": v.get("expected")
                })

        # 2. Honorific Agreement Check
        if not hon_res["is_concord_valid"]:
            issues.append({
                "type": "honorific_mismatch",
                "severity": "error",
                "message": hon_res["message"]
            })

        # Calculate score
        score = 1.0
        for iss in issues:
            if iss["severity"] == "error":
                score -= 0.25
            else:
                score -= 0.10
        score = max(0.0, round(score, 2))

        return {
            "text": text,
            "is_valid": len(issues) == 0,
            "score": score,
            "issues_count": len(issues),
            "issues": issues,
            "is_canonical_sov": parsed.is_canonical_sov,
            "is_ergative_clause": parsed.is_ergative_subject,
            "postpositions_found": parsed.postpositions
        }
