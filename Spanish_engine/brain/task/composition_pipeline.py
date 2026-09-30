"""
Spanish Composition and Prose Generation Task Pipeline.
"""

from typing import Dict, Any, Optional
from ..skills.tokenization import SpanishTokenizer
from ..skills.generation import SpanishGenerator


class SpanishCompositionPipeline:
    """
    End-to-end composition pipeline for Spanish sentences and descriptive statements.
    """

    def __init__(self):
        self.tokenizer = SpanishTokenizer()
        self.generator = SpanishGenerator()

    def compose_statement(
        self,
        subject: str,
        verb_lemma: str,
        obj: str,
        tense: str = "presente_indicativo",
        pro_drop: bool = False,
        polite: bool = False,
        is_question: bool = False,
    ) -> Dict[str, Any]:
        sentence = self.generator.generate(
            subject=subject,
            verb_lemma=verb_lemma,
            obj=obj,
            tense=tense,
            pro_drop=pro_drop,
            polite=polite,
            is_question=is_question,
        )

        tokens = self.tokenizer.segment(sentence)

        return {
            "composed_text": sentence,
            "tokens": tokens,
            "token_count": len(tokens),
            "pro_drop_applied": pro_drop,
            "tense": tense,
        }
