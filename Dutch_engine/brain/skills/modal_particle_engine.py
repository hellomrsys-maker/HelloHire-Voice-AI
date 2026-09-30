"""
Dutch Modal Particle & Pragmatic Attenuation Engine
Detects modal particles (maar, even, toch, eens, hoor, nou) and clusters,
evaluating conversational nuance and politeness attenuation.
"""

from typing import List, Dict, Any

class DutchModalParticleEngine:
    def __init__(self):
        self.particles = {
            "maar": "imperative_softener / permission",
            "even": "minimizing burden / brief duration",
            "toch": "counter-expectation / confirmation",
            "eens": "invitation / exploratory suggestion",
            "hoor": "clause-final reassurance",
            "nou": "urgency / impatience"
        }
        self.particle_clusters = [
            ("maar", "even"),
            ("toch", "maar"),
            ("toch", "eens"),
            ("toch", "maar", "eens"),
            ("nou", "eens"),
            ("maar", "eens")
        ]

    def analyze_particles(self, tokens: List[str]) -> Dict[str, Any]:
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]
        detected_particles = []
        for tok in low_tokens:
            if tok in self.particles:
                detected_particles.append({
                    "token": tok,
                    "force": self.particles[tok]
                })

        # Check clusters
        detected_clusters = []
        for cluster in self.particle_clusters:
            # Check if elements appear consecutively
            c_len = len(cluster)
            for i in range(len(low_tokens) - c_len + 1):
                if tuple(low_tokens[i:i+c_len]) == cluster:
                    detected_clusters.append(" ".join(cluster))

        return {
            "particle_count": len(detected_particles),
            "particles": detected_particles,
            "clusters": detected_clusters,
            "is_attenuated": len(detected_particles) > 0
        }
