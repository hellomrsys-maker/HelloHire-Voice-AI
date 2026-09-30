"""
Hindustani Oblique Concord Cognitive Analyzer.
Scans text for noun phrases preceding overt postpositions and validates
the presence of obligatory oblique inflection.
"""

from typing import Dict, Any, List, Tuple
from ..skills.tokenization import HindustaniTokenizer
from ..skills.pos_tagging import HindustaniPOSTagger
from ..skills.oblique_case_engine import ObliqueCaseEngine


class ObliqueConcordAnalyzer:
    """
    Cognitive analyzer diagnosing oblique case concordance preceding postpositions.
    """

    POSTPOSITIONS = {
        "ne", "ko", "se", "ka", "ke", "ki", "mein", "par", "tak",
        "ने", "को", "से", "का", "के", "की", "में", "पर", "तक"
    }

    def __init__(self):
        self.tokenizer = HindustaniTokenizer()
        self.tagger = HindustaniPOSTagger()
        self.oblique_engine = ObliqueCaseEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)

        violations: List[Dict[str, Any]] = []

        for i in range(len(tagged) - 1):
            w1, tag1 = tagged[i]
            w2, tag2 = tagged[i + 1]

            if tag1 in {"NOUN"} and w2.lower() in self.POSTPOSITIONS:
                # Evaluate if w1 is an uninflected marked masculine noun (e.g. ladka ne)
                eval_res = self.oblique_engine.evaluate_noun_phrase(w1, w2, gender="M", number="SG")
                if not eval_res["is_valid"]:
                    violations.append({
                        "noun": w1,
                        "postposition": w2,
                        "expected": eval_res["expected_oblique"],
                        "message": eval_res["message"]
                    })

        is_clean = len(violations) == 0

        return {
            "text": text,
            "is_valid": is_clean,
            "violation_count": len(violations),
            "violations": violations,
            "message": "Concordance oblique respectée." if is_clean else f"{len(violations)} anomalie(s) de cas oblique détectée(s)."
        }
