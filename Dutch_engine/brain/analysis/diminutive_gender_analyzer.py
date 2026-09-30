"""
Dutch Diminutive & Grammatical Gender Cognitive Analyzer
Validates noun gender agreement and verifies the diminutive neuter invariant.
"""

from typing import Dict, Any, List
from ..skills.tokenization import DutchTokenizer
from ..skills.diminutive_engine import DutchDiminutiveEngine
from ..skills.gender_engine import DutchGenderEngine

class DutchDiminutiveGenderAnalyzer:
    def __init__(self):
        self.tokenizer = DutchTokenizer()
        self.diminutive_engine = DutchDiminutiveEngine()
        self.gender_engine = DutchGenderEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        diminutives_found = []
        gender_errors = []
        concord_valid = True

        for i, tok in enumerate(tokens):
            tok_low = tok.lower()
            if self.diminutive_engine.is_diminutive(tok_low):
                diminutives_found.append(tok)

            # Look for article + noun pairs
            if tok_low in {"de", "het", "'t", "een", "geen", "dit", "dat", "deze", "die"} and i + 1 < len(tokens):
                # Next token might be an adjective, skip if adjective
                target_idx = i + 1
                if target_idx < len(tokens) and tokens[target_idx].lower() in self.gender_engine.het_nouns.union(self.gender_engine.de_nouns):
                    noun = tokens[target_idx]
                elif target_idx + 1 < len(tokens) and tokens[target_idx + 1].lower() in self.gender_engine.het_nouns.union(self.gender_engine.de_nouns):
                    noun = tokens[target_idx + 1]
                elif target_idx < len(tokens) and self.diminutive_engine.is_diminutive(tokens[target_idx]):
                    noun = tokens[target_idx]
                elif target_idx + 1 < len(tokens) and self.diminutive_engine.is_diminutive(tokens[target_idx + 1]):
                    noun = tokens[target_idx + 1]
                else:
                    noun = None

                if noun:
                    # Check diminutive concord
                    if self.diminutive_engine.is_diminutive(noun):
                        res = self.diminutive_engine.verify_diminutive_concord(tok_low, noun)
                        if not res["valid"]:
                            concord_valid = False
                            gender_errors.append(res["error"])
                    else:
                        res = self.gender_engine.verify_article_noun(tok_low, noun)
                        if not res["valid"]:
                            concord_valid = False
                            gender_errors.append(res["error"])

        score = 100 if concord_valid else max(100 - len(gender_errors) * 35, 20)

        return {
            "diminutives_found": diminutives_found,
            "diminutive_count": len(diminutives_found),
            "concord_valid": concord_valid,
            "gender_errors": gender_errors,
            "gender_score": score
        }
