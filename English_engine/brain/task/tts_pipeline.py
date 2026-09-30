"""
Text-to-Speech (TTS) Front-End and SSML Synthesis Pipeline.
Transforms raw English orthography into normalized SSML and timed phonemic streams
with prosodic contours, pitch targets, and duration coefficients.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer
from English_engine.brain.skills.g2p import EnglishG2PConverter


@dataclass
class PhonemeFrame:
    phoneme: str
    duration_ms: float
    pitch_hz: float
    stress: int  # 0: unstressed, 1: primary, 2: secondary
    is_pause: bool = False


@dataclass
class TTSOutput:
    ssml: str
    phoneme_stream: List[PhonemeFrame]
    total_duration_seconds: float
    sample_rate_hz: int
    audio_format: str


class TTSPipeline:
    """
    TTS Front-end converter synthesizing SSML and timed acoustic phoneme streams.
    """

    def __init__(self, default_pitch_hz: float = 120.0, default_rate: str = "medium") -> None:
        self.tokenizer = EnglishTokenizer()
        self.g2p = EnglishG2PConverter()
        self.default_pitch_hz = default_pitch_hz
        self.default_rate = default_rate

    def synthesize_stream(self, text: str, voice_name: str = "en-US-Standard-C") -> TTSOutput:
        tokens = self.tokenizer.tokenize(text)
        phoneme_frames: List[PhonemeFrame] = []
        total_time_ms = 0.0

        for tok in tokens:
            if not tok.is_word:
                # Punctuation pause
                pause_duration = 300.0 if tok.text in {".", "!", "?"} else 150.0
                phoneme_frames.append(
                    PhonemeFrame(
                        phoneme="SIL",
                        duration_ms=pause_duration,
                        pitch_hz=0.0,
                        stress=0,
                        is_pause=True,
                    )
                )
                total_time_ms += pause_duration
                continue

            # Grapheme to Phoneme
            g2p_res = self.g2p.convert_word(tok.text)
            for p in g2p_res.phonemes:
                stress = 0
                if p.endswith("1"):
                    stress = 1
                elif p.endswith("2"):
                    stress = 2

                # Pitch contour variation
                pitch = self.default_pitch_hz * (1.2 if stress == 1 else 1.0)
                dur = 85.0 if stress == 1 else 65.0

                phoneme_frames.append(
                    PhonemeFrame(
                        phoneme=p,
                        duration_ms=dur,
                        pitch_hz=round(pitch, 1),
                        stress=stress,
                        is_pause=False,
                    )
                )
                total_time_ms += dur

            # Inter-word silence (30ms)
            phoneme_frames.append(
                PhonemeFrame(
                    phoneme="SP",
                    duration_ms=30.0,
                    pitch_hz=0.0,
                    stress=0,
                    is_pause=True,
                )
            )
            total_time_ms += 30.0

        # Build valid SSML
        escaped_text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        ssml = (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\n'
            f'  <voice name="{voice_name}">\n'
            f'    <prosody rate="{self.default_rate}" pitch="{self.default_pitch_hz:.0f}Hz">\n'
            f'      {escaped_text}\n'
            f'    </prosody>\n'
            f'  </voice>\n'
            f'</speak>'
        )

        return TTSOutput(
            ssml=ssml,
            phoneme_stream=phoneme_frames,
            total_duration_seconds=round(total_time_ms / 1000.0, 3),
            sample_rate_hz=24000,
            audio_format="PCM_16BIT_MONO",
        )
