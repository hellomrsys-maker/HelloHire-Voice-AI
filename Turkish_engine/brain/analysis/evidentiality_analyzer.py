"""Turkish Evidentiality Analyzer.

Evaluates epistemic stance, distinguishing direct sensory eyewitness knowledge (-di)
from inferential, hearsay, and mirative evidentiality (-miş).
"""

from typing import Dict, Any, List
from ..skills.tokenization import TurkishTokenizer
from ..skills.pos_tagging import TurkishPOSTagger


class TurkishEvidentialityAnalyzer:
    EVIDENTIAL_SUFFIXES = ("miş", "mış", "müş", "muş")
    DIRECT_PAST_SUFFIXES = ("di", "dı", "dü", "du", "ti", "tı", "tü", "tu")

    def __init__(
        self,
        tokenizer: TurkishTokenizer = None,
        pos_tagger: TurkishPOSTagger = None
    ):
        self.tokenizer = tokenizer or TurkishTokenizer()
        self.pos_tagger = pos_tagger or TurkishPOSTagger()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Audits verbs for evidential vs direct past markings."""
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag(tokens)

        direct_count = 0
        evidential_count = 0
        verb_details = []

        for item in tagged:
            if item["pos"] == "VERB":
                tok_low = TurkishTokenizer.turkish_lower(item["token"])
                is_evidential = any(sfx in tok_low for sfx in self.EVIDENTIAL_SUFFIXES)
                is_direct = any(sfx in tok_low for sfx in self.DIRECT_PAST_SUFFIXES) and not is_evidential

                if is_evidential:
                    evidential_count += 1
                    stance = "indirect_evidential"
                elif is_direct:
                    direct_count += 1
                    stance = "direct_eyewitness"
                else:
                    stance = "other_tam"

                verb_details.append({
                    "verb": item["token"],
                    "stance": stance
                })

        total_past = direct_count + evidential_count
        if evidential_count > direct_count:
            primary_stance = "indirect_evidential"
        elif direct_count > evidential_count:
            primary_stance = "direct_eyewitness"
        else:
            primary_stance = "neutral"

        return {
            "text": text,
            "total_verbs": len(verb_details),
            "direct_past_count": direct_count,
            "evidential_past_count": evidential_count,
            "primary_stance": primary_stance,
            "verb_details": verb_details
        }
