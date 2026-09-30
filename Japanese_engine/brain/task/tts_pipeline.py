"""
Japanese Text-to-Speech (TTS) Front-End and SSML Synthesis Pipeline
===================================================================
Transforms Japanese orthography (Kanji/Kana) into phonetic mora streams with
pitch accent contours (Tokyo standard), duration modeling, and SSML generation.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.g2p import JapaneseG2PConverter


@dataclass
class JapaneseMoraFrame:
    mora: str
    duration_ms: float
    pitch_hz: float
    is_high_pitch: bool
    is_pause: bool = False


@dataclass
class JapaneseTTSOutput:
    ssml: str
    mora_stream: List[JapaneseMoraFrame]
    total_duration_seconds: float
    sample_rate_hz: int
    audio_format: str
    pitch_pattern: str


class JapaneseTTSPipeline:
    """
    TTS front-end converter generating pitch-accented mora frames and SSML.
    """

    def __init__(self, base_pitch_hz: float = 135.0, default_mora_ms: float = 130.0) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.g2p = JapaneseG2PConverter()
        self.base_pitch_hz = base_pitch_hz
        self.default_mora_ms = default_mora_ms

    def synthesize_stream(self, text: str, voice_name: str = "ja-JP-Standard-A") -> JapaneseTTSOutput:
        g2p_res = self.g2p.convert(text)
        moras = g2p_res.phonetic_moras
        accent = g2p_res.pitch_accent_type

        frames: List[JapaneseMoraFrame] = []
        n_moras = len(moras)

        # Apply Tokyo pitch accent contour
        for i, m in enumerate(moras):
            if m in {"。", "、", " ", "　"}:
                frames.append(
                    JapaneseMoraFrame(
                        mora="SIL",
                        duration_ms=250.0 if m == "。" else 120.0,
                        pitch_hz=0.0,
                        is_high_pitch=False,
                        is_pause=True,
                    )
                )
                continue

            # Determine high/low pitch according to accent type
            is_high = False
            if accent == "Atamadaka (頭高)":
                is_high = (i == 0)
            elif accent == "Nakadaka (中高)":
                is_high = (0 < i < n_moras - 1)
            elif accent == "Odaka (尾高)":
                is_high = (i > 0)
            else:  # Heiban (平板)
                is_high = (i > 0)

            # Pitch frequency
            f0 = self.base_pitch_hz * (1.30 if is_high else 0.95)

            # Duration adjustments (Sokuon っ is shorter, Chōon ー is longer)
            dur = self.default_mora_ms
            if m in {"っ", "ッ"}:
                dur = self.default_mora_ms * 0.75
            elif m in {"ー"}:
                dur = self.default_mora_ms * 1.25

            frames.append(
                JapaneseMoraFrame(
                    mora=m,
                    duration_ms=round(dur, 1),
                    pitch_hz=round(f0, 1),
                    is_high_pitch=is_high,
                    is_pause=False,
                )
            )

        total_ms = sum(f.duration_ms for f in frames)

        # Generate SSML
        ssml = (
            f'<speak><voice name="{voice_name}">'
            f'<phoneme alphabet="x-kana" ph="{g2p_res.hiragana_reading}">{text}</phoneme>'
            f'</voice></speak>'
        )

        return JapaneseTTSOutput(
            ssml=ssml,
            mora_stream=frames,
            total_duration_seconds=round(total_ms / 1000.0, 3),
            sample_rate_hz=24000,
            audio_format="LINEAR_PCM_16BIT",
            pitch_pattern=accent,
        )
