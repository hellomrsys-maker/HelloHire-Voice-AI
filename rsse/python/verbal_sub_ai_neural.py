"""
verbal_sub_ai_neural.py - Production-Grade Transformer Sub-AI for Recruitment Verbal Communication.

Implements deep bidirectional Transformer sequence modeling for candidate verbal responses:
- UniversalSubwordTokenizer: Native multilingual subword & jargon tokenization.
- Star Coherence Head: Evaluates narrative completeness across Situation, Task, Action, Result.
- Register Compliance Head: Evaluates formal executive articulation vs. colloquial drift.
- Professional Jargon Density Head: Measures domain-specific vocabulary presence.
- Candidate Confidence Head: Evaluates communicative certainty and assertiveness.
- Format Fit Classification Head: Matches response to 1 of 8 standardized interview formats.
"""

from __future__ import annotations
import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from gra_voi.bandhu.sub_ai_neural import UniversalSubwordTokenizer, TransformerSequenceEncoder


class RecruitmentVerbalSubAINeural(nn.Module):
    """
    Dedicated Neural Sub-AI Architecture for Recruitment Verbal Communication (RVCE).
    """

    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        # 1. STAR Coherence Head (Situation, Task, Action, Result completeness)
        self.star_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

        # 2. Register Compliance Head (Executive / Formal vs. Informal)
        self.register_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

        # 3. Professional Jargon Density Head
        self.jargon_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # 4. Candidate Confidence Head
        self.confidence_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # 5. Interview Format Fit Head (8 formats)
        self.format_head = nn.Linear(d_model, 8)

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        _, pooled = self.encoder(input_ids, attention_mask)
        return {
            "star_coherence": self.star_head(pooled),
            "register_compliance": self.register_head(pooled),
            "jargon_density": self.jargon_head(pooled),
            "candidate_confidence": self.confidence_head(pooled),
            "format_logits": self.format_head(pooled),
            "pooled_embedding": pooled
        }

    def analyze_verbal_response(
        self,
        transcript: str,
        format_code: int = 1,
        wpm: float = 135.0
    ) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(transcript, max_length=64)
            out = self.forward(input_ids, attention_mask)

            star = out["star_coherence"].item()
            reg = out["register_compliance"].item()
            jargon = out["jargon_density"].item()
            conf = out["candidate_confidence"].item()
            fmt_pred = out["format_logits"].argmax(dim=-1).item() + 1

            # Format weight modulation
            fmt_weight = 0.50 if format_code in (2, 3) else 0.35
            composite = (star * fmt_weight) + (reg * (1.0 - fmt_weight))

            format_names = {
                1: "Technical Interview",
                2: "Behavioral Interview (STAR)",
                3: "Competency-Based Interview",
                4: "Case Study / Business Case",
                5: "Group Discussion",
                6: "HR Screening",
                7: "Executive Leadership",
                8: "Multi-Examiner Panel"
            }

            feedback = []
            if star < 0.60 and format_code in (2, 3):
                feedback.append("STAR methodology incomplete: Action or quantifiable Result component missing.")
            if reg < 0.65:
                feedback.append("Colloquial phrasing detected; recommend elevating executive register.")
            if conf < 0.60:
                feedback.append("Excessive epistemic hedge qualifiers detected; project greater communicative certainty.")

            return {
                "skill": "RecruitmentVerbalCommunication",
                "format_evaluated": format_names.get(format_code, "General Interview"),
                "predicted_format_affinity": format_names.get(fmt_pred, "Technical Interview"),
                "format_fit": format_names.get(fmt_pred, "Technical Interview"),
                "star_coherence_score": round(star, 4),
                "star_coherence": round(star, 4),
                "register_compliance_score": round(reg, 4),
                "register_compliance": round(reg, 4),
                "jargon_density_score": round(jargon, 4),
                "jargon_density": round(jargon, 4),
                "candidate_confidence_score": round(conf, 4),
                "candidate_confidence": round(conf, 4),
                "composite_verbal_score": round(composite, 4),
                "composite_score": round(composite, 4),
                "passed_threshold": composite >= 0.70,
                "actionable_feedback": feedback
            }

