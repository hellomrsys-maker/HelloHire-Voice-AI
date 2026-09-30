"""
Cantonese Composition Task Pipeline.
Synthesizes creative, expressive Cantonese prose enriched with idioms (成語 / 俗語),
Xiehouyu (歇後語), and authentic aspect markers.
"""

from typing import Dict, List, Optional
from Cantonese_engine.brain.skills.generation import generate_cantonese_sentence

CANTONESE_IDIOMS = {
    "飲茶": "飲茶食點心，歎一盅兩件 (yum cha / dim sum cultural tradition)",
    "炒魷魚": "俾老細炒魷魚 (to get fired / terminated from a job)",
    "放飛機": "次次都放飛機唔見人 (to stand someone up / flake on an appointment)",
    "食死貓": "無辜俾人冤枉食死貓 (to take the blame for someone else's mistake)",
    "生骨大頭菜": "種極都唔大 (Xiehouyu: like hard-headed turnips - never grows up)"
}

class CantoneseCompositionPipeline:
    """
    Prose and creative composition synthesizer for Cantonese.
    """
    def __init__(self):
        self.name = "Cantonese Composition Pipeline"

    def compose_narrative(self, topic: str, include_idiom: bool = True) -> Dict[str, any]:
        narrative_lines = [
            generate_cantonese_sentence("我哋", "去", "茶餐廳", aspect="緊", sfp="呀。"),
            generate_cantonese_sentence("老細", "畀", theme_object="份菜單", recipient_io="我哋", aspect="咗", sfp="喇。"),
            generate_cantonese_sentence("大家", "行", aspect=None, adverb="先", sfp="啦！")
        ]
        
        idiom_used = None
        if include_idiom:
            idiom_used = "飲茶"
            narrative_lines.append(f"今朝早同朋友一齊去{idiom_used}，真正歎世界。")
            
        full_text = "\n".join(narrative_lines)
        
        return {
            "topic": topic,
            "prose": full_text,
            "idiom_used": idiom_used,
            "line_count": len(narrative_lines)
        }
