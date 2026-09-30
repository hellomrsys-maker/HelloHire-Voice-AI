"""
Spanish Pro-Drop Cognitive Analyzer.
Analyzes null-subject phenomena, overt pronoun emphasis, and topical discourse grounding.
"""

from typing import Dict, Any, List
from ..skills.tokenization import SpanishTokenizer
from ..skills.pos_tagging import SpanishPOSTagger
from ..skills.parsing import SpanishParser


class ProDropAnalyzer:
    """
    Evaluates informational packaging, subject omission, and pragmatic focus.
    """

    def __init__(self):
        self.tokenizer = SpanishTokenizer()
        self.tagger = SpanishPOSTagger()
        self.parser = SpanishParser()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.segment(text)
        tagged = self.tagger.tag(tokens)
        parsed = self.parser.parse(tagged)

        # Contrastive / emphatic indicators (pero yo, mientras tú, él en cambio)
        is_contrastive = any(w in text.lower() for w in ["pero yo", "mientras tú", "en cambio", "por mi parte"])

        style = "Natural Pro-Drop (Castilian / Pan-Hispanic)"
        if parsed.has_overt_subject and not is_contrastive:
            style = "Overt Subject (Emphatic or Caribbean / Contact Tendency)"
        elif parsed.has_overt_subject and is_contrastive:
            style = "Overt Contrastive Focus"

        return {
            "is_pro_drop": parsed.is_pro_drop,
            "has_overt_subject": parsed.has_overt_subject,
            "overt_subject": parsed.overt_subject,
            "is_contrastive": is_contrastive,
            "discourse_style": style,
        }
