"""
Japanese Grammar Checker Pipeline
=================================
End-to-end multi-layer grammar, keigo, orthography, and style checker.
Orchestrates morphological segmentation, POS tagging, bunsetsu parsing,
and declarative rule validation to produce unified diagnostic feedback and corrections.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.pos_tagging import JapanesePOSTagger
from Japanese_engine.brain.skills.parsing import JapaneseParser
from Japanese_engine.brain.skills.lemmatization import JapaneseLemmatizer
from Japanese_engine.brain.rules.rules_engine import (
    JapaneseRulesEngine,
    JapaneseRuleViolation,
    JapaneseRegisterProfile,
)


@dataclass
class JapaneseGrammarCheckResult:
    original_text: str
    corrected_text: str
    total_issues: int
    grammar_score: float  # 0 to 100
    violations: List[JapaneseRuleViolation] = field(default_factory=list)
    register: Optional[JapaneseRegisterProfile] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)


class JapaneseGrammarCheckerPipeline:
    """
    Unified Japanese grammar and style checking pipeline.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.pos_tagger = JapanesePOSTagger()
        self.lemmatizer = JapaneseLemmatizer()
        self.parser = JapaneseParser()
        self.rules_engine = JapaneseRulesEngine()

    def check(self, text: str) -> JapaneseGrammarCheckResult:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)
        violations = self.rules_engine.check_text(text)
        reg = self.rules_engine.detect_register(text)

        # Apply corrections
        corrected = text
        # Replace from right-to-left to preserve character indices
        replaceable = [v for v in violations if v.suggested_replacement is not None]
        replaceable.sort(key=lambda v: v.start_char, reverse=True)

        for v in replaceable:
            corrected = (
                corrected[: v.start_char]
                + (v.suggested_replacement or "")
                + corrected[v.end_char :]
            )

        error_count = sum(1 for v in violations if v.severity == "error")
        warning_count = sum(1 for v in violations if v.severity in {"warning", "info"})

        penalty = (error_count * 15.0) + (warning_count * 5.0)
        score = max(0.0, min(100.0, 100.0 - penalty))

        return JapaneseGrammarCheckResult(
            original_text=text,
            corrected_text=corrected,
            total_issues=len(violations),
            grammar_score=round(score, 1),
            violations=violations,
            register=reg,
            diagnostics={
                "error_count": error_count,
                "warning_count": warning_count,
                "token_count": len(tokens),
            },
        )
