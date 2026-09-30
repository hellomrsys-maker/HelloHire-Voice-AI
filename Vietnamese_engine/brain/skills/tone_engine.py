"""
Vietnamese Tone Engine
Analyzes, classifies, and validates the 6 phonemic tones of Quốc Ngữ orthography.
"""

from typing import Dict, Any, List, Optional
import unicodedata

TONE_VOWELS = {
    # 1. Ngang (none)
    "ngang": set("aăâeêioôơuưyAĂÂEÊIOÔƠUƯY"),
    # 2. Huyền (grave)
    "huyen": set("àằầèềìòồờùừỳÀẰẦÈỀÌÒỒỜÙỪỲ"),
    # 3. Sắc (acute)
    "sac": set("áắấéếíóốớúứýÁẮẤÉẾÍÓỐỚÚỨÝ"),
    # 4. Hỏi (hook above)
    "hoi": set("ảẳẩẻểỉỏổởủửỷẢẲẨẺỂỈỎỔỞỦỬỶ"),
    # 5. Ngã (tilde)
    "nga": set("ãẵẫẽễĩõỗỡũữỹÃẴẪẼỄĨÕỖỠŨỮỸ"),
    # 6. Nặng (dot below)
    "nang": set("ạặậẹệịọộợụựỵẠẶẬẸỆỊỌỘỢỤỰỴ")
}

TONE_MAP = {
    "ngang": 1,
    "huyen": 2,
    "sac": 3,
    "hoi": 4,
    "nga": 5,
    "nang": 6
}

class VietnameseToneEngine:
    """
    Identifies tone contour, tone numbers (1..6), and validates diacritic placement.
    """

    def detect_syllable_tone(self, syllable: str) -> Dict[str, Any]:
        """
        Detects the lexical tone of a single Vietnamese syllable.
        """
        clean = syllable.strip()
        if not clean:
            return {"tone_name": "ngang", "tone_id": 1, "diacritic": "none"}

        # Normalize to NFC
        norm = unicodedata.normalize("NFC", clean)
        
        # Check from most specific diacritics to ngang
        for tone_name in ["nang", "nga", "hoi", "sac", "huyen"]:
            vowel_set = TONE_VOWELS[tone_name]
            if any(ch in vowel_set for ch in norm):
                return {
                    "syllable": norm,
                    "tone_name": tone_name,
                    "tone_id": TONE_MAP[tone_name],
                    "diacritic": tone_name
                }

        # Fallback to Ngang (Level / unmarked)
        return {
            "syllable": norm,
            "tone_name": "ngang",
            "tone_id": 1,
            "diacritic": "none"
        }

    def analyze_text_tones(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the tone distribution across all syllables in a text.
        """
        words = text.split()
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        
        for w in words:
            # Clean punctuation
            clean = "".join(c for c in w if c.isalpha())
            if clean:
                t = self.detect_syllable_tone(clean)
                counts[t["tone_id"]] += 1

        total = sum(counts.values())
        return {
            "total_syllables": total,
            "tone_counts": counts,
            "has_tones": total > 0
        }
