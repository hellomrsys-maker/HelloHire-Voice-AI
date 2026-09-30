"""
Korean Engine — Speech Level Analyzer
Audits speech level consistency and flags register clashing across sentence terminals.
"""

from typing import Dict, Any, List
from ..skills.tokenization import split_sentences
from ..skills.speech_level_engine import classify_speech_level, audit_speech_level_consistency

class SpeechLevelAnalyzer:
    """Cognitive analyzer for speech level consistency (상대높임법)."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        sentence_details = []
        for s in sentences:
            sl = classify_speech_level(s)
            sentence_details.append({
                "sentence": s,
                "level": sl["level"],
                "ending": sl["ending"]
            })
            
        audit = audit_speech_level_consistency(sentences)
        
        return {
            "sentence_count": len(sentences),
            "sentence_details": sentence_details,
            "levels_detected": audit["levels_detected"],
            "primary_level": audit["primary_level"],
            "is_clash": audit["is_clash"],
            "is_consistent": audit["is_consistent"]
        }
