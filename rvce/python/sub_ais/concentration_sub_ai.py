"""
concentration_sub_ai.py - RVCE Concentration & Focus Sub-AI

Evaluates:
1. Attentive window stability
2. Speech rate tempo variance
3. Distraction and interruption resistance
4. Cognitive endurance factor over elapsed interview duration
5. Cognitive Signal-to-Noise Ratio (SNR)
"""

from __future__ import annotations
from typing import Dict, Any

class ConcentrationSubAI:
    def __init__(self):
        self.optimal_wpm_center = 145.0
        self.optimal_wpm_window = 35.0

    def evaluate(
        self,
        measured_wpm: float,
        elapsed_minutes: float,
        turn_number: int,
        filler_penalty: float = 0.0
    ) -> Dict[str, Any]:
        # Pacing stability
        wpm_diff = abs(measured_wpm - self.optimal_wpm_center)
        pace_stability = max(0.2, 1.0 - (wpm_diff / 80.0))

        # Sustained attention (simulated continuous seconds in active speech)
        sustained_attention_sec = turn_number * 45.0

        # Cognitive endurance decay under continuous cognitive load
        # Degrades slightly over 45+ minute interview
        endurance_factor = max(0.5, 1.0 - (elapsed_minutes * 0.004))

        # Distraction resistance
        distraction_resistance = max(0.1, (pace_stability * 0.7 + (1.0 - filler_penalty) * 0.3) * endurance_factor)

        # Cognitive SNR (dB)
        cognitive_snr_db = 15.0 + (distraction_resistance * 15.0)

        composite = (distraction_resistance * 0.50) + (pace_stability * 0.30) + (endurance_factor * 0.20)

        return {
            "sub_ai": "concentration",
            "sustained_attention_sec": round(sustained_attention_sec, 1),
            "pace_stability": round(pace_stability, 3),
            "endurance_factor": round(endurance_factor, 3),
            "distraction_resistance": round(distraction_resistance, 3),
            "cognitive_snr_db": round(cognitive_snr_db, 1),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
