"""
linguistic_drive_core.py - Linguistic Drive Core (Drive Core)
Governs communicative motive force, objective priorities, pedagogical intent,
and dynamic attention weighting across Engines A, B, C, and D.
Directly synchronizes to AMSV Offset 0x38-0x3F (maio_global_state_beta).
"""

from __future__ import annotations
import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from amsv.python.amsv_embedded import AMSVEmbeddedView


class LinguisticDriveCore:
    """
    Drive Core: Motive force, communicative intention steering, and attention routing.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

    def evaluate_drive_state(
        self,
        current_phase: str = "COMPOSITION_AND_COMMUNICATION",
        user_intent: str = "MASTERY"
    ) -> Dict[str, Any]:
        """
        Calculates drive intensity and engine weights based on communicative context.
        """
        # Engine attention weights (Engine A: Written, B: Verbal, C: Phonology, D: Cognitive)
        if user_intent == "VERBAL_INTERVIEW":
            weights = {"engine_a": 0.15, "engine_b": 0.45, "engine_c": 0.20, "engine_d": 0.20}
            directives_mask = 0x00000002 # Verbal priority directive
        elif user_intent == "ACADEMIC_WRITING":
            weights = {"engine_a": 0.50, "engine_b": 0.10, "engine_c": 0.10, "engine_d": 0.30}
            directives_mask = 0x00000001 # Written grammar directive
        elif user_intent == "PRONUNCIATION_TRAINING":
            weights = {"engine_a": 0.10, "engine_b": 0.20, "engine_c": 0.50, "engine_d": 0.20}
            directives_mask = 0x00000004 # Phonology directive
        else: # BALANCED_MASTERY
            weights = {"engine_a": 0.25, "engine_b": 0.25, "engine_c": 0.25, "engine_d": 0.25}
            directives_mask = 0x00000007 # Holistic directive

        # Zero-bridge synchronization to AMSV Offset 0x38 - 0x3F (maio_global_state_beta):
        # Bits 0-31: Intervention Directives Bitmask
        # Bits 32-63: Cross-Module Attention Weights (packed into uint32)
        packed_weights = (
            (int(weights["engine_a"] * 255) << 24) |
            (int(weights["engine_b"] * 255) << 16) |
            (int(weights["engine_c"] * 255) << 8)  |
            (int(weights["engine_d"] * 255))
        )
        self.amsv.set_intervention_directives(directives_mask)
        self.amsv.set_cross_module_attention(packed_weights)

        return {
            "core": "Linguistic_Drive_Core",
            "phase": current_phase,
            "user_intent": user_intent,
            "engine_weights": weights,
            "directives_mask": hex(directives_mask),
            "packed_weights_hex": hex(packed_weights),
            "motive_force_momentum": 0.95,
            "amsv_sync_offset": "0x38-0x3F"
        }
