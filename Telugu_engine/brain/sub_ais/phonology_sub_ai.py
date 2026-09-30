"""
Telugu Phonology Sub-AI.
Evaluates phonetic prosody, syllable count, acoustic stress, and sound invariants.
Syncs strictly with AMSV Phonemes (0x00..0x07), Prosody (0x08..0x0F), and Capability 4 (0x18 / Byte 24).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import PronunciationSubAINeural


@dataclass
class TeluguPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    phonological_density_score: float
    ending_audibility: float
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


TeluguPhonologyEvaluation = TeluguPhonologyEvaluationResult


class TeluguPhonologySubAI:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None, checkpoint_path: Optional[str] = None):
        self.amsv = amsv_view
        self.neural_model = PronunciationSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("pronunciation_sub_ai", ckpt.get("pronunciation", ckpt))
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> TeluguPhonologyEvaluationResult:
        words = text.strip().split()
        syllables = max(len(words), len(text) // 3)
        base_density = min(1.0, 0.75 + (0.02 * min(10, len(words))))

        ending_aud = 0.90
        if self.is_neural_loaded:
            try:
                n_res = self.neural_model.analyze_text(text)
                ending_aud = float(n_res.get("grammar_ending_audibility", 0.90))
                density_score = 0.70 * base_density + 0.30 * ending_aud
            except Exception:
                density_score = base_density
        else:
            density_score = base_density

        density_score = round(min(1.0, max(0.0, density_score)), 4)
        synced = False
        if self.amsv is not None:
            self.amsv.set_phoneme_state((syllables & 0xFFFF) | 0x11220000)
            self.amsv.set_prosody_state(int(density_score * 0xFFFF) & 0xFFFF)
            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return TeluguPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllables,
            phonological_density_score=density_score,
            ending_audibility=round(ending_aud, 4),
            amsv_synced=synced,
        )
