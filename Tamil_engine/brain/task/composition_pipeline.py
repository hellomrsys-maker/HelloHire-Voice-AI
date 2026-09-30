"""
Tamil Composition Task Pipeline.
Synthesizes creative, expressive Tamil prose enriched with Sangam motifs,
Tirukkuṟaḷ ideals, and authentic proverbs (பழமொழி).
"""

from typing import Dict, List, Optional
from Tamil_engine.brain.skills.generation import generate_sov_sentence

TAMIL_PROVERBS = {
    "அறிவு": "கற்றது கைமண் அளவு, கல்லாதது உலகளவு (Avvaiyār).",
    "உழைப்பு": "சுவர் இருந்தால் தான் சித்திரம் வரைய முடியும்.",
    "அன்பு": "அகத்தின் அழகு முகத்தில் தெரியும்.",
    "முயற்சி": "ஆழம் தெரியாமல் காலை விடாதே."
}

class TamilCompositionPipeline:
    """
    Prose and creative composition synthesizer for Tamil.
    """
    def __init__(self):
        self.name = "Tamil Composition Pipeline"

    def compose_narrative(self, theme: str = "அறிவு", include_proverb: bool = True) -> Dict[str, any]:
        lines = [
            generate_sov_sentence("மாணவன்", "படித்தான்", object_noun="புத்தகம்"),
            generate_sov_sentence("ஆசிரியர்", "கற்பித்தார்", object_noun="தமிழ்"),
            generate_sov_sentence("நாங்கள்", "புரிந்துகொண்டோம்", object_noun="பாடம்")
        ]
        
        proverb_used = None
        if include_proverb and theme in TAMIL_PROVERBS:
            proverb_used = TAMIL_PROVERBS[theme]
            lines.append(f"பழமொழி கூறுவது போல, {proverb_used}")
            
        full_text = "\n".join(lines)
        
        return {
            "theme": theme,
            "prose": full_text,
            "proverb_used": proverb_used,
            "line_count": len(lines)
        }
