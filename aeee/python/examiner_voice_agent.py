"""
examiner_voice_agent.py - AI Examiner & Adaptive Examination Engine (AEEE) Python Voice Agent.

Manages adaptive examination dialogue flows, aggregates the 8-dimension scoring rubric,
computes 3PL Item Response Theory (IRT) ability estimation, and synchronizes with AMSV.
"""

from __future__ import annotations
import math
import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class DimensionScore:
    name: str
    weight: float
    score: float  # [0.0, 1.0]

@dataclass
class ComprehensiveEvaluation:
    question_index: int
    theta_estimate: float
    standard_error: float
    composite_score: float
    dimensions: Dict[str, float]
    stopping_criterion_met: bool
    next_question: str

@dataclass
class ExamItem:
    item_id: int
    prompt: str
    difficulty_b: float       # b in [-3.0, +3.0]
    discrimination_a: float   # a in [0.5, 2.5]
    guessing_c: float         # c in [0.0, 0.25]
    administered: bool = False

class ExaminerVoiceAgent:
    """
    Sub-Agent managing real-time adaptive examination with 3PL IRT logic.
    """

    DIMENSION_WEIGHTS = {
        "phonetic_precision": 0.10,
        "prosody_fluency": 0.15,
        "grammatical_accuracy": 0.15,
        "structural_coherence": 0.15,
        "vocabulary_richness": 0.10,
        "analytical_depth": 0.15,
        "emotional_resilience": 0.10,
        "executive_presence": 0.10
    }

    def __init__(self, amsv_state_vector: Optional[memoryview] = None, max_questions: int = 8, target_sem: float = 0.25):
        self.amsv_view = amsv_state_vector
        self.max_questions = max_questions
        self.target_sem = target_sem
        
        self.theta: float = 0.0
        self.sem: float = 1.0
        self.question_index: int = 0
        self.is_completed: bool = False
        self.evaluation_history: List[ComprehensiveEvaluation] = []

        # Default calibrated 3PL item bank across difficulty spectrum
        self.item_bank: List[ExamItem] = [
            # Low Difficulty (Warmup / Foundations: b in [-2.0, -0.5])
            ExamItem(1, "Please introduce your core technical specialization and summarize your most impactful system design.", -1.5, 1.2, 0.05),
            ExamItem(2, "Explain the difference between synchronous and asynchronous communication in distributed systems.", -1.0, 1.4, 0.05),
            ExamItem(3, "Describe a time when you had to learn a completely new domain or technology under a tight deadline.", -0.5, 1.3, 0.05),

            # Medium Difficulty (Mid-Senior: b in [-0.2, +1.0])
            ExamItem(4, "How do you systematically analyze and resolve lock contention and memory bandwidth saturation in high-throughput pipelines?", 0.2, 1.8, 0.05),
            ExamItem(5, "Reconcile a critical security vulnerability discovered 2 hours before an enterprise release with client SLA penalties.", 0.6, 1.7, 0.05),
            ExamItem(6, "Evaluate the architectural trade-offs between eventual consistency and linearizability under network partitions.", 1.0, 1.9, 0.05),

            # High Difficulty (Staff / Principal / Executive: b in [+1.2, +2.5])
            ExamItem(7, "Design an ultra-low-latency zero-bridge memory synchronization layer connecting disparate runtime memory spaces without serialization overhead.", 1.6, 2.2, 0.05),
            ExamItem(8, "Formulate a board-level capital allocation strategy for an enterprise AI transformation during a 40% margin compression.", 2.1, 2.4, 0.05),
            ExamItem(9, "A distributed consensus cluster is suffering from asymmetric packet loss causing cascading leader reelection loops. Isolate the mathematical proof of convergence failure.", 2.5, 2.5, 0.05)
        ]

    def start_exam(self) -> str:
        """Starts examination session and returns initial question."""
        self.theta = 0.0
        self.sem = 1.0
        self.question_index = 0
        self.is_completed = False
        self.evaluation_history.clear()
        for item in self.item_bank:
            item.administered = False

        first_item = self._select_next_item()
        if first_item:
            first_item.administered = True
            self.question_index = 1
            self._sync_to_amsv()
            return first_item.prompt
        return "Begin by describing your background."

    def submit_candidate_response(
        self,
        candidate_transcript: str,
        dimension_signals: Optional[Dict[str, float]] = None
    ) -> ComprehensiveEvaluation:
        """
        Processes candidate response, updates 3PL IRT ability estimate,
        checks stopping rules, and selects next adaptive probe.
        """
        # Default dimension signals if not provided
        signals = dimension_signals or {}
        dim_scores = {}
        for dim, weight in self.DIMENSION_WEIGHTS.items():
            dim_scores[dim] = float(signals.get(dim, 0.70))

        # Composite score
        composite = sum(dim_scores[d] * self.DIMENSION_WEIGHTS[d] for d in self.DIMENSION_WEIGHTS)

        # Update IRT theta estimate using last administered item
        last_item = self._get_last_administered_item()
        if last_item:
            self._update_irt_theta(composite, last_item.difficulty_b, last_item.discrimination_a)

        # Check stopping rule
        if self.question_index >= self.max_questions or (self.question_index >= 3 and self.sem <= self.target_sem):
            self.is_completed = True
            next_q = "Examination complete. Thank you."
        else:
            next_item = self._select_next_item()
            if next_item:
                next_item.administered = True
                self.question_index += 1
                next_q = next_item.prompt
            else:
                self.is_completed = True
                next_q = "Examination complete. All items administered."

        # Sync with AMSV
        self._sync_to_amsv()

        evaluation = ComprehensiveEvaluation(
            question_index=self.question_index,
            theta_estimate=self.theta,
            standard_error=self.sem,
            composite_score=composite,
            dimensions=dim_scores,
            stopping_criterion_met=self.is_completed,
            next_question=next_q
        )
        self.evaluation_history.append(evaluation)
        return evaluation

    def _select_next_item(self) -> Optional[ExamItem]:
        """Selects unadministered item maximizing Fisher Information at current theta."""
        best_item = None
        max_info = -1.0

        for item in self.item_bank:
            if not item.administered:
                info = self._fisher_information(self.theta, item)
                if info > max_info:
                    max_info = info
                    best_item = item
        return best_item

    def _fisher_information(self, theta: float, item: ExamItem) -> float:
        a = item.discrimination_a
        b = item.difficulty_b
        c = item.guessing_c

        exp_term = math.exp(-max(-25.0, min(25.0, a * (theta - b))))
        p_star = 1.0 / (1.0 + exp_term)
        p = c + (1.0 - c) * p_star

        if p <= c or p >= 1.0:
            return 0.0
        
        numerator = (a ** 2) * (p_star ** 2) * (1.0 - p)
        return numerator / p

    def _update_irt_theta(self, response_quality: float, difficulty_b: float, discrimination_a: float) -> None:
        """Newton-Raphson update with Gaussian prior N(0, 1)."""
        theta = self.theta
        a = discrimination_a
        b = difficulty_b
        u = response_quality

        exp_term = math.exp(-max(-25.0, min(25.0, a * (theta - b))))
        p = 1.0 / (1.0 + exp_term)

        # Prior log-gradient: -theta, prior precision: 1.0
        grad = -theta + a * (u - p)
        info = 1.0 + (a ** 2) * p * (1.0 - p)

        delta = grad / info
        delta = max(-0.75, min(0.75, delta))

        self.theta = max(-3.5, min(3.5, theta + delta))
        self.sem = 1.0 / math.sqrt(max(0.1, info))

    def _get_last_administered_item(self) -> Optional[ExamItem]:
        admin = [i for i in self.item_bank if i.administered]
        return admin[-1] if admin else None

    def _sync_to_amsv(self) -> None:
        if self.amsv_view is None:
            return

        # AEEE Examination state is at byte offset 0x28 (40) in AMSV AtomicStateVector (8 bytes uint64)
        # Bit layout:
        # [Bits 0-31: Theta (IEEE 754 float) | Bits 32-47: SEM Q16 | Bits 48-63: Question Index]
        theta_bytes = struct.pack("<f", float(self.theta))
        theta_bits = struct.unpack("<I", theta_bytes)[0]

        sem_q16 = int(max(0.0, min(1.0, self.sem)) * 65535)
        packed_u64 = (
            (theta_bits & 0xFFFFFFFF) |
            ((sem_q16 & 0xFFFF) << 32) |
            ((self.question_index & 0xFFFF) << 48)
        )
        struct.pack_into("<Q", self.amsv_view, 40, packed_u64)
