"""
dialogue_dynamics_analyzer.py - Conversational Dialogue Dynamics & Turn-Taking Analyzer for Hindustani.

Analyzes natural conversational behavior, inter-turn latency (response wait time in ms),
conversational floor management, prosodic delivery cadence, and pragmatic register alignment
based on observational discourse modeling, without any voice cloning.
Syncs latency and timing parameters directly into the 64-byte Atomic Memory State Vector.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from amsv.python.amsv_embedded import AMSVEmbeddedView


@dataclass
class TurnDynamicsResult:
    input_text: str
    detected_register: str
    recommended_reply_register: str
    is_question: bool
    floor_yielding: bool
    recommended_wait_time_ms: int
    optimal_latency_range_ms: Tuple[int, int]
    delivery_tempo: str
    speech_act_detected: str
    recommended_reply_speech_act: str
    focal_emphasis_detected: List[str] = field(default_factory=list)
    amsv_synced: bool = False


class DialogueDynamicsAnalyzer:
    """
    Analyzes observational communicative dynamics, turn-taking pauses,
    and conversational cadence for Hindustani interactions.
    """

    # Honorific markers
    AAP_MARKERS = ["आप", "आपने", "आपको", "आपका", "आपकी", "आपके", "सर", "जी", "कहिए", "बताइए", "लीजिए", "कीजिए"]
    TUM_MARKERS = ["तुम", "तुमने", "तुम्हें", "तुम्हारा", "तुम्हारी", "तुम्हारे", "करो", "कहो", "बताओ", "लो"]
    TU_MARKERS = ["तू", "तूने", "तुझे", "तेरा", "तेरी", "तेरे", "कर", "ले", "जा", "यार"]

    # Floor-holding fillers (indicating the speaker hasn't finished thinking / yielded floor)
    FLOOR_HOLDING_FILLERS = ["देखिए", "मतलब", "असल में", "सच कहूँ तो", "रुकिए", "रुको", "सोचने दीजिए", "बात यह है"]

    # Deliberative / profound thought indicators requiring longer reflective latency
    REFLECTIVE_MARKERS = ["चेतना", "अनुभूति", "गहरी", "रहस्य", "संवेदनाओं", "सैद्धांतिक", "दार्शनिक", "विचार"]

    # Urgent / rapid markers indicating brisk turn transitions
    URGENT_MARKERS = ["तुरंत", "अभी", "क्रैश", "जल्दी", "फटाफट", "रुक", "शटडाउन", "आपात"]

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view

    def analyze_dialogue_turn(self, utterance: str) -> TurnDynamicsResult:
        text = utterance.strip()
        words = [re.sub(r'[^\w\s]', '', w) for w in text.split()]

        # 1. Register Detection
        aap_count = sum(1 for w in words if w in self.AAP_MARKERS)
        tum_count = sum(1 for w in words if w in self.TUM_MARKERS)
        tu_count = sum(1 for w in words if w in self.TU_MARKERS)

        if aap_count >= tum_count and aap_count >= tu_count and aap_count > 0:
            current_reg = "AAP"
            reply_reg = "AAP"
        elif tum_count > aap_count and tum_count >= tu_count:
            current_reg = "TUM"
            reply_reg = "TUM"
        elif tu_count > aap_count and tu_count > tum_count:
            current_reg = "TU"
            reply_reg = "TU"
        else:
            current_reg = "AAP"  # Default respectful register
            reply_reg = "AAP"

        # 2. Question & Terminal Contour
        is_question = any(q in text for q in ["क्या", "क्यों", "कैसे", "कहाँ", "कब", "किस", "किसने", "?"]) or text.endswith("?")

        # 3. Floor Holding vs Yielding
        has_filler = any(f in text for f in self.FLOOR_HOLDING_FILLERS)
        # If utterance ends with ellipsis (...) or mid-clause, speaker might be holding floor
        floor_yielding = not (text.endswith("...") or (has_filler and len(words) < 5))

        # 4. Latency / Wait Time Determination (in milliseconds)
        is_reflective = any(r in text for r in self.REFLECTIVE_MARKERS)
        is_urgent = any(u in text for u in self.URGENT_MARKERS)

        if is_urgent:
            tempo = "ALLEGRO_FAST"
            target_ms = 280
            range_ms = (180, 380)
            speech_act = "URGENT_PROMPT"
            reply_act = "IMMEDIATE_ACTION"
        elif is_reflective:
            tempo = "LENTO_DELIBERATE"
            target_ms = 950
            range_ms = (750, 1300)
            speech_act = "REFLECTIVE_INQUIRY"
            reply_act = "MEDITATIVE_ANALYSIS"
        elif is_question:
            tempo = "MODERATE_INQUIRING"
            target_ms = 500 if current_reg == "AAP" else 380
            range_ms = (350, 650)
            speech_act = "INQUIRY"
            reply_act = "REASSURING_EXPLANATION"
        else:
            tempo = "FLOWING_CONVERSATIONAL"
            target_ms = 450
            range_ms = (300, 580)
            speech_act = "INFORMATIONAL_STATEMENT"
            reply_act = "ACKNOWLEDGMENT"

        # 5. Extract Focal Emphasis Points
        focal_points = []
        for w in words:
            if w in ["बिल्कुल", "ज़रूर", "बहुत", "पूरी", "शून्य", "हमेशा", "कभी", "सत्य"]:
                focal_points.append(w)

        # 6. AMSV Zero-Bridge Memory Sync
        synced = False
        if self.amsv is not None:
            # Sync timing and prosody fluency into AMSV
            fluency_score = min(1.0, max(0.2, 1000.0 / float(target_ms)))
            self.amsv.set_prosody_state(f0_hz=140.0, speech_rate=4.5, fluency=fluency_score, pitch_stability=0.88)
            # Capability 4: Pragmatics & Register
            pol_score = 0.95 if current_reg == "AAP" else (0.65 if current_reg == "TUM" else 0.40)
            self.amsv.set_cognitive_score(4, pol_score)
            synced = True

        return TurnDynamicsResult(
            input_text=text,
            detected_register=current_reg,
            recommended_reply_register=reply_reg,
            is_question=is_question,
            floor_yielding=floor_yielding,
            recommended_wait_time_ms=target_ms,
            optimal_latency_range_ms=range_ms,
            delivery_tempo=tempo,
            speech_act_detected=speech_act,
            recommended_reply_speech_act=reply_act,
            focal_emphasis_detected=focal_points,
            amsv_synced=synced,
        )
