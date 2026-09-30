"""
Korean Engine — Speech Level Skill
Classifies Korean sentence-final endings into speech levels and audits pragmatic consistency.
"""

from typing import Dict, Any, List

def classify_speech_level(sentence: str) -> Dict[str, Any]:
    """
    Classify the speech level of a sentence based on its terminal predicate.
    Levels: 'hasipsio', 'haeyo', 'haera', 'hae', 'hage', 'hao', 'neutral'
    """
    clean = sentence.strip().rstrip(".!?~")
    if not clean:
        return {"level": "neutral", "level_code": 0, "ending": ""}
        
    last_word = clean.split()[-1]
    
    # Hasipsio-che: -습니다, -ㅂ니다 (ends with 니다), -습니까, -ㅂ니까 (ends with 니까), -하십시오
    if last_word.endswith(("습니다", "니다", "습니까", "니까", "하십시오", "시지요")):
        return {"level": "hasipsio", "level_code": 1, "ending": last_word}
        
    # Haeyo-che: -아요, -어요, -해요, -지요, -네요, -세요, -군요
    if last_word.endswith(("아요", "어요", "해요", "지요", "네요", "세요", "군요", "게요", "래요")):
        return {"level": "haeyo", "level_code": 2, "ending": last_word}
        
    # Hage-che: -네, -나, -게
    if last_word.endswith(("네", "나", "게")) and not last_word.endswith(("하네", "보네")):
        return {"level": "hage", "level_code": 3, "ending": last_word}
        
    # Hao-che: -오, -소
    if last_word.endswith(("오", "소")):
        return {"level": "hao", "level_code": 4, "ending": last_word}
        
    # Haera-che: -는다, -ㄴ다 (ends with 다 preceded by ㄴ batchim), -다, -니, -냐, -아라, -어라, -자
    from .jaso_engine import has_batchim, get_batchim
    is_n_da = last_word.endswith("다") and len(last_word) >= 2 and has_batchim(last_word[-2]) and get_batchim(last_word[-2]) == "ㄴ"
    if last_word.endswith(("는다", "았다", "었다", "였다", "겠다", "니", "냐", "아라", "어라", "자")) or is_n_da:
        return {"level": "haera", "level_code": 5, "ending": last_word}
        
    # Hae-che (반말): -아, -어, -해, -지
    if last_word.endswith(("아", "어", "해", "지", "야")):
        return {"level": "hae", "level_code": 6, "ending": last_word}
        
    return {"level": "neutral", "level_code": 0, "ending": last_word}

def audit_speech_level_consistency(sentences: List[str]) -> Dict[str, Any]:
    """Check if an utterance or multi-sentence document maintains a consistent speech level."""
    levels_found = []
    for s in sentences:
        res = classify_speech_level(s)
        if res["level"] != "neutral":
            levels_found.append(res["level"])
            
    unique_levels = set(levels_found)
    
    # Mixing formal/polite (hasipsio + haeyo) is common in Korean polite discourse,
    # but mixing polite (hasipsio/haeyo) with banmal (hae/haera) is a severe clash!
    polite_levels = unique_levels.intersection({"hasipsio", "haeyo"})
    informal_levels = unique_levels.intersection({"hae", "haera"})
    
    is_clash = len(polite_levels) > 0 and len(informal_levels) > 0
    
    primary_level = levels_found[0] if levels_found else "neutral"
    
    return {
        "levels_detected": list(unique_levels),
        "primary_level": primary_level,
        "is_clash": is_clash,
        "is_consistent": not is_clash
    }
