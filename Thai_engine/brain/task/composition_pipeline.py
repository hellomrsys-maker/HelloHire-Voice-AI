"""
Thai Composition Task Pipeline.
Synthesizes creative, expressive Thai prose with classifiers, proverbs (สุภาษิต),
and polite registers.
"""

from typing import Dict, List, Optional
from Thai_engine.brain.skills.generation import generate_thai_sentence

THAI_PROVERBS = {
    "โอกาส": "น้ำขึ้นให้รีบตัก (Strike while the iron is hot).",
    "ความจริง": "ช้างตายทั้งตัวเอาใบบัวมาปิด (You cannot hide a dead elephant with a lotus leaf).",
    "การปรับตัว": "เข้าเมืองตาหลิ่ว ต้องหลิ่วตาตาม (When in Rome, do as the Romans do).",
    "ความสงบ": "ใจเย็น ๆ (Keep your heart cool and calm)."
}

class ThaiCompositionPipeline:
    """
    Prose and creative composition synthesizer for Thai.
    """
    def __init__(self):
        self.name = "Thai Composition Pipeline"

    def compose_narrative(self, theme: str = "โอกาส", include_proverb: bool = True) -> Dict[str, any]:
        lines = [
            generate_thai_sentence("ผม", "อ่าน", object_noun="หนังสือ", numeral="สอง", polite_particle="ครับ"),
            generate_thai_sentence("เขา", "ซื้อ", object_noun="รถยนต์", numeral="หนึ่ง", polite_particle="ครับ"),
            generate_thai_sentence("เรา", "ไป", object_noun="โรงเรียน", polite_particle="ครับ")
        ]
        
        proverb_used = None
        if include_proverb and theme in THAI_PROVERBS:
            proverb_used = THAI_PROVERBS[theme]
            lines.append(f"สุภาษิตไทยกล่าวว่า {proverb_used}")
            
        full_text = "\n".join(lines)
        
        return {
            "theme": theme,
            "prose": full_text,
            "proverb_used": proverb_used,
            "line_count": len(lines)
        }
