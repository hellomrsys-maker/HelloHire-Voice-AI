"""
Spanish Pragmatics & Register Engine Skill.
Classifies pronominal address tiers (tuteo, voseo, ustedeo) and evaluates politeness indices.
"""

from typing import Dict, Any, List

COURTESY_MARKERS = [
    "por favor", "muchas gracias", "le agradezco", "te agradezco",
    "disculpe", "disculpa", "con su permiso", "sería tan amable", "tenga la amabilidad"
]


class SpanishPragmaticsEngine:
    """
    Evaluator for Spanish communicative registers, deference, and socio-pragmatic distance.
    """

    def evaluate_pragmatics(self, text: str) -> Dict[str, Any]:
        low = text.lower()
        clean_tokens = [w.strip("¿?¡!,.;:\"«»()") for w in low.split() if w.strip("¿?¡!,.;:\"«»()")]

        has_tuteo = any(t in {"tú", "te", "ti", "contigo", "tu", "tus", "estás", "tienes", "hablas", "comes", "quieres"} for t in clean_tokens)
        has_voseo = any(t in {"vos", "tenés", "sos", "venís", "sabés", "querés", "hablás"} for t in clean_tokens)
        has_ustedeo = any(t in {"usted", "ustedes", "su", "sus", "le", "les", "señor", "señora", "estimado", "atentamente"} for t in clean_tokens)

        detected_courtesy = [m for m in COURTESY_MARKERS if m in low]
        has_mitigation = any(v in low for v in ["podría", "querría", "quisiera", "desearía", "quería"])

        # Determine dominant tier
        if has_ustedeo:
            tier = "Ustedeo (Formal / Deference)"
            base_score = 0.85
        elif has_voseo:
            tier = "Voseo (Informal / Rioplatense)"
            base_score = 0.50
        elif has_tuteo:
            tier = "Tuteo (Informal / Standard)"
            base_score = 0.50
        else:
            tier = "Neutral / Descriptive"
            base_score = 0.60

        # Adjust score for politeness
        score = base_score + (len(detected_courtesy) * 0.08)
        if has_mitigation:
            score += 0.07
        score = min(1.0, max(0.0, score))

        return {
            "address_tier": tier,
            "is_formal": has_ustedeo or score >= 0.80,
            "politeness_score": round(score, 4),
            "detected_courtesy_markers": detected_courtesy,
            "has_pragmatic_mitigation": has_mitigation,
        }
