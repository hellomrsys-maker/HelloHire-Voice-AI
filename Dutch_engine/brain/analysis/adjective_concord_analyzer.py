"""
Dutch Adjective Concord & Inflection Cognitive Analyzer
Validates the zero-ending rule on indefinite singular neuter nouns
(e.g., 'een mooi huis' vs *'een mooie huis').
"""

from typing import Dict, Any, List
from ..skills.tokenization import DutchTokenizer
from ..skills.gender_engine import DutchGenderEngine
from ..skills.pos_tagging import DutchPOSTagger

class DutchAdjectiveConcordAnalyzer:
    def __init__(self):
        self.tokenizer = DutchTokenizer()
        self.gender_engine = DutchGenderEngine()
        self.pos_tagger = DutchPOSTagger()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag(tokens)

        inflection_errors = []
        concord_valid = True

        # Scan for patterns: [DET] [ADJ] [NOUN] or [ADJ] [NOUN]
        for i in range(len(tagged) - 1):
            tok, tag = tagged[i]

            # Case A: DET + ADJ + NOUN
            if tag == "DET" and i + 2 < len(tagged):
                adj_tok, adj_tag = tagged[i + 1]
                noun_tok, noun_tag = tagged[i + 2]

                if adj_tag == "ADJ" and noun_tag == "NOUN":
                    res = self.gender_engine.verify_adjective_inflection(tok, adj_tok, noun_tok)
                    if not res["valid"]:
                        concord_valid = False
                        inflection_errors.append(res["error"])

            # Case B: ADJ + NOUN (no determiner preceding)
            elif tag == "ADJ":
                prev_tag = tagged[i - 1][1] if i > 0 else None
                if prev_tag != "DET":
                    noun_tok, noun_tag = tagged[i + 1]
                    if noun_tag == "NOUN":
                        res = self.gender_engine.verify_adjective_inflection(None, tok, noun_tok)
                        if not res["valid"]:
                            concord_valid = False
                            inflection_errors.append(res["error"])

        score = 100 if concord_valid else max(100 - len(inflection_errors) * 40, 20)

        return {
            "concord_valid": concord_valid,
            "adjective_concord_score": score,
            "errors": inflection_errors
        }
