"""
Korean Engine — Honorific Concord Skill
Analyzes subject/object honorification, lexical honorifics, and cross-sentential harmony.
"""

from typing import List, Dict, Any

HONORIFIC_TITLES = {
    "선생님", "교수님", "할아버지", "할머니", "부모님", "아버지", "어머니",
    "사장님", "대표님", "부장님", "과장님", "팀장님", "어르신", "선배님"
}

HONORIFIC_LEXICAL_NOUNS = {
    "진지": "밥",
    "댁": "집",
    "연세": "나이",
    "생신": "생일",
    "말씀": "말",
    "분": "사람",
    "성함": "이름"
}

HONORIFIC_LEXICAL_VERBS = {
    "드시다", "잡수시다", "주무시다", "계시다", "있으시다", "돌아가시다",
    "편찮으시다", "드리다", "모시다", "여쭙다", "뵙다"
}

PLAIN_NOUN_HONORIFIC_EQUIVALENTS = {
    "밥": "진지", "집": "댁", "나이": "연세", "생일": "생신"
}

def analyze_honorific_concord(tokens: List[str], tags: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check honorific harmony across subjects, particles, lexical nouns, and predicates.
    """
    has_hon_particle = any(t["token"].endswith("께서") or t.get("particle") == "께서" for t in tags)
    has_dative_hon_particle = any(t["token"].endswith("께") or t.get("particle") == "께" for t in tags)
    
    hon_titles_found = []
    plain_subjects_found = []
    lexical_hon_nouns = []
    lexical_hon_verbs = []
    
    for t in tags:
        stem = t.get("stem") or t["token"]
        if any(stem.startswith(title) for title in HONORIFIC_TITLES):
            hon_titles_found.append(stem)
        elif stem in {"나", "저", "철수", "영희", "학생", "아이"}:
            plain_subjects_found.append(stem)
            
        for hn in HONORIFIC_LEXICAL_NOUNS:
            if hn in t["token"]:
                lexical_hon_nouns.append(hn)
                
        if t["upos"] == "VERB":
            token_str = t["token"]
            has_lexical_root = any(hv in token_str for hv in ["드리", "모시", "여쭈", "봬", "뵙"])
            
            # Check if any syllable is an honorific infix (시, 신, 실, 셨, 십, 세)
            has_hon_syllable = False
            for ch in token_str:
                from .jaso_engine import decompose_syllable
                decomp = decompose_syllable(ch)
                if decomp and decomp[0] == 'ㅅ' and decomp[1] in {'ㅣ', 'ㅕ', 'ㅔ'}:
                    has_hon_syllable = True
                    break
                    
            if has_lexical_root or has_hon_syllable:
                lexical_hon_verbs.append(token_str)
                
    has_hon_subject = len(hon_titles_found) > 0 or has_hon_particle
    has_hon_predicate = len(lexical_hon_verbs) > 0
    
    # Concord checks
    clash_errors = []
    
    # Case 1: Honored subject with completely plain predicate
    if has_hon_subject and not has_hon_predicate and any(t["upos"] == "VERB" and not t["token"].endswith(("세요", "십시오", "습니다")) for t in tags):
        clash_errors.append("Subject is an elder/superior, but predicate lacks subject honorification -(으)시-")
        
    # Case 2: Lexical mismatch: 진지 with plain 먹다 (instead of 드시다)
    for t in tags:
        if "진지" in t["token"] and any("먹" in tag["token"] for tag in tags if tag["upos"] == "VERB"):
            clash_errors.append("Honorific noun '진지' requires honorific verb '드시다', not plain '먹다'")
            
    is_harmonious = len(clash_errors) == 0
    
    return {
        "has_honorific_subject": has_hon_subject,
        "has_honorific_particle": has_hon_particle,
        "has_honorific_predicate": has_hon_predicate,
        "honorific_titles": hon_titles_found,
        "lexical_honorific_nouns": lexical_hon_nouns,
        "lexical_honorific_verbs": lexical_hon_verbs,
        "is_harmonious": is_harmonious,
        "clash_errors": clash_errors
    }
