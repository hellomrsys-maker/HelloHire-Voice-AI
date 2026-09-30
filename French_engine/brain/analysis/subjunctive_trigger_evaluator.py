"""
French Subjunctive Trigger Cognitive Evaluator.
Evaluates matrix clauses and subordinating conjunctions to identify semantic triggers
governing obligatory subjunctive mood selection in subordinate clauses.
"""

from typing import Dict, Any, List


class SubjunctiveTriggerEvaluator:
    """
    Evaluates semantic conditions governing French subjunctive mood selection.
    """

    TRIGGER_CATEGORIES = {
        "volition_necessity": [
            "vouloir que", "veux que", "veut que", "souhaiter que", "désirer que",
            "il faut que", "il est nécessaire que", "exiger que", "demander que"
        ],
        "emotion_sentiment": [
            "avoir peur que", "a peur que", "être content que", "est content que",
            "être triste que", "regretter que", "se réjouir que"
        ],
        "doubt_denial": [
            "douter que", "doute que", "ne pas croire que", "ne pas penser que",
            "il est douteux que", "nier que"
        ],
        "conjunctions": [
            "bien que", "quoique", "pour que", "afin que", "avant que",
            "sans que", "à condition que", "pourvu que"
        ]
    }

    def evaluate_clause(self, text: str) -> Dict[str, Any]:
        low = text.lower()
        matched_categories: List[str] = []
        found_triggers: List[str] = []

        for category, triggers in self.TRIGGER_CATEGORIES.items():
            for trig in triggers:
                if trig in low:
                    matched_categories.append(category)
                    found_triggers.append(trig)

        requires_subjunctive = len(found_triggers) > 0

        return {
            "text": text,
            "requires_subjunctive": requires_subjunctive,
            "trigger_count": len(found_triggers),
            "triggers_detected": found_triggers,
            "semantic_categories": list(set(matched_categories)),
            "message": (
                f"Déclencheur de subjonctif identifié ({', '.join(found_triggers)}). Mode subjonctif obligatoire."
                if requires_subjunctive
                else "Aucun déclencheur de subjonctif détecté (mode indicatif approprié)."
            )
        }
