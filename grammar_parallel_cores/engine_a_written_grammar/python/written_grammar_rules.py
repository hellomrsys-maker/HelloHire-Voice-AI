"""
written_grammar_rules.py - Engine A Sub-Core A2 (Python)
Written Grammar & Discourse Engine: Deep Transformer rules, clause completeness,
discourse coherence, and register classification.
"""

from __future__ import annotations
import os
import sys
import re
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from gra_voi.bandhu.sub_ai_neural import WritingSubAINeural, BookWritingSubAINeural, UniversalSubwordTokenizer


class WrittenGrammarRulesSubCore:
    """
    Python Sub-Core A2: Orchestrates deep neural writing rules and syntactic features.
    """

    def __init__(self, tokenizer: Optional[UniversalSubwordTokenizer] = None):
        self.tokenizer = tokenizer or UniversalSubwordTokenizer(vocab_size=4096)
        self.writing_model = WritingSubAINeural(vocab_size=4096, d_model=128)
        self.book_model = BookWritingSubAINeural(vocab_size=4096, d_model=128)
        self.writing_model.eval()
        self.book_model.eval()

    def evaluate_written_rules(self, text: str) -> Dict[str, Any]:
        """
        Executes rule evaluation and neural forward passes for written text.
        """
        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)
        
        # Rule 1: Clause segmentation and punctuation integrity
        clauses = [c.strip() for c in re.split(r'[.!?;]', text) if c.strip()]
        clause_count = max(1, len(clauses))
        avg_clause_length = sum(len(c.split()) for c in clauses) / clause_count

        # Rule 2: Subordinating / coordinating conjunctions
        subordinators = ["because", "although", "since", "whereas", "while", "if", "unless"]
        coordinators = ["and", "but", "or", "so", "yet", "for", "nor"]
        lower = text.lower()
        sub_count = sum(lower.count(f" {w} ") for w in subordinators)
        coord_count = sum(lower.count(f" {w} ") for w in coordinators)
        complex_ratio = min(1.0, (sub_count * 1.5 + coord_count) / max(1, clause_count))

        # Neural evaluation via analyze_text
        w_res = self.writing_model.analyze_text(text)
        b_res = self.book_model.analyze_text(text)

        clause_prob = 0.88 if len(w_res.get("clarity_errors", [])) == 0 else 0.55
        completeness_prob = float(w_res.get("completeness", 0.85)) if "completeness" in w_res else 0.85
        coherence_score = float(b_res.get("consistency_score", 0.80))

        composite_rule_score = round(
            0.35 * completeness_prob + 0.35 * clause_prob + 0.15 * complex_ratio + 0.15 * coherence_score,
            4
        )

        return {
            "sub_core": "A2_Python",
            "token_count": token_count,
            "clause_count": clause_count,
            "avg_clause_length": round(avg_clause_length, 2),
            "subordinating_count": sub_count,
            "coordinating_count": coord_count,
            "clause_completeness_prob": round(completeness_prob, 4),
            "discourse_coherence_score": round(coherence_score, 4),
            "syntactic_complexity_ratio": round(complex_ratio, 4),
            "written_rule_composite": composite_rule_score
        }
