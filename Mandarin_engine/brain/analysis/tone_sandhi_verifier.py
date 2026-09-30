"""
Mandarin Tone Sandhi Verifier.
Validates 3rd tone sandhi and 一/不 sandhi execution.
"""

from typing import Dict, Any
from ..skills.pinyin_tone import PinyinToneEngine


class ToneSandhiVerifier:
    """
    Validates phonological tone sandhi application.
    """

    def __init__(self):
        self.engine = PinyinToneEngine()

    def verify_sandhi(self, text: str) -> Dict[str, Any]:
        raw = self.engine.hanzi_to_raw_pinyin(text)
        sandhi = self.engine.apply_tone_sandhi(raw)

        sandhi_events = []
        for i in range(len(raw)):
            if raw[i][2] != sandhi[i][2] and raw[i][2] != -1:
                sandhi_events.append({
                    "char": raw[i][0],
                    "original_tone": raw[i][2],
                    "surface_tone": sandhi[i][2],
                    "pinyin": self.engine.format_with_diacritics(sandhi[i][1], sandhi[i][2]),
                })

        return {
            "has_sandhi": len(sandhi_events) > 0,
            "sandhi_count": len(sandhi_events),
            "events": sandhi_events,
            "surface_pinyin": self.engine.text_to_pinyin_string(text, apply_sandhi=True),
        }
