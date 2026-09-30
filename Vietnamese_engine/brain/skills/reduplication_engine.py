"""
Vietnamese Reduplication (Từ Láy) Engine
Analyzes, classifies, and generates Vietnamese full and partial phonological reduplications.
"""

from typing import Dict, Any, Optional

COMMON_LAY_WORDS = {
    # Full reduplication (diminutive / attenuative)
    "xanh xanh": "lay_toan_bo",
    "trăng trắng": "lay_toan_bo",
    "nhè nhẹ": "lay_toan_bo",
    "đo đỏ": "lay_toan_bo",
    "nho nhỏ": "lay_toan_bo",
    # Alliterative / Láy âm đầu
    "đẹp đẽ": "lay_am_dau",
    "sạch sẽ": "lay_am_dau",
    "mạnh mẽ": "lay_am_dau",
    "lung linh": "lay_am_dau",
    "vui vẻ": "lay_am_dau",
    "buồn bã": "lay_am_dau",
    # Rhyming / Láy vần
    "lác đác": "lay_van",
    "bối rối": "lay_van",
    "lúng túng": "lay_van",
    "khéo léo": "lay_van"
}

class VietnameseReduplicationEngine:
    """
    Classifies phonological reduplications into:
    - Full reduplication (Láy toàn bộ)
    - Alliteration / Initial rhyme (Láy âm đầu)
    - Rhyme / Final vowel rhyme (Láy vần)
    """

    def classify_reduplication(self, two_syllables: str) -> Dict[str, Any]:
        """Classifies a two-syllable phrase into its reduplication type."""
        clean = two_syllables.lower().strip()
        
        # Direct lookup
        if clean in COMMON_LAY_WORDS:
            return {
                "phrase": clean,
                "is_reduplication": True,
                "type": COMMON_LAY_WORDS[clean]
            }

        parts = clean.split()
        if len(parts) != 2:
            return {"phrase": clean, "is_reduplication": False, "type": "none"}

        s1, s2 = parts[0], parts[1]
        
        # Check identical (full)
        if s1 == s2:
            return {"phrase": clean, "is_reduplication": True, "type": "lay_toan_bo"}
            
        # Check initial consonant match (láy âm đầu)
        if s1[0] == s2[0] and s1[0].isalpha():
            return {"phrase": clean, "is_reduplication": True, "type": "lay_am_dau"}
            
        return {"phrase": clean, "is_reduplication": False, "type": "none"}
