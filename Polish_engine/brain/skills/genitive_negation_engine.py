"""
Polish Genitive of Negation Engine (Dopełniacz Negacji)
Enforces the mandatory shift of direct objects from Accusative to Genitive
under verbal negation ('nie' + transitive verb).
"""

from typing import Dict, Any, List, Optional, Tuple

class PolishGenitiveNegationEngine:
    def __init__(self):
        # Pairs of (Accusative, Genitive) for common nouns
        # Maps lemma -> { "acc": form, "gen": form }
        self.noun_forms = {
            "czas": {"acc": "czas", "gen": "czasu"},
            "książka": {"acc": "książkę", "gen": "książki"},
            "chleb": {"acc": "chleb", "gen": "chleba"},
            "samochód": {"acc": "samochód", "gen": "samochodu"},
            "woda": {"acc": "wodę", "gen": "wody"},
            "kawa": {"acc": "kawę", "gen": "kawy"},
            "problem": {"acc": "problem", "gen": "problemu"},
            "pytanie": {"acc": "pytanie", "gen": "pytania"},
            "odpowiedź": {"acc": "odpowiedź", "gen": "odpowiedzi"},
            "cukier": {"acc": "cukier", "gen": "cukru"},
            "mleko": {"acc": "mleko", "gen": "mleka"},
            "herbata": {"acc": "herbatę", "gen": "herbaty"},
            "pieniądze": {"acc": "pieniądze", "gen": "pieniędzy"},
            "praca": {"acc": "pracę", "gen": "pracy"},
            "dom": {"acc": "dom", "gen": "domu"},
            "list": {"acc": "list", "gen": "listu"},
            "raport": {"acc": "raport", "gen": "raportu"}
        }
        # Inverted index: word -> (case, lemma)
        self.word_to_case = {}
        for lemma, forms in self.noun_forms.items():
            acc = forms["acc"].lower()
            gen = forms["gen"].lower()
            if acc != gen:
                self.word_to_case[acc] = ("ACC", lemma)
                self.word_to_case[gen] = ("GEN", lemma)

        self.transitive_verbs = {
            "mam", "masz", "ma", "mamy", "macie", "mają", "miał", "miała",
            "czytam", "czytasz", "czyta", "czytamy", "czytacie", "czytają",
            "kupuję", "kupujesz", "kupuje", "kupujemy", "kupujecie", "kupują",
            "widzę", "widzisz", "widzi", "widzimy", "widzicie", "widzą",
            "robię", "robisz", "robi", "robimy", "robicie", "robią",
            "lubię", "lubisz", "lubi", "lubimy", "lubicie", "lubią",
            "znam", "znasz", "zna", "znamy", "znacie", "znają",
            "piję", "pijesz", "pije", "pijemy", "pijecie", "piją",
            "jem", "jesz", "je", "jemy", "jecie", "jedzą",
            "piszę", "piszesz", "pisze", "piszemy", "piszecie", "piszą",
            "rozumiem", "rozumiesz", "rozumie", "rozumiemy", "rozumieją"
        }

    def verify_sentence(self, tokens: List[str]) -> Dict[str, Any]:
        low_tokens = [t.lower() for t in tokens if t not in {".", ",", "!", "?", ";", ":"}]

        # Check if sentence is negated
        is_negated = False
        neg_verb_idx = -1

        for i in range(len(low_tokens) - 1):
            if low_tokens[i] == "nie" and low_tokens[i + 1] in self.transitive_verbs:
                is_negated = True
                neg_verb_idx = i + 1
                break

        if not is_negated:
            return {
                "is_negated": False,
                "genitive_of_negation_valid": True,
                "errors": []
            }

        # Under negation, scan tokens following the verb for direct object
        errors = []
        genitive_verified = False

        for tok in low_tokens[neg_verb_idx + 1:]:
            if tok in self.word_to_case:
                case, lemma = self.word_to_case[tok]
                if case == "ACC":
                    # Accusative found under negation -> Violation!
                    expected_gen = self.noun_forms[lemma]["gen"]
                    errors.append(
                        f"Genitive of Negation Violation: Transitive verb negated with 'nie' requires direct object "
                        f"in Genitive ('{expected_gen}'), but found Accusative ('{tok}')."
                    )
                elif case == "GEN":
                    genitive_verified = True

        valid = len(errors) == 0
        return {
            "is_negated": True,
            "genitive_of_negation_valid": valid,
            "genitive_verified": genitive_verified,
            "errors": errors
        }
