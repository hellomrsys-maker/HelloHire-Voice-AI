"""
Korean Engine — Verb Conjugation Skill
Conjugates regular and 7-irregular verbs across speech levels, tenses, and honorific -(으)시-.
"""

from typing import Dict, Any, Optional
from .jaso_engine import decompose_syllable, compose_syllable, has_batchim, get_batchim

IRREGULAR_CACHE = {
    # ㄷ-irregular
    "듣다": {"haeyo": "들어요", "hasipsio": "듣습니다", "past": "들었어요", "honorific": "들으시다"},
    "걷다": {"haeyo": "걸어요", "hasipsio": "걷습니다", "past": "걸었어요", "honorific": "걸으시다"},
    "묻다": {"haeyo": "물어요", "hasipsio": "묻습니다", "past": "물었어요", "honorific": "물으시다"},
    # ㅂ-irregular
    "춥다": {"haeyo": "추워요", "hasipsio": "춥습니다", "past": "추웠어요", "honorific": "추우시다"},
    "덥다": {"haeyo": "더워요", "hasipsio": "덥습니다", "past": "더웠어요", "honorific": "더우시다"},
    "돕다": {"haeyo": "도와요", "hasipsio": "돕습니다", "past": "도왔어요", "honorific": "도우시다"},
    "곱다": {"haeyo": "고와요", "hasipsio": "곱습니다", "past": "고왔어요", "honorific": "고우시다"},
    "어렵다": {"haeyo": "어려워요", "hasipsio": "어렵습니다", "past": "어려웠어요", "honorific": "어려우시다"},
    "쉽다": {"haeyo": "쉬워요", "hasipsio": "쉽습니다", "past": "쉬웠어요", "honorific": "쉬우시다"},
    "맵다": {"haeyo": "매워요", "hasipsio": "맵습니다", "past": "매웠어요", "honorific": "매우시다"},
    # ㅅ-irregular
    "짓다": {"haeyo": "지어요", "hasipsio": "짓습니다", "past": "지었어요", "honorific": "지으시다"},
    "낫다": {"haeyo": "나아요", "hasipsio": "낫습니다", "past": "나았어요", "honorific": "나으시다"},
    # 르-irregular
    "빠르다": {"haeyo": "빨라요", "hasipsio": "빠릅니다", "past": "빨랐어요", "honorific": "빠르시다"},
    "부르다": {"haeyo": "불러요", "hasipsio": "부릅니다", "past": "불렀어요", "honorific": "부르시다"},
    "모르다": {"haeyo": "몰라요", "hasipsio": "모릅니다", "past": "몰랐어요", "honorific": "모르시다"},
    # 으-drop
    "크다": {"haeyo": "커요", "hasipsio": "큽니다", "past": "컸어요", "honorific": "크시다"},
    "쓰다": {"haeyo": "써요", "hasipsio": "씁니다", "past": "썼어요", "honorific": "쓰시다"},
    "바쁘다": {"haeyo": "바빠요", "hasipsio": "바쁩니다", "past": "바빴어요", "honorific": "바쁘시다"},
    # ㅎ-irregular
    "그렇다": {"haeyo": "그래요", "hasipsio": "그렇습니다", "past": "그랬어요", "honorific": "그러시다"},
    "파랗다": {"haeyo": "파래요", "hasipsio": "파랗습니다", "past": "파랬어요", "honorific": "파라시다"}
}

