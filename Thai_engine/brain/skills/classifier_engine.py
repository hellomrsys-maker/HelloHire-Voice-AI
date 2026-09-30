"""
Thai Numeral Classifier Engine.
Validates post-nominal classifier syntax [Noun] + [Numeral] + [Classifier],
and detects ungrammatical pre-nominal calques (*[Numeral] + [Classifier] + [Noun]).
"""

from typing import Dict, List, Optional

NOUN_CLASSIFIER_MAP = {
    "หมา": "ตัว", "สุนัข": "ตัว", "แมว": "ตัว", "ช้าง": "ตัว", "ปลา": "ตัว", "นก": "ตัว",
    "เสื้อ": "ตัว", "กางเกง": "ตัว", "โต๊ะ": "ตัว", "เก้าอี้": "ตัว",
    "คน": "คน", "นักเรียน": "คน", "ครู": "คน", "เพื่อน": "คน", "เด็ก": "คน", "อาจารย์": "คน",
    "หนังสือ": "เล่ม", "สมุด": "เล่ม", "มีด": "เล่ม", "เทียน": "เล่ม",
    "รถ": "คัน", "รถยนต์": "คัน", "จักรยาน": "คัน", "ร่ม": "คัน", "ช้อน": "คัน",
    "บ้าน": "หลัง", "กระท่อม": "หลัง", "ตึก": "หลัง",
    "กระเป๋า": "ใบ", "แก้ว": "ใบ", "จาน": "ใบ", "ถ้วย": "ใบ", "ไข่": "ใบ",
    "เค้ก": "ชิ้น", "ขนม": "ชิ้น", "เนื้อ": "ชิ้น",
    "สถานที่": "แห่ง", "โรงพยาบาล": "แห่ง", "มหาวิทยาลัย": "แห่ง",
    "พระพุทธรูป": "องค์", "พระสงฆ์": "องค์"
}

NUMERALS = {"หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า", "สิบ"}
ALL_CLASSIFIERS = {"ตัว", "คน", "องค์", "เล่ม", "คัน", "หลัง", "ใบ", "ชิ้น", "แห่ง", "อัน"}

def get_classifier_for_noun(noun: str) -> str:
    """Returns canonical classifier for noun, defaulting to 'อัน'."""
    return NOUN_CLASSIFIER_MAP.get(noun, "อัน")

def audit_classifier_syntax(tokens: List[str]) -> Dict[str, any]:
    """
    Scans token stream for classifier structures:
    - Canonical: [Noun] + [Num] + [Clf] (e.g. หมา สอง ตัว)
    - Calque error: [Num] + [Clf] + [Noun] (e.g. สอง ตัว หมา)
    """
    violations = []
    found_structures = []
    
    for i in range(len(tokens) - 2):
        t1, t2, t3 = tokens[i], tokens[i + 1], tokens[i + 2]
        
        # Check canonical: Noun + Num + Clf
        if t1 in NOUN_CLASSIFIER_MAP and t2 in NUMERALS and t3 in ALL_CLASSIFIERS:
            found_structures.append({
                "type": "canonical",
                "noun": t1,
                "numeral": t2,
                "classifier": t3,
                "phrase": f"{t1}{t2}{t3}"
            })
            
        # Check calque: Num + Clf + Noun
        elif t1 in NUMERALS and t2 in ALL_CLASSIFIERS and t3 in NOUN_CLASSIFIER_MAP:
            violations.append(f"Ungrammatical pre-nominal calque '{t1}{t2}{t3}' detected; recommend canonical '{t3}{t1}{t2}'")
            found_structures.append({
                "type": "calque_error",
                "noun": t3,
                "numeral": t1,
                "classifier": t2,
                "phrase": f"{t1}{t2}{t3}",
                "suggested": f"{t3}{t1}{t2}"
            })
            
    is_valid = len(violations) == 0
    return {
        "is_valid": is_valid,
        "violations": violations,
        "structures": found_structures,
        "concord_flag": 1 if is_valid else 0
    }
