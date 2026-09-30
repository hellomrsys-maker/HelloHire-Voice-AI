"""
rvce_orchestrator.py - Recruitment Verbal Cognitive Engine Master Orchestrator

Coordinates all six cognitive sub-AIs:
1. ThinkingSubAI
2. ConcentrationSubAI
3. RecallSubAI
4. CreativitySubAI
5. ImaginationSubAI
6. VerbalSubAI

Zero-Bridge Synchronous Memory Rule:
Binds directly to the shared 64-byte AMSV physical memory buffer with 0-nanosecond latency.
No serialization, no bridge libraries, direct in-place mutation.
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from rvce.python.sub_ais.thinking_sub_ai import ThinkingSubAI
from rvce.python.sub_ais.concentration_sub_ai import ConcentrationSubAI
from rvce.python.sub_ais.recall_sub_ai import RecallSubAI
from rvce.python.sub_ais.creativity_sub_ai import CreativitySubAI
from rvce.python.sub_ais.imagination_sub_ai import ImaginationSubAI
from rvce.python.sub_ais.verbal_sub_ai import VerbalSubAI

class RecruitmentVerbalCognitiveOrchestrator:
    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        """
        Initializes the RVCE Orchestrator.
        :param master_amsv_buffer: 64-byte shared memory bytearray (0-ns zero-bridge)
        """
        self.thinking_ai = ThinkingSubAI()
        self.concentration_ai = ConcentrationSubAI()
        self.recall_ai = RecallSubAI()
        self.creativity_ai = CreativitySubAI()
        self.imagination_ai = ImaginationSubAI()
        self.verbal_ai = VerbalSubAI()

        self.amsv_buffer = master_amsv_buffer
        self.conversation_history: List[str] = []

    def evaluate_turn(
        self,
        candidate_transcript: str,
        turn_number: int,
        measured_wpm: float = 145.0,
        elapsed_minutes: float = 5.0,
        claimed_resume_entities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's turn across all 6 cognitive faculties and
        atomically synchronizes to the shared AMSV memory.
        """
        # 1. Verbal Articulation
        verbal_res = self.verbal_ai.evaluate(candidate_transcript, measured_wpm)

        # 2. Thinking Ability
        thinking_res = self.thinking_ai.evaluate(candidate_transcript)

        # 3. Concentration & Focus
        concentration_res = self.concentration_ai.evaluate(
            measured_wpm=measured_wpm,
            elapsed_minutes=elapsed_minutes,
            turn_number=turn_number,
            filler_penalty=verbal_res["filler_penalty"]
        )

        # 4. Recall & Working Memory
        recall_res = self.recall_ai.evaluate(
            current_transcript=candidate_transcript,
            conversation_history=self.conversation_history,
            claimed_resume_entities=claimed_resume_entities
        )

        # 5. Creativity & Out-of-the-Box Thinking
        creativity_res = self.creativity_ai.evaluate(candidate_transcript)

        # 6. Imagination & Future Forecasting
        imagination_res = self.imagination_ai.evaluate(candidate_transcript)

        # Store transcript for subsequent turn recall checks
        self.conversation_history.append(candidate_transcript)

        # Weighted Composite Hireability Formulation
        composite = (
            thinking_res["composite_score"] * 0.22 +
            concentration_res["composite_score"] * 0.15 +
            recall_res["composite_score"] * 0.18 +
            creativity_res["composite_score"] * 0.15 +
            imagination_res["composite_score"] * 0.15 +
            verbal_res["composite_score"] * 0.15
        )
        composite = min(1.0, max(0.0, composite))

        # Recommendation Code
        if composite >= 0.82:
            rec_code = 1
            rec_label = "STRONG_HIRE"
        elif composite >= 0.68:
            rec_code = 2
            rec_label = "HIRE"
        elif composite >= 0.52:
            rec_code = 3
            rec_label = "LEANING_HIRE"
        else:
            rec_code = 4
            rec_label = "NO_HIRE"

        report = {
            "turn": turn_number,
            "composite_hireability": round(composite, 3),
            "recommendation_code": rec_code,
            "recommendation_label": rec_label,
            "faculties": {
                "thinking": thinking_res,
                "concentration": concentration_res,
                "recall": recall_res,
                "creativity": creativity_res,
                "imagination": imagination_res,
                "verbal": verbal_res,
            }
        }

        # Synchronize to physical AMSV memory
        self.sync_to_amsv(report, scenario_id=202, turn=turn_number)
        return report

    def sync_to_amsv(self, report: Dict[str, Any], scenario_id: int, turn: int) -> None:
        """
        Zero-Bridge Synchronous Memory Sync:
        Writes 16-bit Q16 fixed-point metrics directly into physical memory offsets.
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(val: float) -> int:
            return int(min(1.0, max(0.0, val)) * 65535.0)

        f = report["faculties"]
        q_think = to_q16(f["thinking"]["composite_score"])
        q_focus = to_q16(f["concentration"]["composite_score"])
        q_recal = to_q16(f["recall"]["composite_score"])
        q_creat = to_q16(f["creativity"]["composite_score"])

        # Offset 0x10: ccte_cog_bank_alpha [Thinking | Focus | Recall | Creativity]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x10, q_think, q_focus, q_recal, q_creat)

        q_imagi = to_q16(f["imagination"]["composite_score"])
        q_analy = to_q16(f["thinking"]["deductive_validity"])
        q_verba = to_q16(f["verbal"]["composite_score"])
        q_emoti = to_q16(f["concentration"]["distraction_resistance"])

        # Offset 0x18: ccte_cog_bank_beta [Imagination | Analytical | Verbal | Composure]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x18, q_imagi, q_analy, q_verba, q_emoti)

        # Offset 0x20: rsse_scenario_state [ScenarioID | Turn | Score | RecCode]
        q_global = to_q16(report["composite_hireability"])
        struct.pack_into("<HHHH", self.amsv_buffer, 0x20, scenario_id, turn, q_global, report["recommendation_code"])
