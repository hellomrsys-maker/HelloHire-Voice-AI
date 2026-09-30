"""
Vietnamese Tense-Aspect-Mood (TAM) Engine
Analyzes, sequences, and validates preverbal functional TAM particles and negation.
"""

from typing import Dict, Any, List, Optional

TAM_PARTICLES = {
    "đã": {"type": "tense", "value": "past", "order": 1},
    "đang": {"type": "aspect", "value": "progressive", "order": 1},
    "sẽ": {"type": "tense", "value": "future", "order": 1},
    "vừa": {"type": "aspect", "value": "immediate_anterior", "order": 1},
    "mới": {"type": "aspect", "value": "recent_past", "order": 1},
    "sắp": {"type": "aspect", "value": "imminent_future", "order": 1},
    "không": {"type": "negation", "value": "declarative_negative", "order": 2},
    "chẳng": {"type": "negation", "value": "emphatic_negative", "order": 2},
    "chưa": {"type": "negation", "value": "experiential_negative", "order": 2}
}

class VietnameseTAMEngine:
    """
    Evaluates preverbal temporal, aspectual, and modal particles.
    """

    def analyze_verbal_cluster(self, preverbal_tokens: List[str]) -> Dict[str, Any]:
        """
        Analyzes a sequence of particles immediately preceding a verb.
        """
        tense = None
        aspect = None
        is_negative = False
        negation_type = None
        
        for tok in preverbal_tokens:
            clean = tok.lower().strip()
            if clean in TAM_PARTICLES:
                info = TAM_PARTICLES[clean]
                if info["type"] == "tense":
                    tense = info["value"]
                elif info["type"] == "aspect":
                    aspect = info["value"]
                elif info["type"] == "negation":
                    is_negative = True
                    negation_type = info["value"]

        return {
            "has_tam": bool(tense or aspect or is_negative),
            "tense": tense,
            "aspect": aspect,
            "is_negative": is_negative,
            "negation_type": negation_type
        }

    def construct_tam_predicate(
        self,
        verb: str,
        tense: Optional[str] = None,
        aspect: Optional[str] = None,
        negative: bool = False
    ) -> str:
        """
        Synthesizes a preverbal particle cluster before a lexical verb.
        (e.g., 'đang viết', 'sẽ không đi', 'chưa đọc')
        """
        particles = []
        
        # Tense / Aspect
        if tense == "past":
            particles.append("đã")
        elif tense == "future":
            particles.append("sẽ")
            
        if aspect == "progressive":
            particles.append("đang")
        elif aspect == "recent":
            particles.append("vừa")
            
        # Negation
        if negative:
            particles.append("không")
            
        particles.append(verb.strip())
        return " ".join(particles)
