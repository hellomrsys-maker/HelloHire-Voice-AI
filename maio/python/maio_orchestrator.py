"""
maio_orchestrator.py - Main Artificial Intelligence Orchestrator (MAIO) Python Implementation.

Coordinates all sub-agents (VCE, CCTE-8, RSSE, AEEE, Lingua Sapiens), maintains
the cross-agent knowledge graph, performs holistic gap reasoning, issues dynamic
interventions, and synchronizes with the AMSV 64-byte shared memory state vector.
"""

from __future__ import annotations
import math
import struct
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from amsv.python.amsv_embedded import AMSVEmbeddedView
from vce.python.vce_subagent import VceSubAgent
from ccte.python.ccte_subagents import CCTECoordinator
from rsse.python.scenario_agent import RecruitmentScenarioAgent
from aeee.python.examiner_voice_agent import ExaminerVoiceAgent
from gra_voi.reasoning.engine import DeepReasoningEngine

@dataclass
class HolisticAssessmentReport:
    session_id: str
    global_competency_index: float
    irt_ability_theta: float
    dimension_scores: Dict[str, float]
    root_cause_diagnoses: List[str]
    active_interventions: List[str]
    prescriptive_curriculum: List[str]

class MaioOrchestrator:
    """
    Main Artificial Intelligence Orchestrator governing the Six-Language Matrix system.
    """

    def __init__(self, amsv_state_vector: Optional[memoryview] = None):
        self.amsv_view = amsv_state_vector
        embedded_view = AMSVEmbeddedView(amsv_state_vector) if amsv_state_vector is not None else None
        
        # Instantiate sub-agents
        self.vce_agent = VceSubAgent(amsv_view=embedded_view)
        self.ccte_coordinator = CCTECoordinator(amsv_view=embedded_view)
        self.rsse_agent = RecruitmentScenarioAgent(amsv_state_vector=amsv_state_vector)
        self.aeee_agent = ExaminerVoiceAgent(amsv_state_vector=amsv_state_vector)
        self.grammar_engine = DeepReasoningEngine()

        # Cross-Agent Knowledge Graph State
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {
            "vce": {"fluency": 0.8, "phonetic_accuracy": 0.85, "speech_rate": 135.0},
            "ccte": {},
            "rsse": {"phase": "WarmupIntroduction", "register_compliance": 1.0},
            "aeee": {"theta": 0.0, "sem": 1.0},
            "grammar": {"complexity": 0.8, "error_count": 0}
        }
        self.intervention_history: List[str] = []

    def initialize_session(self, format_code: int = 1, scenario_id: int = 101) -> str:
        """Initializes a new training or examination session across all sub-agents."""
        opening_prompt = self.rsse_agent.start_scenario(format_code, scenario_id)
        exam_prompt = self.aeee_agent.start_exam()
        
        self._sync_to_amsv(global_comp=0.75, interventions=0)
        return f"{opening_prompt}\n\nExaminer: {exam_prompt}"

    def process_candidate_turn(
        self,
        candidate_utterance: str,
        speech_wpm: float = 135.0,
        pitch_contour: Optional[List[float]] = None
    ) -> HolisticAssessmentReport:
        """
        Processes a candidate turn through the unified multi-agent intelligence pipeline.
        """
        # 1. Grammar & Structural Reasoning (Lingua Sapiens)
        deep_reasoning = self.grammar_engine.think(candidate_utterance)
        grammar_score = 0.95 if not deep_reasoning.ambiguities_detected else 0.85

        # 2. VCE Acoustic & Prosody Evaluation
        vce_eval = self.vce_agent.evaluate_text_utterance(
            candidate_utterance,
            pitch_contour=pitch_contour,
            speech_wpm=speech_wpm
        )

        # 3. RSSE Register & Scenario Evaluation
        rsse_eval = self.rsse_agent.evaluate_turn(candidate_utterance, wpm=speech_wpm)

        # 4. CCTE Multi-Capability Cognitive Evaluation
        ccte_scores = self.ccte_coordinator.evaluate_candidate_turn(candidate_utterance, speech_wpm)

        # 5. Aggregate Signals into 8-Dimension Rubric for AEEE
        fl_score = float(vce_eval.get("fluency_score", 0.8))
        ph_score = float(vce_eval.get("phoneme_accuracy", 0.85))
        verb_score = float(ccte_scores.get("verbal_reasoning", 0.7))

        dim_signals = {
            "phonetic_precision": ph_score,
            "prosody_fluency": fl_score,
            "grammatical_accuracy": grammar_score,
            "structural_coherence": rsse_eval.star_eval.overall_star_coherence if rsse_eval.star_eval else 0.75,
            "vocabulary_richness": rsse_eval.register_compliance,
            "analytical_depth": ccte_scores.get("analytical_thinking", 0.7),
            "emotional_resilience": ccte_scores.get("emotional_regulation", 0.7),
            "executive_presence": (fl_score * 0.5 + verb_score * 0.5)
        }

        # 6. AEEE Adaptive IRT Update & Next Question
        aeee_eval = self.aeee_agent.submit_candidate_response(candidate_utterance, dim_signals)

        # 7. Update Knowledge Graph
        self._update_knowledge_graph(vce_eval, ccte_scores, rsse_eval, aeee_eval, grammar_score)

        # 8. Holistic Gap Reasoning & Root Cause Diagnosis
        diagnoses = self._diagnose_holistic_gaps(dim_signals)

        # 9. Dynamic Intervention Directives
        active_interventions, bitmask = self._generate_interventions(dim_signals)

        # 10. Compute Global Competency Index
        global_comp = sum(dim_signals.values()) / len(dim_signals)

        # 11. Prescriptive Curriculum Generation
        curriculum = self._generate_prescriptive_curriculum(dim_signals, diagnoses)

        # 12. Synchronize with AMSV
        self._sync_to_amsv(global_comp, bitmask)

        return HolisticAssessmentReport(
            session_id="SESSION-SOLOROCK-001",
            global_competency_index=global_comp,
            irt_ability_theta=aeee_eval.theta_estimate,
            dimension_scores=dim_signals,
            root_cause_diagnoses=diagnoses,
            active_interventions=active_interventions,
            prescriptive_curriculum=curriculum
        )

    def _update_knowledge_graph(self, vce_eval, ccte_scores, rsse_eval, aeee_eval, grammar_score):
        self.knowledge_graph["vce"]["fluency"] = vce_eval.get("fluency_score", 0.8)
        self.knowledge_graph["vce"]["phonetic_accuracy"] = vce_eval.get("phoneme_accuracy", 0.85)
        self.knowledge_graph["ccte"] = ccte_scores
        self.knowledge_graph["rsse"]["phase"] = rsse_eval.phase_name
        self.knowledge_graph["rsse"]["register_compliance"] = rsse_eval.register_compliance
        self.knowledge_graph["aeee"]["theta"] = aeee_eval.theta_estimate
        self.knowledge_graph["aeee"]["sem"] = aeee_eval.standard_error
        self.knowledge_graph["grammar"]["score"] = grammar_score

    def _diagnose_holistic_gaps(self, dims: Dict[str, float]) -> List[str]:
        diagnoses = []
        # Check if dysfluency is caused by cognitive overload
        if dims["prosody_fluency"] < 0.60 and dims["analytical_depth"] > 0.80:
            diagnoses.append("High Cognitive Load Trade-off: Deep analytical synthesis is creating acoustic hesitations and dysfluent pacing.")
        
        # Check if emotional dysregulation is impairing working memory
        if dims["emotional_resilience"] < 0.50 and dims["structural_coherence"] < 0.60:
            diagnoses.append("Acute Stress Impairment: High sympathetic arousal is fragmenting answer structure (STAR breakdown).")

        # Check vocabulary and register misalignment
        if dims["vocabulary_richness"] < 0.55:
            diagnoses.append("Register Deficit: Response lacks expected domain-specific technical vocabulary and executive gravitas.")

        if not diagnoses:
            diagnoses.append("Optimal Integrated Flow: Cohesive alignment across cognitive, linguistic, and acoustic layers.")
        return diagnoses

    def _generate_interventions(self, dims: Dict[str, float]) -> Tuple[List[str], int]:
        interventions = []
        bitmask = 0

        if dims["emotional_resilience"] < 0.40:
            interventions.append("STRESS_DEESCALATION: Soften probe tone and lower situational pressure.")
            bitmask |= 0x01

        if dims["structural_coherence"] < 0.50:
            interventions.append("PROMPT_STRUCTURE: Request candidate to explicitly frame response using STAR/MECE.")
            bitmask |= 0x02

        if dims["prosody_fluency"] < 0.45:
            interventions.append("PACE_REGULATION: Encourage controlled pause and deliberate breathing cadence.")
            bitmask |= 0x04

        if dims["vocabulary_richness"] > 0.85 and dims["analytical_depth"] > 0.85:
            interventions.append("EXECUTIVE_ELEVATION: Escalate question to principal/board-level strategic ambiguity.")
            bitmask |= 0x08

        return interventions, bitmask

    def _generate_prescriptive_curriculum(self, dims: Dict[str, float], diagnoses: List[str]) -> List[str]:
        curriculum = []
        if dims["structural_coherence"] < 0.70:
            curriculum.append("Module CCTE-04: Structured Communication & STAR/MECE Decomposition Drills")
        if dims["emotional_resilience"] < 0.70:
            curriculum.append("Module CCTE-08: Vagal Tone & High-Pressure Acoustic Demeanor Training")
        if dims["prosody_fluency"] < 0.70:
            curriculum.append("Module VCE-02: Rhythmic Entrainment & Pitch Contour Inflection Workstation")
        if dims["vocabulary_richness"] < 0.70:
            curriculum.append("Module RSSE-03: C-Suite Lexicon & Strategic Vocabulary Gating")
        if not curriculum:
            curriculum.append("Mastery Maintenance: Advanced Dynamic Stress Simulation & Hostile Panel Defense")
        return curriculum

    def _sync_to_amsv(self, global_comp: float, interventions: int) -> None:
        if self.amsv_view is None:
            return

        # Offset 0x30 (48): maio_global_state_alpha [Bits 0-31: Float GCI | Bits 32-63: Health/Timestamp]
        gci_bytes = struct.pack("<f", float(global_comp))
        gci_bits = struct.unpack("<I", gci_bytes)[0]
        packed_alpha = (gci_bits & 0xFFFFFFFF) | (0x0100 << 32)
        struct.pack_into("<Q", self.amsv_view, 48, packed_alpha)

        # Offset 0x38 (56): maio_global_state_beta [Bits 0-31: Interventions bitmask]
        packed_beta = interventions & 0xFFFFFFFF
        struct.pack_into("<Q", self.amsv_view, 56, packed_beta)
