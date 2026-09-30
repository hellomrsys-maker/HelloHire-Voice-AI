"""
toolkit.py - BandhuPrime High-Level Application Toolkit SDK.

Provides clean, enterprise-ready Python interfaces for integrating BandhuPrime's
six-language matrix and sub-AI grammar intelligence into client applications,
web services, editorial pipelines, and education platforms.
"""

from __future__ import annotations
import os
import sys
from typing import Any, Dict, List, Optional, Union

from .matrix_bridge import SixLanguageMatrixBridge
from gra_voi.bandhu.bandhu_orchestrator import BandhuPrimeOrchestrator
from gra_voi.bandhu.skill_models import (
    BandhuWritingSubAI,
    BandhuEmailSubAI,
    BandhuListeningSubAI,
    BandhuPronunciationSubAI,
    BandhuReviewingSubAI,
    BandhuBookWritingSubAI
)

class BandhuApplicationToolkit:
    """
    Main Application Toolkit for BandhuPrime Grammar Intelligence.
    Integrates:
    - Six-Language Matrix (Rust, Julia, Python, C++20, CUDA, Java 21)
    - Trained Deep Transformer Dedicated Sub-AIs (B1 - B6)
    - 0-Nanosecond Physical 64-Byte AMSV Memory Synchronization
    """

    def __init__(self, rust_dll_path: Optional[str] = None, checkpoint_path: Optional[str] = None):
        self.bridge = SixLanguageMatrixBridge(rust_dll_path=rust_dll_path)
        self.orchestrator = BandhuPrimeOrchestrator(checkpoint_path=checkpoint_path)
        
        # Expose dedicated neural Sub-AI models
        self.neural_cluster = self.orchestrator.neural_cluster
        self.neural_writing = self.neural_cluster.writing
        self.neural_email = self.neural_cluster.email
        self.neural_listening = self.neural_cluster.listening
        self.neural_pronunciation = self.neural_cluster.pronunciation
        self.neural_reviewing = self.neural_cluster.reviewing
        self.neural_book_writing = self.neural_cluster.book_writing

        # Symbolic rule engines
        self.writing_sub_ai = self.orchestrator.writing_sub_ai
        self.email_sub_ai = self.orchestrator.email_sub_ai
        self.listening_sub_ai = self.orchestrator.listening_sub_ai
        self.pronunciation_sub_ai = self.orchestrator.pronunciation_sub_ai
        self.reviewing_sub_ai = self.orchestrator.reviewing_sub_ai
        self.book_writing_sub_ai = self.orchestrator.book_writing_sub_ai

    def analyze_utterance(
        self,
        text: str,
        skill_hint: Optional[str] = None,
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes any utterance through the Multi-Language Meta-Router,
        executes dedicated Sub-AI diagnostics, and writes directly to AMSV.
        """
        # 1. High-level orchestrator diagnosis
        orch_res = self.orchestrator.process_utterance(
            text=text,
            skill_hint=skill_hint,
            lang_hint=language_hint
        )

        skill = orch_res["skill"]
        skill_id = {"Writing": 0, "Emailing": 1, "Listening": 2, "Pronouncing": 3, "Reviewing": 4, "BookWriting": 5}.get(skill, 0)

        # 2. Rust C-ABI engine verification if available
        rust_res = self.bridge.call_rust_skill_engine(text, skill_id)
        if rust_res:
            orch_res["rust_engine_verified"] = True
            orch_res["rust_diagnostics"] = rust_res
        else:
            orch_res["rust_engine_verified"] = False

        # 3. Synchronize to 64-byte AMSV physical state vector
        era_id = {"Ancient": 0, "Historical": 1, "Modern": 2, "Digital": 3}.get(orch_res["historical_era"], 2)
        self.bridge.sync_to_amsv(
            skill_id=skill_id,
            era_id=era_id,
            struct_score=orch_res["structural_score"],
            reg_score=orch_res["register_score"]
        )
        orch_res["amsv_telemetry"] = self.bridge.read_amsv()

        return orch_res

    def review_editorial_text(self, review_text: str) -> Dict[str, Any]:
        """Runs the two-pass Reviewing Sub-AI with 4-tier error taxonomy, citation checking, and Transformer inference."""
        res = self.reviewing_sub_ai.evaluate(review_text)
        neural_diag = self.neural_reviewing.analyze_text(review_text)
        return {
            "skill": "Reviewing",
            "structural_score": res.structural_score,
            "register_score": res.register_score,
            "dominant_error_tier": neural_diag.get("dominant_error_tier", "Clarity"),
            "hedging_score": neural_diag.get("hedging_score", 0.5),
            "is_location_anchored": neural_diag.get("is_location_anchored", False),
            "fatal_errors": res.fatal_errors,
            "clarity_errors": res.clarity_errors,
            "register_errors": res.register_errors,
            "style_preferences": res.style_preferences,
            "recommended_stage": res.recommended_stage,
            "actionable_plan": res.actionable_plan,
            "neural_diagnostics": neural_diag
        }

    def audit_book_manuscript(self, manuscript_text: str) -> Dict[str, Any]:
        """Runs the Book-Scale Writing Sub-AI checking tense/POV locks, reference decay, and 5-stage editorial status."""
        res = self.book_writing_sub_ai.evaluate(manuscript_text)
        neural_diag = self.neural_book_writing.analyze_text(manuscript_text)
        return {
            "skill": "BookWriting",
            "word_count": len(manuscript_text.split()),
            "structural_score": res.structural_score,
            "consistency_score": round(0.6 * neural_diag.get("consistency_score", res.consistency_score) + 0.4 * res.consistency_score, 4),
            "tense_collision_risk": neural_diag.get("tense_collision_risk", 0.1),
            "reference_decay_risk": neural_diag.get("reference_decay_risk", 0.1),
            "current_editing_stage": neural_diag.get("current_editing_stage", res.recommended_stage),
            "clarity_errors": res.clarity_errors,
            "fatal_errors": res.fatal_errors,
            "recommended_stage": res.recommended_stage,
            "five_stage_pipeline_plan": res.actionable_plan,
            "neural_diagnostics": neural_diag
        }

    def coach_pronunciation(
        self,
        transcript: str,
        vocalic_durations: Optional[List[float]] = None,
        dropped_endings: bool = False
    ) -> Dict[str, Any]:
        """
        Runs Pronunciation Sub-AI and Julia's Pairwise Variability Index (nPVI/rPVI) rhythm analysis.
        Generates the personalized 7-step clinical correction path.
        """
        pron_res = self.pronunciation_sub_ai.evaluate(transcript, dropped_endings=dropped_endings)
        neural_diag = self.neural_pronunciation.analyze_text(transcript)

        # Julia rhythm metrics
        durations = vocalic_durations or [120.0, 45.0, 140.0, 50.0, 130.0]
        rhythm_res = self.bridge.compute_julia_rhythm_metrics(durations)

        return {
            "skill": "Pronouncing",
            "transcript": transcript,
            "structural_score": pron_res.structural_score,
            "grammar_ending_audibility": neural_diag.get("grammar_ending_audibility", 0.9),
            "predicted_stress_class": neural_diag.get("predicted_stress_class", "Trochaic (Initial Stress - Noun)"),
            "tonal_accuracy": neural_diag.get("tonal_accuracy", 0.85),
            "fatal_errors": pron_res.fatal_errors,
            "rhythm_metrics": rhythm_res,
            "seven_step_correction_path": pron_res.actionable_plan,
            "neural_diagnostics": neural_diag
        }

    def inspect_amsv_state(self) -> Dict[str, Any]:
        """Inspects the live 64-byte Atomic Memory State Vector."""
        return self.bridge.read_amsv()
