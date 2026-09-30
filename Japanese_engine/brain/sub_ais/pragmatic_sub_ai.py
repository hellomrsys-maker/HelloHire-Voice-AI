"""
Japanese Pragmatic Sub-AI Module
================================
Dedicated artificial intelligence for communicative intent, speech acts,
Sasshi indirectness, Uchi/Soto honorific alignment, and register formality.
Synchronously maps to physical memory addresses in AMSV (offsets 0x20, 0x36).
"""

from __future__ import annotations
import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Japanese_engine.brain.Analysis.intent_mapper import JapaneseIntentMapper, JapaneseIntentReport, JapaneseSpeechAct
from Japanese_engine.brain.Analysis.presupposition_check import JapanesePresuppositionChecker, JapanesePresuppositionReport
from Japanese_engine.brain.rules.rules_engine import JapaneseRulesEngine, JapaneseRegisterProfile


@dataclass
class JapanesePragmaticEvaluation:
    utterance: str
    intent_report: JapaneseIntentReport
    presuppositions: JapanesePresuppositionReport
    register: JapaneseRegisterProfile
    pragmatic_felicity_score: float
    is_indirect_sasshi: bool
    amsv_synced: bool


class JapanesePragmaticSubAI:
    """
    Pragmatic Sub-AI managing contextual felicity, indirect speech acts, and conversational honorifics.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None) -> None:
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.intent_mapper = JapaneseIntentMapper()
        self.presupposition_checker = JapanesePresuppositionChecker()
        self.rules_engine = JapaneseRulesEngine()

    def evaluate(self, utterance: str) -> JapanesePragmaticEvaluation:
        intent = self.intent_mapper.map_intent(utterance)
        presupp = self.presupposition_checker.check(utterance)
        reg = self.rules_engine.detect_register(utterance)

        # Pragmatic felicity calculation
        base_score = intent.primary_speech_act.confidence
        if reg.confidence > 0.7:
            base_score = (base_score + reg.formality_score) / 2.0
        pragmatic_score = round(max(0.0, min(1.0, base_score)), 4)

        # ZERO-BRIDGE SYNCHRONOUS MEMORY WRITE
        # Writes directly into AMSV memory offsets
        self.amsv.set_global_register_score(reg.formality_score)
        self.amsv.set_cognitive_score(2, pragmatic_score)  # Capability 2: Pragmatics/Discourse

        # Pack scenario state into offset 0x20
        scenario_packed = (hash(intent.primary_speech_act.illocutionary_force) & 0xFFFFFFFF) | (int(pragmatic_score * 65535) << 32)
        self.amsv.set_scenario_state(scenario_packed)

        return JapanesePragmaticEvaluation(
            utterance=utterance,
            intent_report=intent,
            presuppositions=presupp,
            register=reg,
            pragmatic_felicity_score=pragmatic_score,
            is_indirect_sasshi=intent.primary_speech_act.is_indirect_sasshi,
            amsv_synced=True,
        )
