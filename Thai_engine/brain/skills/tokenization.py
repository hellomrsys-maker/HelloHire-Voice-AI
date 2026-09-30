"""
Thai Tokenization Engine.
Performs scriptio continua lexical word segmentation using maximal matching
over a comprehensive Thai lexicon.
"""

from typing import List

THAI_LEXICON = {
    # Conjunctions & Prepositions
    "และ": True, "หรือ": True, "แต่": True, "กับ": True, "ที่": True, "ใน": True, "บน": True,

    # Pronouns & Greetings
    "สวัสดี": True, "ขอบคุณ": True, "ขอโทษ": True, "ครับ": True, "ค่ะ": True, "คะ": True,
    "ผม": True, "ฉัน": True, "เขา": True, "เรา": True, "พวกเรา": True, "ท่าน": True,
    "เธอ": True, "คุณ": True, "มัน": True, "ใคร": True, "อะไร": True, "ที่ไหน": True, "อย่างไร": True,
    
    # Common Nouns & Compounding
    "ข้าว": True, "น้ำ": True, "น้ำแข็ง": True, "รถ": True, "รถยนต์": True, "รถไฟ": True,
    "หนังสือ": True, "สมุด": True, "บ้าน": True, "โรงเรียน": True, "มหาวิทยาลัย": True,
    "โรงพยาบาล": True, "ประเทศไทย": True, "ภาษาไทย": True, "เพื่อน": True, "อาจารย์": True,
    "ครู": True, "นักเรียน": True, "หมา": True, "สุนัข": True, "แมว": True, "ช้าง": True,
    "อาหาร": True, "ผลไม้": True, "ร้านอาหาร": True, "ห้องน้ำ": True, "เสื้อ": True,
    "กางเกง": True, "โต๊ะ": True, "เก้าอี้": True, "กระเป๋า": True, "งาน": True, "เวลา": True,
    "วัน": True, "เงิน": True, "ทอง": True, "ความรัก": True, "ความสุข": True,
    
    # Verbs
    "กิน": True, "กินข้าว": True, "ดื่ม": True, "อ่าน": True, "เขียน": True, "ดู": True,
    "นอน": True, "เดิน": True, "ไป": True, "มา": True, "ซื้อ": True, "ขาย": True, "ทำ": True,
    "ทำงาน": True, "เรียน": True, "รู้": True, "เข้าใจ": True, "ชอบ": True, "รัก": True,
    "มี": True, "เป็น": True, "อยู่": True, "พูด": True, "คุย": True, "นั่ง": True, "ยืน": True,
    "ฟัง": True, "ถาม": True, "ตอบ": True, "ช่วย": True, "เสด็จ": True, "เสวย": True,
    
    # Classifiers
    "ตัว": True, "คน": True, "องค์": True, "เล่ม": True, "คัน": True, "หลัง": True,
    "ใบ": True, "ชิ้น": True, "แห่ง": True, "อัน": True,
    
    # Numerals
    "หนึ่ง": True, "สอง": True, "สาม": True, "สี่": True, "ห้า": True, "หก": True,
    "เจ็ด": True, "แปด": True, "เก้า": True, "สิบ": True, "ร้อย": True, "พัน": True,
    
    # Adjectives & Adverbs & Auxiliaries
    "ดี": True, "มาก": True, "สวย": True, "ใหญ่": True, "เล็ก": True, "เร็ว": True, "ช้า": True,
    "อร่อย": True, "แพง": True, "ถูก": True, "ร้อน": True, "หนาว": True, "จริง": True,
    "กำลัง": True, "แล้ว": True, "เคย": True, "จะ": True, "ได้": True, "ไม่": True, "ไม่ได้": True
}

def tokenize_thai(text: str) -> List[str]:
    """
    Maximal matching tokenizer for Thai unspaced scriptio continua.
    """
    tokens: List[str] = []
    i = 0
    n = len(text)
    
    while i < n:
        # Skip ascii / whitespace
        if text[i].isspace():
            i += 1
            continue
            
        # Punctuation check
        if text[i] in ".,!?()[]{}'\"“”ໆ":
            tokens.append(text[i])
            i += 1
            continue
            
        # Try matching longest word from lexicon (up to 14 chars)
        matched = False
        for l in range(min(14, n - i), 1, -1):
            sub = text[i:i + l]
            if sub in THAI_LEXICON:
                tokens.append(sub)
                i += l
                matched = True
                break
                
        if not matched:
            # Check for non-Thai sequence
            if not ('\u0e00' <= text[i] <= '\u0e7f'):
                j = i
                while j < n and not ('\u0e00' <= text[j] <= '\u0e7f') and not text[j].isspace() and text[j] not in ".,!?":
                    j += 1
                tokens.append(text[i:j])
                i = j
            else:
                # Group Thai character with following vowels/tone marks
                j = i + 1
                while j < n and ('\u0e30' <= text[j] <= '\u0e3a' or '\u0e47' <= text[j] <= '\u0e4e'):
                    j += 1
                tokens.append(text[i:j])
                i = j
                
    return tokens
