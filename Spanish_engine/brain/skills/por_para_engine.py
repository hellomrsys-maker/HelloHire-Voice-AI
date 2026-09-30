"""
Por vs Para Verification & Disambiguation Skill.
Validates prepositional selection based on causal vs teleological domains.
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "por_para_rules.json")


class PorParaEngine:
    """
    Evaluates prepositional harmony for 'por' and 'para'.
    """

    def __init__(self, rules_path: Optional[str] = None):
        target = rules_path or RULES_PATH
        self.rules: Dict[str, Any] = {}
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                self.rules = json.load(f)

    def evaluate_preposition(self, preposition: str, context_phrase: str) -> Dict[str, Any]:
        """
        Validates whether 'por' or 'para' fits the following context phrase.
        """
        prep = preposition.lower().strip()
        ctx = context_phrase.lower().strip()

        # Para triggers
        # Purpose with infinitive (para + verb ending in ar/er/ir)
        is_infinitive = any(ctx.startswith(v) for v in ["estudiar", "hacer", "trabajar", "aprender", "aprobar", "ir", "comprar"]) or (len(ctx.split()) > 0 and ctx.split()[0].endswith(("ar", "er", "ir")))
        # Recipient (para ti, para mí, para Juan)
        is_recipient = any(ctx.startswith(p) for p in ["ti", "mí", "usted", "él", "ella", "nosotros", "juan", "maría", "los"])
        # Deadline (para el lunes, para mañana)
        is_deadline = any(ctx.startswith(d) for d in ["el lunes", "el martes", "el viernes", "mañana", "la próxima semana"])

        # Por triggers
        # Cause / reason (por la lluvia, por culpa de, por favor, por eso)
        is_cause = any(ctx.startswith(c) for c in ["la lluvia", "culpa", "eso", "accidente", "enfermedad", "miedo"])
        # Gratitude (gracias por)
        is_thanks = "gracias" in ctx or "agradezco" in ctx
        # Duration (por dos horas, por mucho tiempo)
        is_duration = any(ctx.startswith(d) for d in ["dos horas", "tres años", "un mes", "mucho tiempo", "siempre"])
        # Means (por teléfono, por correo)
        is_means = any(ctx.startswith(m) for m in ["teléfono", "correo", "avión", "internet"])

        recommended = prep
        category = "general"

        if is_infinitive or is_recipient or is_deadline:
            recommended = "para"
            category = "finalidad_o_destinatario" if (is_infinitive or is_recipient) else "fecha_limite"
        elif is_cause or is_thanks or is_duration or is_means:
            recommended = "por"
            category = "causa_o_medio" if (is_cause or is_means) else "duracion_o_agradecimiento"

        is_valid = (prep == recommended) or (prep in {"por", "para"} and recommended == prep)

        return {
            "selected_preposition": prep,
            "recommended_preposition": recommended,
            "context": context_phrase,
            "category": category,
            "is_valid": is_valid,
        }
