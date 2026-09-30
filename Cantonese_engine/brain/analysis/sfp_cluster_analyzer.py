"""
Cantonese Sentence-Final Particle (SFP) Cluster Cognitive Analyzer.
Audits pragmatic appropriateness of SFPs and clusters in colloquial Cantonese.
"""

from typing import Dict, List
from Cantonese_engine.brain.skills.sfp_engine import extract_sfps

class SfpClusterAnalyzer:
    """
    Evaluates sentence-final particles and particle sequences for pragmatic concord.
    """
    def __init__(self):
        self.name = "Cantonese SFP Cluster Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        sfps = extract_sfps(text)
        has_particles = len(sfps) > 0
        particle_chars = [p["particle"] for p in sfps]
        
        # Check cluster depth
        cluster_valid = len(sfps) <= 3
        
        # Pragmatic consistency score
        score = 1.0 if (has_particles and cluster_valid) else (0.8 if not has_particles else 0.5)
        
        return {
            "text": text,
            "has_sfps": has_particles,
            "sfp_count": len(sfps),
            "particles": particle_chars,
            "details": sfps,
            "cluster_valid": cluster_valid,
            "pragmatic_score": score
        }
