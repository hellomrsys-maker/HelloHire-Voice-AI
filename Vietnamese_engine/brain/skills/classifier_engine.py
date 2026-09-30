"""
Vietnamese Numeral Classifier Engine
Validates, selects, and attaches classifiers (Loại từ) to head nouns.
"""

from typing import Dict, Any, List, Optional

NOUN_CLASSIFIER_MAP = {
    # Animals & active/moving
    "chó": "con", "mèo": "con", "cá": "con", "chim": "con", "gà": "con",
    "bò": "con", "ngựa": "con", "dao": "con", "đường": "con", "sông": "con",
    # Inanimate artifacts
    "bàn": "cái", "ghế": "cái", "áo": "cái", "xe": "cái", "cửa": "cái", "máy": "cái",
    # Books / bound volumes
    "sách": "cuốn", "tiểu thuyết": "cuốn", "từ điển": "quyển", "vở": "quyển", "sổ": "cuốn",
    # Elongated / plants
    "bút": "cây", "cầu": "cây", "tre": "cây", "chuối": "cây", "cột": "cây",
    # Vertical art / letters
    "tranh": "bức", "ảnh": "bức", "thư": "bức", "tường": "bức",
    # Thin flexible sheets
    "báo": "tờ", "giấy": "tờ", "tiền": "tờ", "vé": "tờ",
    # Structures
    "nhà": "ngôi", "chùa": "ngôi", "trường": "ngôi", "sao": "ngôi",
    # Humans
    "bạn": "người", "giáo viên": "người", "bác sĩ": "người", "phụ nữ": "người",
    # Fruits / round
    "táo": "quả", "cam": "quả", "bóng": "quả"
}

class VietnameseClassifierEngine:
    """
    Selects, validates, and inserts classifiers for Vietnamese nominal quantification.
    """

    def get_preferred_classifier(self, noun: str) -> str:
        """Returns the canonical classifier for a given noun."""
        clean = noun.lower().strip()
        return NOUN_CLASSIFIER_MAP.get(clean, "cái")

    def validate_classifier_noun_pair(self, classifier: str, noun: str) -> bool:
        """Checks whether a classifier is semantically compatible with a noun."""
        clean_clf = classifier.lower().strip()
        clean_n = noun.lower().strip()
        
        # Exact map match
        preferred = NOUN_CLASSIFIER_MAP.get(clean_n)
        if preferred == clean_clf:
            return True
            
        # Flexible alternatives
        if clean_n in {"sách", "tiểu thuyết"} and clean_clf in {"cuốn", "quyển"}:
            return True
        if clean_n in {"táo", "cam", "bóng"} and clean_clf in {"quả", "trái"}:
            return True
        if clean_n in {"nhà"} and clean_clf in {"ngôi", "cái"}:
            return True
            
        return False

    def construct_quantified_np(self, number: str, noun: str, classifier: Optional[str] = None) -> str:
        """
        Synthesizes a quantified noun phrase:
        [Number] + [Classifier] + [Noun]
        (e.g., 'hai' + 'con' + 'chó' = 'hai con chó')
        """
        clf = classifier if classifier else self.get_preferred_classifier(noun)
        return f"{number.strip()} {clf} {noun.strip()}"
