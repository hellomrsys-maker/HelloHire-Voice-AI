"""
End-to-End Multi-Layer Grammar Checker Pipeline.
Orchestrates tokenization, POS tagging, lemmatization, dependency parsing,
and declarative rule validation to produce unified diagnostic feedback and suggested corrections.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.skills.pos_tagging import EnglishPOSTagger
from English_engine.brain.skills.lemmatization import EnglishLemmatizer
from English_engine.brain.skills.parsing import EnglishParser
from English_engine.brain.rules.rules_engine import RulesEngine, RuleViolation, RegisterProfile


@dataclass
class GrammarCheckResult:
    original_text: str
    corrected_text: str
    total_issues: int
    grammar_score: float  # 0 to 100
    violations: List[RuleViolation] = field(default_factory=list)
    register: Optional[RegisterProfile] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)


class GrammarCheckerPipeline:
    """
    Unified grammar and editorial validation pipeline.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()
        self.pos_tagger = EnglishPOSTagger()
        self.lemmatizer = EnglishLemmatizer()
        self.parser = EnglishParser()
        self.rules_engine = RulesEngine()

    def check(self, text: str) -> GrammarCheckResult:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)
        violations = self.rules_engine.check_text(text)
        reg = self.rules_engine.detect_register(text)

        # Apply corrections
        corrected = text
        # Sort violations in reverse order of start_char to replace without index invalidation
        replaceable_violations = [v for v in violations if v.suggested_replacement is not None]
        replaceable_violations.sort(key=lambda v: v.start_char, reverse=True)

        for v in replaceable_violations:
            corrected = (
                corrected[: v.start_char]
                + v.suggested_replacement
                + corrected[v.end_char :]
            )

        # Compute composite grammar score (penalizing for errors)
        error_count = sum(1 for v in violations if v.severity == "error")
        warning_count = sum(1 for v in violations if v.severity in {"warning", "info"})

        penalty = (error_count * 15.0) + (warning_count * 5.0)
        score = max(0.0, min(100.0, 100.0 - penalty))

        return GrammarCheckResult(
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
                "sentence_count": len(self.tokenizer.split_sentences(text)),
            },
        )
