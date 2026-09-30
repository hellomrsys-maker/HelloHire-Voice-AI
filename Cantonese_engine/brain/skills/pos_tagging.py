"""
Cantonese Part-of-Speech Tagger.
Assigns Universal Dependencies (UD) POS tags to Cantonese tokens.
"""

from typing import List, Tuple
from Cantonese_engine.brain.skills.tokenization import tokenize_cantonese

# POS Mapping dictionary for core Cantonese lexicon
CANTONESE_POS_LEXICON = {
    # Pronouns
    "我": "PRON", "你": "PRON", "佢": "PRON",
    "我哋": "PRON", "你哋": "PRON", "佢哋": "PRON",
    "自己": "PRON", "大家": "PRON", "邊個": "PRON",
    
    # Classifiers
    "個": "CLF", "隻": "CLF", "條": "CLF", "件": "CLF",
    "本": "CLF", "架": "CLF", "間": "CLF", "張": "CLF",
    "粒": "CLF", "啲": "CLF", "份": "CLF", "杯": "CLF",
    "碗": "CLF", "碟": "CLF", "部": "CLF", "把": "CLF",
    
    # Ditransitive / Core Verbs
    "畀": "VERB", "送": "VERB", "教": "VERB", "借": "VERB", "還": "VERB", "派": "VERB",
    "食": "VERB", "飲": "VERB", "睇": "VERB", "講": "VERB", "諗": "VERB",
    "行": "VERB", "走": "VERB", "買": "VERB", "賣": "VERB", "做": "VERB",
    "食飯": "VERB", "睇波": "VERB", "翻工": "VERB", "返工": "VERB", "放工": "VERB", "收工": "VERB",
    "傾偈": "VERB", "瞓覺": "VERB", "游水": "VERB", "讀書": "VERB", "搞掂": "VERB",
    "有": "VERB", "冇": "VERB", "係": "AUX", "唔係": "AUX",
    
    # Postverbal Aspect Enclitics
    "咗": "PART", "緊": "PART", "過": "PART", "開": "PART",
    "住": "PART", "吓": "PART", "晒": "PART", "埋": "PART", "返": "PART", "翻": "PART",
    
    # Sentence-Final Particles (SFPs)
    "喇": "PART", "啦": "PART", "呀": "PART", "㗎": "PART",
    "啫": "PART", "喎": "PART", "囉": "PART", "添": "PART",
    "咩": "PART", "咋": "PART", "哩": "PART", "播": "PART", "話": "PART", "嘛": "PART",
    
    # Postverbal & Preverbal Adverbs
    "先": "ADV", "多": "ADV", "少": "ADV", "好": "ADV", "好耐": "ADV",
    "好快": "ADV", "好靚": "ADV", "太": "ADV", "都": "ADV", "仲": "ADV",
    "再": "ADV", "又": "ADV", "就": "ADV",
    
    # Negators
    "唔": "ADV", "咪": "ADV", "未": "ADV",
    
    # Nouns
    "書": "NOUN", "車": "NOUN", "人": "NOUN", "狗": "NOUN", "貓": "NOUN",
    "茶餐廳": "NOUN", "廣東話": "NOUN", "點心": "NOUN", "飯": "NOUN", "波": "NOUN",
    "禮物": "NOUN", "錢": "NOUN", "話": "NOUN", "水": "NOUN", "嘢": "NOUN",
    "學校": "NOUN", "舖頭": "NOUN", "公司": "NOUN", "屋": "NOUN", "房": "NOUN",
    "蛋撻": "NOUN", "蝦餃": "NOUN", "叉燒包": "NOUN", "奶茶": "NOUN", "銀包": "NOUN",
    
    # Adjectives
    "大": "ADJ", "細": "ADJ", "多": "ADJ", "少": "ADJ", "長": "ADJ", "短": "ADJ",
    "靚": "ADJ", "得意": "ADJ", "好食": "ADJ", "好飲": "ADJ", "平": "ADJ", "貴": "ADJ",
    "快": "ADJ", "慢": "ADJ", "叻": "ADJ", "醒目": "ADJ", "熱": "ADJ", "凍": "ADJ",
    
    # Numerals
    "一": "NUM", "二": "NUM", "兩": "NUM", "三": "NUM", "四": "NUM",
    "五": "NUM", "六": "NUM", "七": "NUM", "八": "NUM", "九": "NUM", "十": "NUM",
    "幾": "NUM", "幾多": "NUM",
    
    # Adpositions
    "喺": "ADP", "同": "ADP", "自": "ADP", "由": "ADP", "向": "ADP"
}

def tag_pos(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Tags a list of Cantonese tokens with Universal Dependencies POS labels.
    """
    tagged: List[Tuple[str, str]] = []
    
    for token in tokens:
        if token in CANTONESE_POS_LEXICON:
            tagged.append((token, CANTONESE_POS_LEXICON[token]))
        elif token.isdigit():
            tagged.append((token, "NUM"))
        elif any(token.endswith(sfp) for sfp in ["喇", "啦", "呀", "㗎", "啫", "喎", "囉", "添", "咩", "咋"]):
            tagged.append((token, "PART"))
        elif any(c in token for c in ["人", "嘢", "頭", "館", "房", "店"]):
            tagged.append((token, "NOUN"))
        else:
            tagged.append((token, "NOUN"))
            
    return tagged
