"""
Spanish Subjunctive Mood Evaluator.
Assesses matrix clause triggers (WEIRDOS) and verifies modal harmony in subordinate clauses.
"""

from typing import Dict, Any, List
from ..skills.tokenization import SpanishTokenizer
from ..skills.parsing import SpanishParser

SUBJUNCTIVE_MARKERS = [
    "quiero que", "quiere que", "deseo que", "espero que", "ojalá",
    "dudo que", "no creo que", "es necesario que", "es importante que",
    "recomiendo que", "sugiero que", "para que", "sin que", "antes de que"
]

SUBJUNCTIVE_VERB_FORMS = {
    "hable", "hables", "hablemos", "habléis", "hablen",
    "coma", "comas", "comamos", "comáis", "coman",
    "viva", "vivas", "vivamos", "viváis", "vivan",
    "sea", "seas", "seamos", "seáis", "sean",
    "esté", "estés", "estemos", "estéis", "estén",
    "vaya", "vayas", "vayamos", "vayáis", "vayan",
    "tenga", "tengas", "tengamos", "tengáis", "tengan",
    "haga", "hagas", "hagamos", "hagáis", "hagan",
    "sepa", "sepas", "sepamos", "sepáis", "sepan",
    "pueda", "puedas", "podamos", "podáis", "puedan",
}


class SubjunctiveEvaluator:
    """
    Cognitive evaluator for epistemic, volitional, and emotional modal governance.
    """

    def __init__(self):
        self.tokenizer = SpanishTokenizer()
        self.parser = SpanishParser()

    def evaluate_clause(self, text: str) -> Dict[str, Any]:
        low = text.lower()
        tokens = self.tokenizer.segment(text)

        matched_triggers = [trig for trig in SUBJUNCTIVE_MARKERS if trig in low]
        requires_subjunctive = len(matched_triggers) > 0

        detected_subjunctives = [tok.lower() for tok in tokens if tok.lower() in SUBJUNCTIVE_VERB_FORMS]
        has_subjunctive_verb = len(detected_subjunctives) > 0

        is_harmonious = True
        if requires_subjunctive and not has_subjunctive_verb:
            is_harmonious = False

        return {
            "requires_subjunctive": requires_subjunctive,
            "detected_triggers": matched_triggers,
            "has_subjunctive_verb": has_subjunctive_verb,
            "detected_subjunctive_verbs": detected_subjunctives,
            "modal_harmony": is_harmonious,
        }
