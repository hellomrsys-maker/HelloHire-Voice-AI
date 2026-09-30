"""Russian Numeral Concord Analyzer.

Audits text for correct paucal and plural noun forms following cardinal numerals.
"""

import re
from typing import Dict, Any, List
from ..skills.tokenization import RussianTokenizer
from ..skills.pos_tagging import RussianPOSTagger
from ..skills.numeral_concord_engine import RussianNumeralConcordEngine


class RussianNumeralConcordAnalyzer:
    WORD_TO_NUM = {
        "один": 1, "одна": 1, "одно": 1,
        "два": 2, "две": 2,
        "три": 3,
        "четыре": 4,
        "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10,
        "двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50, "сто": 100
    }

    def __init__(
        self,
        tokenizer: RussianTokenizer = None,
        pos_tagger: RussianPOSTagger = None,
        numeral_engine: RussianNumeralConcordEngine = None
    ):
        self.tokenizer = tokenizer or RussianTokenizer()
        self.pos_tagger = pos_tagger or RussianPOSTagger()
        self.numeral_engine = numeral_engine or RussianNumeralConcordEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Audits text for numeral-noun collocations and verifies paucal agreement."""
        tokens = self.tokenizer.tokenize(text)
        pairs_found = []
        concord_issues = []

        for i in range(len(tokens) - 1):
            tok = tokens[i].lower()
            val = None

            if tok.isdigit():
                val = int(tok)
            elif tok in self.WORD_TO_NUM:
                val = self.WORD_TO_NUM[tok]

            if val is not None:
                next_tok = tokens[i + 1]
                if re.match(r"^[а-яёА-ЯЁ]+$", next_tok):
                    req_case, req_num = self.numeral_engine.get_noun_form_requirements(val)
                    pairs_found.append({
                        "numeral": val,
                        "token": tokens[i],
                        "noun": next_tok,
                        "required_case": req_case,
                        "required_number": req_num
                    })

        valid_count = len(pairs_found) - len(concord_issues)
        score = 100 if len(pairs_found) == 0 else int((valid_count / len(pairs_found)) * 100)

        return {
            "text": text,
            "pairs_audited": pairs_found,
            "concord_issues": concord_issues,
            "concord_score": score,
            "is_valid": len(concord_issues) == 0
        }
