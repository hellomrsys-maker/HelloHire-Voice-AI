"""
Vietnamese Part-of-Speech Tagger
Universal Dependencies conformant tagger for Vietnamese (NOUN, VERB, ADJ, PRON, CLF, NUM, PART, ADP, CCONJ, PUNCT).
"""

from typing import List, Tuple, Dict
from Vietnamese_engine.brain.skills.tokenization import VietnameseTokenizer

VIETNAMESE_CLASSIFIERS = {"con", "cái", "quyển", "cuốn", "cây", "bức", "tờ", "ngôi", "quả", "trái", "chiếc"}
VIETNAMESE_PRONOUNS = {
    "tôi", "chúng tôi", "chúng ta", "bạn", "các bạn", "họ", "nó", "mình",
    "anh", "chị", "em", "ông", "bà", "cháu", "cô", "chú", "bác", "quý vị"
}
VIETNAMESE_PREVERBAL_TAM = {"đã", "đang", "sẽ", "vừa", "mới", "sắp", "chưa", "không", "chẳng"}
VIETNAMESE_PREPOSITIONS = {"ở", "tại", "đến", "về", "với", "cho", "của", "từ", "bằng", "trong", "trên", "dưới"}
VIETNAMESE_CONJUNCTIONS = {"và", "hoặc", "nhưng", "mà", "vì", "nên", "nếu", "thì", "tuy", "bởi vì"}
VIETNAMESE_NUMERALS = {"một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "trăm", "nghìn", "triệu"}

COMMON_VERBS = {
    "là", "có", "đi", "đến", "về", "làm", "viết", "đọc", "nói", "nghe", "thấy", "nhìn",
    "ăn", "uống", "mua", "bán", "học", "dạy", "yêu", "thích", "biết", "hiểu", "nghĩ", "sống"
}

COMMON_ADJECTIVES = {
    "tốt", "xấu", "đẹp", "lớn", "to", "nhỏ", "bé", "cao", "thấp", "dài", "ngắn",
    "mới", "cũ", "nhanh", "chậm", "khó", "dễ", "vui", "buồn", "sạch", "bẩn"
}

class VietnamesePOSTagger:
    """
    Morpho-syntactic POS tagger for Vietnamese assigning UD tags:
    NOUN, VERB, ADJ, PRON, CLF, NUM, PART, ADP, CCONJ, PUNCT.
    """

    def __init__(self):
        self.tokenizer = VietnameseTokenizer()

    def tag_word(self, word: str, prev_word: str = "", next_word: str = "") -> str:
        """Determines the POS tag of a word in context."""
        lower = word.lower()
        
        # Punctuation
        if lower in {",", ".", "?", "!", ";", ":", "«", "»", "\"", "(", ")", "—", "-"}:
            return "PUNCT"
            
        # Classifiers (Loại từ)
        if lower in VIETNAMESE_CLASSIFIERS:
            return "CLF"
            
        # Numerals
        if lower in VIETNAMESE_NUMERALS or lower.isdigit():
            return "NUM"
            
        # TAM Functional Particles
        if lower in VIETNAMESE_PREVERBAL_TAM:
            return "PART"
            
        # Prepositions
        if lower in VIETNAMESE_PREPOSITIONS:
            return "ADP"
            
        # Conjunctions
        if lower in VIETNAMESE_CONJUNCTIONS:
            return "CCONJ"
            
        # Kinship & Personal Pronouns
        # If preceding a verb or following a preposition/verb, frequently pronoun
        if lower in VIETNAMESE_PRONOUNS:
            return "PRON"
            
        # Verbs
        if lower in COMMON_VERBS:
            return "VERB"
        if prev_word.lower() in VIETNAMESE_PREVERBAL_TAM:
            return "VERB"
            
        # Adjectives
        if lower in COMMON_ADJECTIVES:
            return "ADJ"
            
        # Compound words with known semantic heads
        if " " in lower:
            first_syl = lower.split()[0]
            if first_syl in {"học", "làm", "phát", "nghiên", "giúp"}:
                return "VERB"
            if first_syl in {"bàn", "quần", "nhà", "xe", "thành", "quốc", "sinh", "giáo", "bác"}:
                return "NOUN"
                
        return "NOUN"

    def tag_sentence(self, text: str) -> List[Tuple[str, str]]:
        """Tokenizes text into words and returns (word, pos_tag) pairs."""
        words = self.tokenizer.tokenize_words(text)
        tagged = []
        for i, w in enumerate(words):
            prev_w = words[i - 1] if i > 0 else ""
            next_w = words[i + 1] if i + 1 < len(words) else ""
            pos = self.tag_word(w, prev_w, next_w)
            tagged.append((w, pos))
        return tagged
