"""
Mandarin Grammar & Collocation Checker Task Pipeline.
Validates disposal (把) constructions, passive (被) syntax, and classifier agreement.
"""

from typing import Dict, Any, List
from ..skills.tokenization import MandarinTokenizer
from ..skills.pos_tagging import MandarinPOSTagger
from ..skills.parsing import MandarinParser
from ..skills.classifier_engine import ClassifierEngine


class MandarinGrammarChecker:
    """
    Automated proofreader and syntactic checker for Mandarin Chinese.
    """

    def __init__(self):
        self.tokenizer = MandarinTokenizer()
        self.tagger = MandarinPOSTagger()
        self.parser = MandarinParser()
        self.clf_engine = ClassifierEngine()

    def check_text(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.segment(text)
        tagged = self.tagger.tag(tokens)
        parsed = self.parser.parse(tagged)

        errors: List[str] = []
        warnings: List[str] = []

        # Check 把 construction
        if parsed.is_ba_construction and not parsed.ba_disposed_object:
            errors.append("把-construction missing disposed object.")

        # Check Classifier + Noun agreement
        for i in range(len(tokens) - 1):
            if tagged[i][1] == "M" and tagged[i + 1][1] == "NN":
                clf = tokens[i]
                noun = tokens[i + 1]
                verif = self.clf_engine.verify_collocation(clf, noun)
                if not verif["is_valid"]:
                    warnings.append(
                        f"Potential classifier mismatch: '{clf}' with '{noun}'. Recommended: {verif['recommended_classifiers']}."
                    )

        return {
            "input_text": text,
            "is_grammatically_sound": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings,
            "is_ba": parsed.is_ba_construction,
            "is_bei": parsed.is_bei_construction,
        }
