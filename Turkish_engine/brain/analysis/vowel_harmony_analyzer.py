"""Turkish Vowel Harmony Analyzer.

Audits running text for vowel harmony compliance, detects vocalic disharmony,
and evaluates overall phonological coherence.
"""

from typing import Dict, Any, List
from ..skills.tokenization import TurkishTokenizer
from ..skills.vowel_harmony_engine import TurkishVowelHarmonyEngine


class TurkishVowelHarmonyAnalyzer:
    # Common loanwords and compound words that inherently contain both front and back vowels
    PERMISSIBLE_DISHARMONIC_LOANS = {
        "kitap", "kitab", "kalem", "otobüs", "istasyon", "gazete", "dünya", "zaman",
        "insan", "dakika", "ziyaret", "merhaba", "profesör", "teknoloji", "dikkat",
        "kütüphane", "öğrenci", "üniversite", "mühendis", "edebiyat", "hastane",
        "eczane", "postane", "mimar", "cumhuriyet", "bina", "telefon", "bilgisayar",
        "rapor", "müdür", "taraf", "meslek", "proje", "program", "sistem"
    }

    def __init__(
        self,
        tokenizer: TurkishTokenizer = None,
        harmony_engine: TurkishVowelHarmonyEngine = None
    ):
        self.tokenizer = tokenizer or TurkishTokenizer()
        self.harmony = harmony_engine or TurkishVowelHarmonyEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Audits all words in text for internal vowel harmony."""
        tokens = self.tokenizer.tokenize(text)
        audited_words = []
        violations = []

        for tok in tokens:
            if not tok.isalpha():
                continue

            stem, _ = self.tokenizer.split_apostrophe(tok)
            stem_low = TurkishTokenizer.turkish_lower(stem)
            canon_stem = stem_low.replace("b", "p").replace("c", "ç").replace("d", "t").replace("ğ", "k")

            res = self.harmony.check_internal_harmony(stem)
            is_loan_exception = (
                stem_low in self.PERMISSIBLE_DISHARMONIC_LOANS
                or any(stem_low.startswith(loan) for loan in self.PERMISSIBLE_DISHARMONIC_LOANS)
                or any(canon_stem.startswith(loan) for loan in self.PERMISSIBLE_DISHARMONIC_LOANS)
            )



            if not res["is_harmonic"] and not is_loan_exception:
                violations.append({
                    "word": tok,
                    "stem": stem,
                    "issue": "vowel_harmony_clash",
                    "severity": "warning"
                })

            audited_words.append({
                "token": tok,
                "is_harmonic": res["is_harmonic"] or is_loan_exception,
                "vowel_count": res["vowel_count"]
            })

        total_words = len(audited_words)
        harmonic_words = total_words - len(violations)
        compliance_score = 100 if total_words == 0 else int((harmonic_words / total_words) * 100)

        return {
            "text": text,
            "total_words": total_words,
            "harmonic_words": harmonic_words,
            "compliance_score": compliance_score,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
