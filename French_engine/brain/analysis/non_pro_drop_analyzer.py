"""
French Non-Pro-Drop Cognitive Analyzer.
Verifies the obligatory presence of overt subject arguments in finite French clauses
and identifies expletive/dummy pronouns (il, ce, c').
"""

from typing import Dict, Any, List, Tuple
from ..skills.tokenization import FrenchTokenizer
from ..skills.pos_tagging import FrenchPOSTagger
from ..skills.parsing import FrenchParser, FrenchSentenceStructure


class NonProDropAnalyzer:
    """
    Cognitive diagnostic module enforcing the non-pro-drop parameter of Gallo-Romance syntax.
    """

    def __init__(self):
        self.tokenizer = FrenchTokenizer()
        self.tagger = FrenchPOSTagger()
        self.parser = FrenchParser()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed: FrenchSentenceStructure = self.parser.parse(tagged)

        is_valid_subject = parsed.has_overt_subject or parsed.is_imperative

        return {
            "text": text,
            "has_overt_subject": parsed.has_overt_subject,
            "subject_token": parsed.subject_token,
            "is_expletive": parsed.is_expletive_subject,
            "is_imperative": parsed.is_imperative,
            "conforms_to_non_pro_drop": is_valid_subject,
            "message": (
                "Sujet manifeste détecté (conforme au paramètre non-pro-drop)."
                if parsed.has_overt_subject
                else (
                    "Phrase impérative (sujet sous-entendu légitime)."
                    if parsed.is_imperative
                    else "Violation du paramètre non-pro-drop: le français exige un sujet explicite !"
                )
            )
        }
