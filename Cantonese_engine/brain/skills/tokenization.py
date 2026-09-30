"""
Cantonese Tokenization Engine.
Performs morpheme and multi-character compound segmentation with HKSCS awareness.
"""

from typing import List

# High-frequency Cantonese multi-character vocabulary
CANTONESE_LEXICON = {
    "茶餐廳", "廣東話", "點心", "點樣", "點解", "點算", "冇問題", "唔好", "唔該", "多謝",
    "食飯", "睇波", "買餸", "買嘢", "翻工", "返工", "放工", "收工", "搭車", "搭巴士",
    "打邊爐", "叉燒包", "蝦餃", "燒賣", "蛋撻", "煲仔飯", "絲襪奶茶", "凍檸茶",
    "邊度", "邊個", "邊啲", "幾時", "幾多", "點樣做", "點樣講", "大把", "搞掂", "搞错",
    "冇嘢", "做乜", "做嘢", "傾偈", "瞓覺", "行街", "游水", "打波", "讀書",
    "我哋", "你哋", "佢哋", "大家", "自己", "先生", "小姐", "老闆", "老細"
}

def tokenize_cantonese(text: str) -> List[str]:
    """
    Maximal matching tokenizer prioritized by Cantonese multi-syllable lexicon,
    falling back to individual Chinese characters and whitespace/punctuation tokens.
    """
    tokens: List[str] = []
    i = 0
    n = len(text)
    
    while i < n:
        # Skip ascii whitespace
        if text[i].isspace():
            i += 1
            continue
            
        # Try matching longest compound from lexicon (up to 4 chars)
        matched = False
        for l in range(min(5, n - i), 1, -1):
            sub = text[i:i + l]
            if sub in CANTONESE_LEXICON:
                tokens.append(sub)
                i += l
                matched = True
                break
        
        if not matched:
            # Single character or non-Chinese run
            char = text[i]
            if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf' or '\U00020000' <= char <= '\U0002a6df':
                tokens.append(char)
                i += 1
            else:
                # ASCII / punctuation sequence
                j = i
                while j < n and not ('\u4e00' <= text[j] <= '\u9fff' or '\u3400' <= text[j] <= '\u4dbf') and not text[j].isspace():
                    j += 1
                if j > i:
                    tokens.append(text[i:j])
                    i = j
                else:
                    tokens.append(char)
                    i += 1
                    
    return tokens
