"""
French Grammar Checker Task Pipeline.
Integrates elision verification, subject overtness (non-pro-drop), bipartite negation,
and register consistency checks into a unified proofreading suite.
"""

from typing import Dict, Any, List
from ..skills.tokenization import FrenchTokenizer
from ..skills.pos_tagging import FrenchPOSTagger
from ..skills.parsing import FrenchParser, FrenchSentenceStructure
from ..skills.liaison_elision_engine import LiaisonElisionEngine
from ..skills.pragmatics_engine import FrenchPragmaticsEngine


class FrenchGrammarChecker:
    """
    Grammar checker and proofreading pipeline for French text.
    """

    def __init__(self):
        self.tokenizer = FrenchTokenizer()
        self.tagger = FrenchPOSTagger()
        self.parser = FrenchParser()
        self.elision_engine = LiaisonElisionEngine()
        self.pragmatics = FrenchPragmaticsEngine()

    def check(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed: FrenchSentenceStructure = self.parser.parse(tagged)
        prag = self.pragmatics.evaluate_register(text)

        issues: List[Dict[str, Any]] = []

        # 1. Non-pro-drop check
        if not parsed.has_overt_subject and not parsed.is_imperative:
            issues.append({
                "type": "missing_subject",
                "severity": "error",
                "message": "Le français exige un sujet explicite (pronom ou nom)."
            })

        # 2. Elision check across consecutive tokens
        for i in range(len(tokens) - 1):
            el_res = self.elision_engine.evaluate_elision(tokens[i], tokens[i + 1])
            if not el_res["is_valid"]:
                issues.append({
                    "type": el_res["error_type"],
                    "severity": "error",
                    "message": el_res["message"],
                    "position": (tokens[i], tokens[i + 1]),
                    "recommended": el_res.get("recommended")
                })

        # 3. Register clash check
        if prag["has_register_clash"]:
            issues.append({
                "type": "register_clash",
                "severity": "warning",
                "message": "Mélange incohérent de tutoiement et vouvoiement."
            })

        # Calculate score
        base_score = 1.0
        for iss in issues:
            if iss["severity"] == "error":
                base_score -= 0.25
            else:
                base_score -= 0.10
        score = max(0.0, round(base_score, 2))

        return {
            "text": text,
            "is_valid": len(issues) == 0,
            "score": score,
            "issues_count": len(issues),
            "issues": issues,
            "register": prag["assigned_register"],
            "has_bipartite_negation": parsed.has_bipartite_negation,
            "has_subjunctive_trigger": parsed.has_subjunctive_trigger
        }
