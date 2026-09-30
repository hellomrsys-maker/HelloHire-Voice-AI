"""
Thai Part-of-Speech Tagger.
Tags Thai words with Universal Dependencies (UD) labels.
"""

from typing import List, Tuple
from Thai_engine.brain.skills.tokenization import tokenize_thai

THAI_POS_LEXICON = {
    # Pronouns
    "ผม": "PRON", "ฉัน": "PRON", "เขา": "PRON", "เรา": "PRON",
    "พวกเรา": "PRON", "ท่าน": "PRON", "คุณ": "PRON", "เธอ": "PRON",
    "มัน": "PRON", "ใคร": "PRON", "อะไร": "PRON",
    
    # Classifiers
    "ตัว": "CLF", "คน": "CLF", "องค์": "CLF", "เล่ม": "CLF",
    "คัน": "CLF", "หลัง": "CLF", "ใบ": "CLF", "ชิ้น": "CLF",
    "แห่ง": "CLF", "อัน": "CLF",
    
    # Numerals
    "หนึ่ง": "NUM", "สอง": "NUM", "สาม": "NUM", "สี่": "NUM", "ห้า": "NUM",
    "หก": "NUM", "เจ็ด": "NUM", "แปด": "NUM", "เก้า": "NUM", "สิบ": "NUM",
    
    # Verbs
    "กิน": "VERB", "กินข้าว": "VERB", "ดื่ม": "VERB", "อ่าน": "VERB",
    "อ่านหนังสือ": "VERB", "เขียน": "VERB", "ดู": "VERB", "นอน": "VERB",
    "เดิน": "VERB", "ไป": "VERB", "มา": "VERB", "ซื้อ": "VERB",
    "ขาย": "VERB", "ทำ": "VERB", "ทำงาน": "VERB", "เรียน": "VERB",
    "ชอบ": "VERB", "รัก": "VERB", "มี": "VERB", "เป็น": "AUX", "อยู่": "AUX",
    "เสด็จ": "VERB", "เสวย": "VERB",
    
    # Nouns
    "ข้าว": "NOUN", "น้ำ": "NOUN", "น้ำแข็ง": "NOUN", "รถ": "NOUN",
    "รถยนต์": "NOUN", "รถไฟ": "NOUN", "หนังสือ": "NOUN", "สมุด": "NOUN",
    "บ้าน": "NOUN", "โรงเรียน": "NOUN", "มหาวิทยาลัย": "NOUN", "โรงพยาบาล": "NOUN",
    "หมา": "NOUN", "สุนัข": "NOUN", "แมว": "NOUN", "ช้าง": "NOUN",
    "อาหาร": "NOUN", "เสื้อ": "NOUN", "กางเกง": "NOUN", "โต๊ะ": "NOUN", "เก้าอี้": "NOUN",
    "ประเทศไทย": "NOUN", "ภาษาไทย": "NOUN", "เพื่อน": "NOUN", "ครู": "NOUN", "นักเรียน": "NOUN",
    
    # Adjectives
    "ดี": "ADJ", "สวย": "ADJ", "ใหญ่": "ADJ", "เล็ก": "ADJ",
    "เร็ว": "ADJ", "ช้า": "ADJ", "อร่อย": "ADJ", "แพง": "ADJ", "ร้อน": "ADJ",
    
    # Adverbs & Preverbal Auxiliaries
    "มาก": "ADV", "เสมอ": "ADV", "บ่อย": "ADV", "จริง": "ADV",
    "กำลัง": "AUX", "จะ": "AUX", "ได้": "AUX", "เคย": "AUX",
    
    # Particles
    "ครับ": "PART", "ค่ะ": "PART", "คะ": "PART", "จ๊ะ": "PART", "จ้า": "PART",
    "นะ": "PART", "แล้ว": "PART", "ไม่": "PART", "ไม่ได้": "PART"
}

def tag_pos(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Tags Thai tokens with Universal Dependencies POS tags.
    """
    tagged: List[Tuple[str, str]] = []
    
    for tok in tokens:
        if tok in THAI_POS_LEXICON:
            tagged.append((tok, THAI_POS_LEXICON[tok]))
        elif tok.isdigit():
            tagged.append((tok, "NUM"))
        elif tok.startswith("การ") or tok.startswith("ความ") or tok.startswith("ผู้") or tok.startswith("นัก"):
            tagged.append((tok, "NOUN"))
        elif tok in ["ครับ", "ค่ะ", "คะ", "จ๊ะ", "จ้า", "นะ", "ล่ะ", "เหรอ"]:
            tagged.append((tok, "PART"))
        else:
            tagged.append((tok, "NOUN"))
            
    return tagged
