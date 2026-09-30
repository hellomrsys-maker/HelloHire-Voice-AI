"""
Thai Rachasap and Register Engine.
Audits multi-tier registers:
1: Colloquial (ภาษาปาก)
2: Formal Polite (ภาษาสุภาพ)
3: Monastic (ภาษาพระสงฆ์)
4: Royal Rachasap (ราชาศัพท์)
"""

from typing import Dict, List, Optional

ROAYL_MARKERS = {"เสด็จ", "เสวย", "บรรทม", "สวรรคต", "พระราชทาน", "พระราชดำรัส", "ทรงงาน", "ทรงพระอักษร"}
MONASTIC_MARKERS = {"ฉัน", "จำวัด", "มรณภาพ", "นิมนต์", "อาตมา", "โยม", "พระสงฆ์"}
FORMAL_MARKERS = {"รับประทาน", "นอนหลับ", "เสียชีวิต", "ถึงแก่กรรม", "มอบ", "เดินทาง", "ท่านผู้จัดการ", "ขอแสดงความนับถือ"}
COLLOQUIAL_MARKERS = {"กิน", "นอน", "ตาย", "ไป", "ให้", "เว้ย", "วะ"}

def detect_register(text: str) -> Dict[str, any]:
    """
    Classifies Thai text into one of four sociolinguistic registers.
    """
    has_royal = any(m in text for m in ROAYL_MARKERS) or "พระราช" in text or "ทรง" in text
    has_monastic = any(m in text for m in MONASTIC_MARKERS)
    has_formal = any(m in text for m in FORMAL_MARKERS)
    has_colloquial = any(m in text for m in COLLOQUIAL_MARKERS)
    
    if has_royal:
        tier = 4
        reg_name = "royal_rachasap"
        desc = "ราชาศัพท์ (Royal Rachasap)"
    elif has_monastic:
        tier = 3
        reg_name = "monastic"
        desc = "ภาษาพระสงฆ์ (Monastic Register)"
    elif has_formal:
        tier = 2
        reg_name = "formal"
        desc = "ภาษาสุภาพ / ทางการ (Formal Polite Register)"
    else:
        tier = 1
        reg_name = "colloquial"
        desc = "ภาษาปาก (Colloquial Register)"
        
    return {
        "text": text,
        "register": reg_name,
        "tier_level": tier,
        "description": desc
    }

def compose_email(recipient: str, subject: str, message: str, gender: str = "male") -> str:
    """
    Synthesizes a structured Thai business or administrative email.
    """
    salutation = f"เรียน {recipient} ที่นับถือ,"
    closing_particle = "ครับ" if gender == "male" else "ค่ะ"
    closing = f"จึงเรียนมาเพื่อโปรดพิจารณา{closing_particle}\n\nขอแสดงความนับถืออย่างยิ่ง"
    
    return f"เรื่อง: {subject}\n\n{salutation}\n\n{message}\n\n{closing}"
