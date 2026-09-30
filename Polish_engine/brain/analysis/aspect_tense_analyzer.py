"""
Polish Verbal Aspect Cognitive Analyzer
Analyzes distribution of Imperfective vs Perfective verbs.
"""

from typing import Dict, Any, List
from ..skills.tokenization import PolishTokenizer
from ..skills.pos_tagging import PolishPOSTagger
from ..skills.aspect_engine import PolishAspectEngine

class PolishAspectTenseAnalyzer:
    def __init__(self):
        self.tokenizer = PolishTokenizer()
        self.tagger = PolishPOSTagger()
        self.aspect_engine = PolishAspectEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)

        impf_verbs = []
        pf_verbs = []

        for tok, tag in tagged:
            if tag in {"VERB", "AUX"} and tok.lower() not in {"jest", "są", "był", "była", "było", "będzie"}:
                asp = self.aspect_engine.classify_aspect(tok)
                if asp == "perfective":
                    pf_verbs.append(tok)
                else:
                    impf_verbs.append(tok)

        total = len(impf_verbs) + len(pf_verbs)
        # Dominant aspect code: 0=mixed/none, 1=imperfective, 2=perfective
        if len(pf_verbs) > len(impf_verbs):
            dominant_code = 2
            dominant_str = "perfective"
        elif len(impf_verbs) > len(pf_verbs):
            dominant_code = 1
            dominant_str = "imperfective"
        else:
            dominant_code = 0
            dominant_str = "neutral_balanced"

        return {
            "total_verbs": total,
            "imperfective_verbs": impf_verbs,
            "perfective_verbs": pf_verbs,
            "dominant_aspect": dominant_str,
            "aspect_code": dominant_code
        }