def conjugate_verb(infinitive: str, speech_level: str = "haeyo", honorific: bool = False, tense: str = "present") -> str:
    """
    Conjugate a Korean verb or adjective.
    speech_level: 'hasipsio' | 'haeyo' | 'haera' | 'hae'
    honorific: True for subject honorification -(으)시-
    tense: 'present' | 'past' | 'future'
    """
    inf = infinitive.strip()
    if not inf.endswith("다"):
        return inf
        
    stem = inf[:-1]
    
    # Check irregular cache
    if inf in IRREGULAR_CACHE:
        cache = IRREGULAR_CACHE[inf]
        if honorific:
            hon_stem = cache["honorific"][:-1]
            return conjugate_verb(cache["honorific"], speech_level, honorific=False, tense=tense)
        if tense == "past":
            base = cache["past"]
            if speech_level == "hasipsio":
                return base[:-2] + "습니다"
            elif speech_level == "haera":
                return base[:-2] + "었다"
            elif speech_level == "hae":
                return base[:-1]
            return base
        if speech_level == "hasipsio":
            return cache["hasipsio"]
        elif speech_level == "haeyo":
            return cache["haeyo"]
        elif speech_level == "hae":
            return cache["haeyo"][:-1]
        elif speech_level == "haera":
            return stem + ("는다" if has_batchim(stem[-1]) else "ㄴ다")

    # Regular conjugation
    last_char = stem[-1]
    has_coda = has_batchim(last_char)
    coda = get_batchim(last_char)
    decomp = decompose_syllable(last_char)
    
    # If honorific requested, insert -(으)시-
    if honorific:
        hon_stem = stem + ("으시" if has_coda else "시")
        return conjugate_verb(hon_stem + "다", speech_level, honorific=False, tense=tense)
        
    # Future tense with -겠-
    if tense == "future":
        fut_stem = stem + "겠"
        if speech_level == "hasipsio":
            return fut_stem + "습니다"
        elif speech_level == "haeyo":
            return fut_stem + "어요"
        elif speech_level == "haera":
            return fut_stem + "다"
        elif speech_level == "hae":
            return fut_stem + "어"
            
    # Hasipsio-che: -습니다 / -ㅂ니다
    if speech_level == "hasipsio":
        if has_coda:
            return stem + "습니다"
        else:
            # Fuse ㅂ as batchim
            cho, jung, _ = decomp
            fused = compose_syllable(cho, jung, 'ㅂ')
            return stem[:-1] + fused + "니다"
            
    # Check for -하다 composite verbs
    if stem.endswith("하"):
        if speech_level == "haeyo":
            return stem[:-1] + "해요"
        elif speech_level == "hae":
            return stem[:-1] + "해"
        elif speech_level == "haera":
            return stem[:-1] + "한다"
            
    # Haeyo / Hae / Past vowel harmony: bright (ㅏ, ㅗ) takes 아, dark takes 어
    vowel = decomp[1] if decomp else 'ㅓ'
    is_bright = vowel in {'ㅏ', 'ㅗ'}
    connective = "아" if is_bright else "어"
    
    if tense == "past":
        past_coda = compose_syllable(decomp[0], decomp[1], 'ㅆ') if not has_coda else None
        if past_coda:
            past_stem = stem[:-1] + past_coda
        else:
            past_stem = stem + ("았" if is_bright else "었")
            
        if speech_level == "hasipsio":
            return past_stem + "습니다"
        elif speech_level == "haeyo":
            return past_stem + "어요"
        elif speech_level == "haera":
            return past_stem + "다"
        elif speech_level == "hae":
            return past_stem + "어"

    # Present Haeyo
    if not has_coda:
        # Contractions: 가 + 아 -> 가, 보 + 아 -> 봐, 서 + 어 -> 서
        if vowel == 'ㅏ':
            return stem + "요"
        elif vowel == 'ㅗ':
            contracted = compose_syllable(decomp[0], 'ㅘ', '')
            return stem[:-1] + contracted + "요"
        elif vowel == 'ㅓ':
            return stem + "요"
        elif vowel == 'ㅜ':
            contracted = compose_syllable(decomp[0], 'ㅝ', '')
            return stem[:-1] + contracted + "요"
        elif vowel == 'ㅣ':
            contracted = compose_syllable(decomp[0], 'ㅕ', '')
            return stem[:-1] + contracted + "요"
        return stem + connective + "요"
    else:
        return stem + connective + "요"
