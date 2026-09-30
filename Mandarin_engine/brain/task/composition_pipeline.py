"""
Mandarin Composition and Text Generation Task Pipeline.
"""

from typing import Dict, Any, Optional
from ..skills.tokenization import MandarinTokenizer
from ..skills.chengyu_engine import ChengyuEngine
from ..skills.generation import MandarinGenerator


class MandarinCompositionPipeline:
    """
    End-to-end writing and composition pipeline for Chinese prose and narrative generation.
    """

    def __init__(self):
        self.tokenizer = MandarinTokenizer()
        self.chengyu_engine = ChengyuEngine()
        self.generator = MandarinGenerator()

    def compose_statement(
        self,
        subject: str,
        verb: str,
        obj: str,
        aspect: Optional[str] = None,
        is_ba: bool = False,
        chengyu_focus: Optional[str] = None,
        polite: bool = False
    ) -> Dict[str, Any]:
        sentence = self.generator.generate(
            subject=subject,
            verb=verb,
            obj=obj,
            aspect=aspect,
            is_ba=is_ba,
            polite=polite
        )

        if chengyu_focus and chengyu_focus in self.chengyu_engine.chengyu_data:
            sentence = f"{sentence[:-1]}，可谓是{chengyu_focus}。"

        tokens = self.tokenizer.segment(sentence)
        density = self.chengyu_engine.evaluate_density(sentence)

        return {
            "composed_text": sentence,
            "tokens": tokens,
            "aspect_applied": aspect,
            "stylistic_level": density["stylistic_level"],
            "detected_chengyu": density["detected_idioms"],
        }
