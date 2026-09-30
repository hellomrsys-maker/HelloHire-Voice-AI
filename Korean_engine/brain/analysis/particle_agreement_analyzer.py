"""
Korean Engine — Particle Agreement Analyzer
Validates that attached postpositions agree with preceding syllable batchim.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_eojeol
from ..skills.pos_tagging import tag_pos
from ..skills.particle_engine import validate_particle_agreement

class ParticleAgreementAnalyzer:
    """Cognitive analyzer for Korean postpositional particle (조사) concord."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_eojeol(text)
        tags = tag_pos(tokens)
        
        checked_particles = []
        violations = []
        
        for t in tags:
            if t["upos"] == "NOUN" and t.get("particle"):
                res = validate_particle_agreement(t["token"])
                checked_particles.append(res)
                if not res.get("valid", True):
                    violations.append({
                        "token": t["token"],
                        "error": res.get("error", "Particle batchim mismatch")
                    })
                    
        return {
            "token_count": len(tokens),
            "checked_count": len(checked_particles),
            "violations": violations,
            "is_valid": len(violations) == 0
        }
