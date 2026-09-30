"""
base_orchestrator.py — Shared English-Parity Master Orchestrator.
=================================================================

``BaseEngineOrchestrator`` wires the COMPLETE English-flagship pipeline once:

  Stage A — English-Pivot Comprehension (every language understands English first)
  Stage B — 4 dedicated Sub-AIs (syntax, phonology, pragmatic, editorial) → AMSV
  Stage C — Six-Language Matrix coordination (Rust/C++/CUDA/Java/Julia/Python) → AMSV
  Stage D — Reusable Four-Stage Matrix Pattern (Stage 1..4 with feedback)
  Stage E — Composite scoring + 64-byte AMSV snapshot

Each concrete engine subclasses this and supplies only its ``LanguageProfile`` (and,
where a language already ships richer skills, may extend ``process`` to add them).
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from amsv.python.amsv_embedded import AMSVEmbeddedView
from .language_profile import LanguageProfile, get_profile
from .english_pivot import EnglishPivotComprehension, PivotComprehensionResult
from .pos_skill import NeuralPOSSkill
from .base_components import (
    SyntaxSubAI, PhonologySubAI, PragmaticSubAI, EditorialSubAI,
    BaseSixLanguageMatrixBridge, SubAIEvaluation,
)

try:
    from four_stage_matrix.four_stage_engine import FourStageMatrixEngine
    from four_stage_matrix.stage1_entry import RequirementContract
    _FOUR_STAGE_OK = True
except Exception:
    _FOUR_STAGE_OK = False
    FourStageMatrixEngine = None
    RequirementContract = None


@dataclass
class EngineComprehensiveOutput:
    input_text: str
    language: str
    iso_code: str
    english_pivot: PivotComprehensionResult
    syntax_sub_ai: SubAIEvaluation
    phonology_sub_ai: SubAIEvaluation
    pragmatic_sub_ai: SubAIEvaluation
    editorial_sub_ai: SubAIEvaluation
    six_language_matrix: Dict[str, Any]
    four_stage_matrix: Dict[str, Any]
    overall_linguistic_score: float
    amsv_bytes_hex: str
    amsv_synced: bool
    latency_ms: float
    pos_tags: List[Any] = field(default_factory=list)   # [(word, UD-POS), ...]
    pos_source: str = "none"                            # "neural" | "heuristic" | "none"
    notes: Dict[str, Any] = field(default_factory=dict)


class BaseEngineOrchestrator:
    """
    Master orchestrator shared by every language engine. Behaviourally identical in
    shape to the English flagship, parameterised by a ``LanguageProfile``, and wired to
    the English-pivot comprehension layer so every language understands English first.
    """

    #: Subclasses set this to their engine directory name, e.g. "Spanish_engine".
    ENGINE_DIR: str = ""

    def __init__(
        self,
        profile: Optional[LanguageProfile] = None,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ) -> None:
        if profile is None:
            if not self.ENGINE_DIR:
                raise ValueError("BaseEngineOrchestrator requires a profile or ENGINE_DIR.")
            profile = get_profile(self.ENGINE_DIR)
        self.profile = profile
        self.amsv = amsv_view or AMSVEmbeddedView()

        # Stage A — English-first comprehension.
        self.english_pivot = EnglishPivotComprehension(profile)

        # Stage B — dedicated Sub-AIs.
        self.syntax_sub_ai = SyntaxSubAI(profile, self.amsv, checkpoint_path)
        self.phonology_sub_ai = PhonologySubAI(profile, self.amsv, checkpoint_path)
        self.pragmatic_sub_ai = PragmaticSubAI(profile, self.amsv, checkpoint_path)
        self.editorial_sub_ai = EditorialSubAI(profile, self.amsv, checkpoint_path)

        # Stage C — Six-Language Matrix bridge.
        self.matrix_bridge = BaseSixLanguageMatrixBridge(profile, self.amsv)

        # POS tagging skill (neural from UD checkpoint, else heuristic fallback).
        self.pos_skill = NeuralPOSSkill(profile.engine_dir)

        # Stage D — Reusable Four-Stage Matrix Pattern.
        self.four_stage_engine = None
        if _FOUR_STAGE_OK:
            try:
                contract = RequirementContract(
                    requirement_name=f"{profile.language_name}GrammarLinguisticRequirement",
                    min_word_count=1, max_word_count=10000,
                    context_metadata={"engine": profile.engine_dir, "standard": "Zero-Bridge-AMSV"},
                )
                self.four_stage_engine = FourStageMatrixEngine(
                    engine_name=f"{profile.class_prefix}GrammarFourStageEngine",
                    contract=contract, amsv_view=self.amsv,
                )
            except Exception:
                self.four_stage_engine = None

    # ------------------------------------------------------------------ #
    def comprehend_via_english(self, text: str) -> PivotComprehensionResult:
        """Public entry to the English-first comprehension spine."""
        return self.english_pivot.comprehend(text)

    def process(self, text: str, request_id: Optional[str] = None) -> EngineComprehensiveOutput:
        """Full English-parity analysis with English-first comprehension + AMSV sync."""
        t0 = time.perf_counter()
        request_id = request_id or f"req-{self.profile.iso_code}-001"

        # Stage A — understand English first.
        pivot = self.comprehend_via_english(text)

        # Stage B — dedicated Sub-AIs (write to AMSV).
        eval_syntax = self.syntax_sub_ai.evaluate(text)
        eval_phon = self.phonology_sub_ai.evaluate(text)
        eval_prag = self.pragmatic_sub_ai.evaluate(text)
        eval_edit = self.editorial_sub_ai.evaluate(text)

        # POS tagging (UD-trained neural, else heuristic).
        pos_res = self.pos_skill.tag(text)

        # Stage C — Six-Language Matrix.
        matrix_res = self.matrix_bridge.coordinate(text, request_id=request_id)

        # Stage D — Four-Stage Matrix.
        if self.four_stage_engine is not None:
            try:
                four_stage_res = self.four_stage_engine.execute(
                    text, custom_context={"request_id": request_id})
            except Exception as exc:
                four_stage_res = {"status": "SKIPPED", "reason": str(exc)}
        else:
            four_stage_res = {"status": "UNAVAILABLE"}

        # Stage E — composite score (same weighting family as flagship engines).
        overall = round(
            0.35 * eval_syntax.score +
            0.20 * eval_phon.score +
            0.20 * eval_prag.score +
            0.25 * eval_edit.score,
            4,
        )

        raw = self.amsv.get_raw_bytes()
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        return EngineComprehensiveOutput(
            input_text=text,
            language=self.profile.language_name,
            iso_code=self.profile.iso_code,
            english_pivot=pivot,
            syntax_sub_ai=eval_syntax,
            phonology_sub_ai=eval_phon,
            pragmatic_sub_ai=eval_prag,
            editorial_sub_ai=eval_edit,
            six_language_matrix=matrix_res,
            four_stage_matrix=four_stage_res,
            overall_linguistic_score=overall,
            amsv_bytes_hex=raw.hex(),
            amsv_synced=True,
            latency_ms=elapsed_ms,
            pos_tags=pos_res.pairs(),
            pos_source=pos_res.source,
            notes={
                "english_first": True,
                "english_projection": pivot.english_projection,
                "word_order": self.profile.word_order.value,
                "script": self.profile.script.value,
                "pos_source": pos_res.source,
                "pos_val_accuracy": pos_res.val_token_accuracy,
            },
        )

    # Convenience alias used by some existing engines.
    def analyze(self, text: str) -> EngineComprehensiveOutput:
        return self.process(text)
