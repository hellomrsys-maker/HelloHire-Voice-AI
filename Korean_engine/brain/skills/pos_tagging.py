"""
Korean Engine — Part-of-Speech Tagging Skill
Provides Sejong and UPOS tagging for Korean Eojeol and segmented morphemes.
"""

from typing import List, Dict, Any

PARTICLES_SET = {
    "은", "는", "이", "가", "께서", "을", "를", "의", "에", "에서",
    "에게", "한테", "께", "으로", "로", "과", "와", "이랑", "랑", "하고",
    "도", "만", "까지", "부터", "마다", "조차", "보다", "처럼"
}

PRONOUNS_SET = {
    "나", "저", "너", "당신", "우리", "저희", "그", "그녀", "그들", "이것", "그것", "저것", "누구", "무엇", "어디"
}

ADVERBS_SET = {
    "오늘", "어제", "내일", "지금", "아주", "매우", "항상", "자주", "가끔",
    "빨리", "천천히", "잘", "못", "안", "다시", "함께", "이미", "벌써"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, Any]]:
    """Tag tokens with UPOS, Sejong POS, and morpheme segmentation."""
    tagged = []
    
    for token in tokens:
        if token in {".", "!", "?", ",", ";", ":", "\"", "'", "“", "”"}:
            tagged.append({"token": token, "upos": "PUNCT", "sejong": "SF" if token in ".!?" else "SP", "lemma": token})
            continue
            
        if token in ADVERBS_SET:
            tagged.append({"token": token, "upos": "ADV", "sejong": "MAG", "lemma": token})
            continue
            
        if token in PRONOUNS_SET:
            tagged.append({"token": token, "upos": "PRON", "sejong": "NP", "lemma": token})
            continue
            
        # Check if token is a verb/adjective ending in typical terminal endings
        if token.endswith(("다", "습니다", "ㅂ니다", "어요", "아요", "해요", "ㄴ다", "는다", "세요", "십시오")):
            tagged.append({"token": token, "upos": "VERB", "sejong": "VV", "lemma": token})
            continue
            
        # Check if token ends with a known particle
        matched_particle = None
        for p in sorted(PARTICLES_SET, key=len, reverse=True):
            if token.endswith(p) and len(token) > len(p):
                matched_particle = p
                break
                
        if matched_particle:
            stem = token[:-len(matched_particle)]
            tagged.append({
                "token": token,
                "upos": "NOUN",
                "sejong": "NNG+J",
                "stem": stem,
                "particle": matched_particle,
                "lemma": stem
            })
        else:
            # Bare noun or other nominal
            tagged.append({
                "token": token,
                "upos": "NOUN",
                "sejong": "NNG",
                "stem": token,
                "particle": None,
                "lemma": token
            })
            
    return tagged
