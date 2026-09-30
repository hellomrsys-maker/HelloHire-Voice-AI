"""
English Pragmatic Sub-AI Module.
Dedicated artificial intelligence for communicative intent, speech acts,
presupposition verification, and conversational register alignment.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView.
Writes ONLY to designated sync offsets:
- Capability 3 (Pragmatics / Register Q16): Offset 0x16 (Byte 22)
- Global Register Score (Q16): Offset 0x36 (Byte 54)
"""

from __future__ import annotations
import os
import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from English_engine.brain.Analysis.intent_mapper import IntentMapper, SpeechActClassification
from English_engine.brain.Analysis.presupposition_check import PresuppositionChecker, PresuppositionReport
from English_engine.brain.rules.rules_engine import RulesEngine, RegisterProfile
from gra_voi.bandhu.sub_ai_neural import EmailSubAINeural


@dataclass
class PragmaticEvaluation:
    utterance: str
    speech_act: SpeechActClassification
    presuppositions: PresuppositionReport
    register: RegisterProfile
    pragmatic_score: float
    neural_politeness_index: float
    pragmatic_transfer_risk: float
    amsv_synced: bool


class EnglishPragmaticSubAI:
    """
    Pragmatic Sub-AI managing contextual felicity, speaker intent, politeness,
    and conversational register via rule-based and trained neural heads.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.intent_mapper = IntentMapper()
        self.presupposition_checker = PresuppositionChecker()
        self.rules_engine = RulesEngine()

        # Neural backbone: EmailSubAINeural (Politeness & Pragmatic Transfer)
        self.neural_model = EmailSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                if "email_sub_ai" in ckpt:
                    self.neural_model.load_state_dict(ckpt["email_sub_ai"])
                    self.is_neural_loaded = True
                elif "email" in ckpt:
                    self.neural_model.load_state_dict(ckpt["email"])
                    self.is_neural_loaded = True
            except Exception:
                pass
        self.neural_model.eval()

    def evaluate(self, utterance: str) -> PragmaticEvaluation:
        speech_act = self.intent_mapper.classify(utterance)
        presupp = self.presupposition_checker.analyze(utterance)
        reg = self.rules_engine.detect_register(utterance)

        # Neural analysis via EmailSubAINeural
        try:
            n_res = self.neural_model.analyze_text(utterance)
            politeness_idx = float(n_res.get("politeness_index", 0.85))
            transfer_risk = float(n_res.get("pragmatic_transfer_risk", 0.10))
            neural_reg_score = float(n_res.get("register_score", reg.formality_score))
        except Exception:
            politeness_idx = 0.85
            transfer_risk = 0.10
            neural_reg_score = reg.formality_score

        # Pragmatic felicity score
        base_score = 0.5 * speech_act.confidence + 0.5 * politeness_idx
        formality = 0.5 * reg.formality_score + 0.5 * neural_reg_score
        pragmatic_score = round(max(0.0, min(1.0, (base_score + formality) / 2.0)), 4)

        # ZERO-BRIDGE SYNCHRONOUS MEMORY WRITE
        # Writes strictly and exclusively to designated sync offsets:
        # 1. Capability 3 (Pragmatics / Register Q16): Offset 0x16 (Byte 22)
        self.amsv.set_cognitive_score(3, pragmatic_score)
        # 2. Global Register Score (Q16): Offset 0x36 (Byte 54)
        self.amsv.set_global_register_score(formality)

        return PragmaticEvaluation(
            utterance=utterance,
            speech_act=speech_act,
            presuppositions=presupp,
            register=reg,
            pragmatic_score=pragmatic_score,
            neural_politeness_index=round(politeness_idx, 4),
            pragmatic_transfer_risk=round(transfer_risk, 4),
            amsv_synced=True,
        )
