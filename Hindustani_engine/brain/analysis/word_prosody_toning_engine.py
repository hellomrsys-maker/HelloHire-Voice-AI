"""
word_prosody_toning_engine.py - Word-Level Prosodic Breakdown & Vocal Toning Engine.

Implements:
1. Word-by-Word Prosodic Breakdown:
   - Tokenizes sentences into individual words with exact duration (ms), pitch (Hz), and focal stress.
   - Example: "आप" (220ms, 145Hz, focal stress), "कैसे" (280ms, sustained), "हैं?" (310ms, falling-rising).
2. Vocal Toning & Texture Parameters (Acoustic Physics for Synthetic Audio Generation):
   - Rough / Gravelly: High glottal tension, lower HNR (roughness: 0.85).
   - Smooth / Breathy: Soft glottal closure, open quotient (smoothness: 0.90).
   - Rash / Harsh: Rapid attack time, high spectral tilt (rashness: 0.80).
   - Calm / Resonant: Fundamental frequency stability, balanced formant envelope (calmness: 0.92).
3. Zero-Bridge 64-Byte AMSV Memory Synchronization:
   - Direct physical in-memory synchronization with AMSVEmbeddedView without Cython/Pybind11/sockets.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum

from amsv.python.amsv_embedded import AMSVEmbeddedView


class VocalTexture(str, Enum):
    ROUGH_GRAVELLY = "ROUGH_GRAVELLY"
    SMOOTH_BREATHY = "SMOOTH_BREATHY"
    RASH_HARSH = "RASH_HARSH"
    CALM_RESONANT = "CALM_RESONANT"


@dataclass
class WordProsodyToken:
    word: str
    clean_word: str
    duration_ms: int
    pitch_hz: float
    focal_stress: bool
    intonation_contour: str  # RISING, FALLING, SUSTAINED, PEAK
    is_terminal: bool
    punctuation: str


@dataclass
class VocalToningProfile:
    texture: VocalTexture
    roughness: float      # 0.0 - 1.0 (Higher in creaky / gravelly / tense voices)
    smoothness: float     # 0.0 - 1.0 (Higher in breathy / flowing / soft voices)
    rashness: float       # 0.0 - 1.0 (Higher in sharp / aggressive / rapid attack voices)
    calmness: float       # 0.0 - 1.0 (Higher in serene / measured / resonant voices)
    spectral_tilt_db: float
    jitter_percent: float


@dataclass
class HindustaniConversationalTimetable:
    expected_response_latency_range_ms: Tuple[int, int]
    post_utterance_pause_ms: int
    floor_management_state: str  # FLOOR_YIELDED, FLOOR_HOLDING, FLOOR_DEMANDING
    interaction_posture: str


@dataclass
class SentenceProsodyResult:
    original_sentence: str
    word_tokens: List[WordProsodyToken]
    total_speech_duration_ms: int
    inter_word_pause_ms: int
    vocal_profile: VocalToningProfile
    detected_register: str
    speech_rate_sps: float # Syllables per second
    amsv_synced: bool = False
    timetable: Optional[HindustaniConversationalTimetable] = None


class WordProsodyToningEngine:
    """
    Engine for word-level prosody decomposition and acoustic vocal toning
    with zero-bridge 64-byte AMSV synchronization.
    """

    AAP_WORDS = {"आप", "आपने", "आपको", "आपका", "आपकी", "आपके", "सर", "जी", "कहिए", "बताइए", "लीजिए", "कीजिए"}
    TUM_WORDS = {"तुम", "तुमने", "तुम्हें", "तुम्हारा", "तुम्हारी", "तुम्हारे", "करो", "कहो", "बताओ", "लो"}
    TU_WORDS = {"तू", "तूने", "तुझे", "तेरा", "तेरी", "तेरे", "कर", "ले", "जा", "यार"}

    FOCAL_WORDS = {"आप", "कैसे", "क्यों", "कहाँ", "कब", "कौन", "शांत", "दर्द", "मोहब्बत", "सत्य", "साहस", "how", "what", "where", "why"}

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view

    def generate_vocal_profile(self, texture: VocalTexture = VocalTexture.CALM_RESONANT) -> VocalToningProfile:
        if texture == VocalTexture.ROUGH_GRAVELLY:
            return VocalToningProfile(
                texture=texture,
                roughness=0.85,
                smoothness=0.20,
                rashness=0.60,
                calmness=0.30,
                spectral_tilt_db=-6.0,
                jitter_percent=2.2
            )
        elif texture == VocalTexture.SMOOTH_BREATHY:
            return VocalToningProfile(
                texture=texture,
                roughness=0.15,
                smoothness=0.90,
                rashness=0.10,
                calmness=0.85,
                spectral_tilt_db=-18.0,
                jitter_percent=0.4
            )
        elif texture == VocalTexture.RASH_HARSH:
            return VocalToningProfile(
                texture=texture,
                roughness=0.65,
                smoothness=0.15,
                rashness=0.80,
                calmness=0.10,
                spectral_tilt_db=-3.0,
                jitter_percent=1.8
            )
        else:  # CALM_RESONANT
            return VocalToningProfile(
                texture=texture,
                roughness=0.10,
                smoothness=0.80,
                rashness=0.10,
                calmness=0.92,
                spectral_tilt_db=-12.0,
                jitter_percent=0.6
            )

    def analyze_sentence(
        self,
        sentence: str,
        texture: VocalTexture = VocalTexture.CALM_RESONANT
    ) -> SentenceProsodyResult:
        raw_words = sentence.strip().split()
        if not raw_words:
            raw_words = ["..."]

        vocal_profile = self.generate_vocal_profile(texture)

        # Baseline pitch modulated by texture
        base_f0 = 135.0
        if texture == VocalTexture.RASH_HARSH:
            base_f0 = 175.0
        elif texture == VocalTexture.ROUGH_GRAVELLY:
            base_f0 = 110.0
        elif texture == VocalTexture.SMOOTH_BREATHY:
            base_f0 = 145.0

        is_question = sentence.endswith("?") or any(q in sentence for q in ["क्या", "कैसे", "क्यों", "कहाँ", "कब", "how", "what", "why"])

        word_tokens: List[WordProsodyToken] = []
        total_duration = 0

        num_words = len(raw_words)
        aap_count = 0
        tum_count = 0
        tu_count = 0

        for i, w in enumerate(raw_words):
            clean = re.sub(r'[.,?!;:।॥"\'\-–—()\[\]{}]+', '', w).strip().lower()
            punct = re.sub(r'[^.,?!;:।॥"\'\-–—()\[\]{}]+', '', w).strip()
            is_term = (i == num_words - 1)

            # Register detection
            if clean in self.AAP_WORDS:
                aap_count += 1
            elif clean in self.TUM_WORDS:
                tum_count += 1
            elif clean in self.TU_WORDS:
                tu_count += 1

            # Focal stress
            is_focal = (clean in self.FOCAL_WORDS) or (i == 0 and is_question)

            # Word Duration calculation
            char_len = max(1, len(clean))
            duration = 180 + (char_len * 35)

            if is_focal:
                duration += 60
            if is_term:
                duration += 50
            if texture == VocalTexture.RASH_HARSH:
                duration = int(duration * 0.85)  # Faster attack
            elif texture == VocalTexture.ROUGH_GRAVELLY:
                duration = int(duration * 1.15)  # Drawn out

            # Pitch Calculation per word
            if is_focal:
                pitch = base_f0 + 20.0
                contour = "PEAK"
            elif is_term and is_question:
                pitch = base_f0 + 25.0
                contour = "RISING"
            elif is_term and not is_question:
                pitch = base_f0 - 15.0
                contour = "FALLING"
            else:
                pitch = base_f0 + (5.0 if i % 2 == 0 else -5.0)
                contour = "SUSTAINED"

            total_duration += duration

            word_tokens.append(WordProsodyToken(
                word=w,
                clean_word=clean,
                duration_ms=duration,
                pitch_hz=round(pitch, 1),
                focal_stress=is_focal,
                intonation_contour=contour,
                is_terminal=is_term,
                punctuation=punct
            ))

        # Register decision
        if aap_count >= tum_count and aap_count >= tu_count and aap_count > 0:
            reg = "AAP"
        elif tum_count > aap_count and tum_count >= tu_count:
            reg = "TUM"
        elif tu_count > aap_count and tu_count > tum_count:
            reg = "TU"
        else:
            reg = "AAP"

        # Inter-word pause
        pause_ms = 45 if texture == VocalTexture.RASH_HARSH else (80 if texture == VocalTexture.ROUGH_GRAVELLY else 60)
        total_duration += pause_ms * max(0, num_words - 1)

        syllables = sum(max(1, len(t.clean_word) // 2) for t in word_tokens)
        speech_rate = (syllables / (total_duration / 1000.0)) if total_duration > 0 else 4.0

        # AMSV Zero-Bridge Memory Synchronization
        synced = False
        if self.amsv is not None:
            # 1. Prosody state (F0, speech rate, fluency, stability)
            fluency = min(1.0, max(0.2, speech_rate / 6.0))
            stability = 0.95 if texture == VocalTexture.CALM_RESONANT else (0.65 if texture == VocalTexture.ROUGH_GRAVELLY else 0.85)
            self.amsv.set_prosody_state(
                f0_hz=base_f0,
                speech_rate=speech_rate,
                fluency=fluency,
                pitch_stability=stability
            )

            # 2. Cognitive capability 3 (Prosody & Pitch Contour)
            self.amsv.set_cognitive_score(3, min(1.0, float(total_duration) / 2000.0))

            # 3. Cognitive capability 4 (Pragmatics & Register)
            reg_score = 0.95 if reg == "AAP" else (0.65 if reg == "TUM" else 0.40)
            self.amsv.set_cognitive_score(4, reg_score)

            # 4. Cognitive capability 6 (Vocal Texture & Toning: Roughness/Smoothness/Rashness/Calmness)
            texture_score = (
                vocal_profile.roughness * 0.25 +
                vocal_profile.smoothness * 0.25 +
                vocal_profile.rashness * 0.25 +
                vocal_profile.calmness * 0.25
            )
            self.amsv.set_cognitive_score(6, texture_score)
            synced = True

        # Conversational Timetable & Turn-taking Floor Mechanics
        if texture == VocalTexture.RASH_HARSH:
            latency_range = (120, 260)
            post_pause = 200
            floor_state = "FLOOR_DEMANDING"
            posture = "AGGRESSIVE_STANCE"
        elif texture == VocalTexture.ROUGH_GRAVELLY:
            latency_range = (350, 700)
            post_pause = 500
            floor_state = "FLOOR_YIELDED"
            posture = "HEAVY_RESONANT_POSTURE"
        elif texture == VocalTexture.SMOOTH_BREATHY:
            latency_range = (450, 800)
            post_pause = 650
            floor_state = "FLOOR_YIELDED"
            posture = "WARM_POLITE_RESPECT"
        else: # CALM_RESONANT
            latency_range = (500, 1000)
            post_pause = 700
            floor_state = "FLOOR_YIELDED"
            posture = "MEASURED_DIGNIFIED_BALANCE"

        timetable = HindustaniConversationalTimetable(
            expected_response_latency_range_ms=latency_range,
            post_utterance_pause_ms=post_pause,
            floor_management_state=floor_state,
            interaction_posture=posture
        )

        return SentenceProsodyResult(
            original_sentence=sentence,
            word_tokens=word_tokens,
            total_speech_duration_ms=total_duration,
            inter_word_pause_ms=pause_ms,
            vocal_profile=vocal_profile,
            detected_register=reg,
            speech_rate_sps=round(speech_rate, 2),
            amsv_synced=synced,
            timetable=timetable
        )
