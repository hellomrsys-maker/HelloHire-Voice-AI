"""
Polish Verbal Aspect Engine
Analyzes Imperfective (niedokonany) vs Perfective (dokonany) verbal aspect
and pairs aspectual stems across prefixation, suffixation, and suppletion.
"""

from typing import Dict, Any, List, Optional

class PolishAspectEngine:
    def __init__(self):
        # Pair map: impf <-> pf
        self.pairs = {
            "pisać": {"pf": "napisać", "type": "prefixation (na-)"},
            "czytać": {"pf": "przeczytać", "type": "prefixation (prze-)"},
            "robić": {"pf": "zrobić", "type": "prefixation (z-)"},
            "kupować": {"pf": "kupić", "type": "suffixation"},
            "otwierać": {"pf": "otworzyć", "type": "stem alternation"},
            "zamykać": {"pf": "zamknąć", "type": "stem alternation"},
            "dawać": {"pf": "dać", "type": "stem reduction"},
            "brać": {"pf": "wziąć", "type": "suppletion"},
            "widzieć": {"pf": "zobaczyć", "type": "suppletion"},
            "mówić": {"pf": "powiedzieć", "type": "suppletion"}
        }
        # Inverted index
        self.pf_to_impf = {v["pf"]: k for k, v in self.pairs.items()}

        self.impf_forms = {
            "piszę", "piszesz", "pisze", "piszemy", "piszecie", "piszą", "pisał", "pisać",
            "czytam", "czytasz", "czyta", "czytamy", "czytacie", "czytają", "czytał", "czytać",
            "robię", "robisz", "robi", "robimy", "robicie", "robią", "robił", "robić",
            "kupuję", "kupujesz", "kupuje", "kupujemy", "kupujecie", "kupują", "kupować"
        }
        self.pf_forms = {
            "napiszę", "napiszesz", "napisze", "napiszemy", "napiszecie", "napiszą", "napisał", "napisać",
            "przeczytam", "przeczytasz", "przeczyta", "przeczytamy", "przeczytacie", "przeczytają", "przeczytał", "przeczytać",
            "zrobię", "zrobisz", "zrobi", "zrobimy", "zrobicie", "zrobią", "zrobił", "zrobić",
            "kupię", "kupisz", "kupi", "kupimy", "kupicie", "kupią", "kupił", "kupić"
        }

    def classify_aspect(self, verb: str) -> str:
        low = verb.lower().strip()
        if low in self.pf_forms or low in self.pf_to_impf:
            return "perfective"
        if low in self.impf_forms or low in self.pairs:
            return "imperfective"
        # General heuristics: common perfective prefixes
        if any(low.startswith(pfx) for pfx in ("prze", "na", "za", "wy", "od", "u", "po")) and len(low) > 5:
            return "perfective"
        return "imperfective"

    def get_aspect_pair(self, verb: str) -> Optional[Dict[str, str]]:
        low = verb.lower().strip()
        if low in self.pairs:
            return {"imperfective": low, "perfective": self.pairs[low]["pf"], "type": self.pairs[low]["type"]}
        if low in self.pf_to_impf:
            impf = self.pf_to_impf[low]
            return {"imperfective": impf, "perfective": low, "type": self.pairs[impf]["type"]}
        return None
