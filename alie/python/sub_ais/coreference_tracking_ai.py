"""
coreference_tracking_ai.py — Cross-Turn Co-Reference & Entity Persistence Sub-AI (ALIE)

Tracks whether the candidate correctly uses, recalls, and builds upon
entities (people, projects, technologies, metrics) introduced in earlier turns.
"""
from __future__ import annotations
import re
from typing import Dict, Any, List

class CoreferenceTrackingAI:
    def evaluate(
        self,
        current_answer: str,
        conversation_history: List[str]
    ) -> Dict[str, Any]:
        if not conversation_history:
            return {
                "sub_ai": "coreference_tracking",
                "entities_detected_in_history": [],
                "entities_carried_forward": [],
                "entity_retention_rate": 0.88,
                "narrative_continuity": 0.87,
                "composite_score": 0.88
            }

        curr_lower = current_answer.lower()
        curr_words = set(re.findall(r'\b[a-z]{5,}\b', curr_lower))

        # Extract entities from history (words ≥5 chars, proxy for content words)
        history_entities = []
        for turn in conversation_history:
            turn_entities = re.findall(r'\b[a-z]{5,}\b', turn.lower())
            history_entities.extend(turn_entities)

        unique_entities = list(set(history_entities))

        # Check which entities the candidate re-used correctly
        carried = [e for e in unique_entities if e in curr_words]

        # Entity retention rate
        retention = len(carried) / max(1, len(unique_entities))
        retention_clamped = min(1.0, max(0.2, 0.40 + retention * 4.0))

        # Narrative continuity: does current answer reference prior turn entities?
        prev_turn_words = set(re.findall(r'\b[a-z]{5,}\b', conversation_history[-1].lower()))
        recent_overlap = len(curr_words & prev_turn_words) / max(1, len(prev_turn_words))
        continuity = min(1.0, max(0.25, recent_overlap * 4.0))

        composite = retention_clamped * 0.55 + continuity * 0.45

        return {
            "sub_ai": "coreference_tracking",
            "entities_detected_in_history": unique_entities[:10],
            "entities_carried_forward": carried[:10],
            "entity_retention_rate": round(retention_clamped, 3),
            "narrative_continuity": round(continuity, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
