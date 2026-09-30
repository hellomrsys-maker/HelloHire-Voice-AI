"""
Japanese Speech-to-Text (STT) Pipeline
======================================
Decodes phonetic mora streams and kana sequences into canonical Japanese orthography
(Kanji/Kana) with context-aware homophone disambiguation and boundary detection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.stt_decoder import JapaneseSTTDecoder, JapaneseSTTDecodeResult
from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer


@dataclass
class JapaneseSTTResult:
    hypothesized_text: str
    raw_kana_input: str
    confidence: float
    segments: List[Dict[str, Any]]
    alternative_hypotheses: List[str] = field(default_factory=list)


class JapaneseSTTPipeline:
    """
    Japanese Speech-to-Text front-end decoding kana to canonical orthography.
    """

    def __init__(self) -> None:
        self.decoder = JapaneseSTTDecoder()
        self.tokenizer = JapaneseTokenizer()

    def decode_kana(self, kana_text: str, context: Optional[str] = None) -> JapaneseSTTResult:
        decode_res = self.decoder.decode_mora_stream(kana_text, context_words=[context] if context else None)
        tokens = self.tokenizer.tokenize(decode_res.decoded_text)

        segments = [
            {"token": t.text, "script": t.script, "start": t.char_start, "end": t.char_end}
            for t in tokens
        ]

        return JapaneseSTTResult(
            hypothesized_text=decode_res.decoded_text,
            raw_kana_input=kana_text,
            confidence=decode_res.confidence,
            segments=segments,
            alternative_hypotheses=decode_res.alternatives,
        )
