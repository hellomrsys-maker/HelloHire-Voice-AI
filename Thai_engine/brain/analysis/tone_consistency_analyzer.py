"""
Thai Tone Consistency Cognitive Analyzer.
Audits orthographic tone assignments across syllables in Thai text.
"""

from typing import Dict, List
from Thai_engine.brain.skills.tone_engine import calculate_syllable_tone
from Thai_engine.brain.skills.tokenization import tokenize_thai

class ToneConsistencyAnalyzer:
    """
    Evaluates Thai words and phrases for tonal conformity.
    """
    def __init__(self):
        self.name = "Thai Tone Consistency Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        tokens = tokenize_thai(text)
        tone_profiles = []
        for t in tokens:
            if any('\u0e01' <= c <= '\u0e2e' for c in t):
                tone_profiles.append(calculate_syllable_tone(t))
                
        distinct_tones = len(set(p["tone_name"] for p in tone_profiles if p["tone_name"] != "unknown"))
        has_tones = len(tone_profiles) > 0
        
        score = 1.0 if has_tones else 0.5
        
        return {
            "text": text,
            "total_syllables": len(tone_profiles),
            "distinct_tones": distinct_tones,
            "profiles": tone_profiles,
            "is_valid": has_tones,
            "tone_score": score
        }
