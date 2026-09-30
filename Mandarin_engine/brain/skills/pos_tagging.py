"""
Mandarin Part-of-Speech Tagging Skill.
Assigns Penn Chinese Treebank (CTB) morphosyntactic tags to Chinese word tokens.
"""

from typing import List, Tuple, Dict, Any

CTB_TAG_MAP = {
    # Pronouns
    "我": "PN", "你": "PN", "您": "PN", "他": "PN", "她": "PN", "它": "PN",
    "我们": "PN", "你们": "PN", "他们": "PN", "大家": "PN", "自己": "PN",
    # Proper Nouns
    "中国": "NR", "北京": "NR", "上海": "NR",
    # Common Nouns
    "语言": "NN", "计算机": "NN", "模型": "NN", "人工智能": "NN",
    "语法": "NN", "句法": "NN", "词法": "NN", "音系": "NN", "语义": "NN", "语用": "NN",
    "书": "NN", "作业": "NN", "报告": "NN", "电脑": "NN", "问题": "NN", "计划": "NN",
    "老师": "NN", "学生": "NN", "朋友": "NN", "苹果": "NN", "门": "NN", "茶": "NN",
    # Verbs
    "做": "VV", "写": "VV", "看": "VV", "学": "VV", "读": "VV", "吃": "VV",
    "买": "VV", "去": "VV", "来": "VV", "说": "VV", "完成": "VV", "借": "VV",
    "开": "VV", "关": "VV", "推迟": "VV", "打破": "VV", "研究": "VV", "考虑": "VV",
    # Copula & Existential
    "是": "VC", "有": "VE", "没有": "VE", "没": "VE",
    # Adjectives
    "好": "VA", "大": "VA", "小": "VA", "多": "VA", "少": "VA", "快": "VA", "慢": "VA", "高": "VA", "新": "VA",
    # Adverbs
    "很": "AD", "非常": "AD", "太": "AD", "不": "AD", "已经": "AD", "正在": "AD", "就": "AD", "都": "AD", "极": "AD",
    # Prepositions (Coverbs)
    "把": "P", "被": "P", "在": "P", "给": "P", "从": "P", "对": "P", "向": "P", "为": "P", "用": "P",
    # Aspect Particles
    "了": "AS", "着": "AS", "过": "AS",
    # Structural Particles
    "的": "DEG", "地": "DEV", "得": "DEC",
    # Sentence-final modal particles
    "吗": "SP", "呢": "SP", "吧": "SP", "啊": "SP",
    # Classifiers / Measure Words
    "个": "M", "本": "M", "张": "M", "条": "M", "支": "M", "只": "M", "辆": "M", "台": "M", "栋": "M", "座": "M", "杯": "M", "双": "M",
    # Determiners & Numerals
    "这": "DT", "那": "DT", "一": "CD", "二": "CD", "三": "CD", "四": "CD", "五": "CD",
    # Conjunctions
    "和": "CC", "跟": "CC", "虽然": "CS", "但是": "CS", "因为": "CS", "所以": "CS"
}


class MandarinPOSTagger:
    """
    Penn Chinese Treebank POS tagger with context-sensitive rules for coverbs and particles.
    """

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Assigns POS tags to segmented tokens."""
        tagged: List[Tuple[str, str]] = []

        for i, token in enumerate(tokens):
            # Contextual disambiguation for '了' (Aspect vs Sentence-final modal)
            if token == "了":
                if i == len(tokens) - 1 or (i < len(tokens) - 1 and tokens[i + 1] in {"。", "！", "？", "，"}):
                    tagged.append((token, "SP"))  # Modal particle
                else:
                    tagged.append((token, "AS"))  # Aspect marker
                continue

            # Contextual disambiguation for '把' / '被'
            if token in {"把", "被"}:
                tagged.append((token, "P"))
                continue

            # Lookup in CTB tag map
            if token in CTB_TAG_MAP:
                tagged.append((token, CTB_TAG_MAP[token]))
            elif len(token) == 4 and token in {"塞翁失马", "画蛇添足", "半途而废", "胸有成竹", "卧薪尝胆", "名落孙山", "一目了然", "循序渐进"}:
                tagged.append((token, "NR"))  # Chengyu idiom
            elif token in {"。", "，", "！", "？", "、", "；", "：", "“", "”", "(", ")"}:
                tagged.append((token, "PU"))
            else:
                # Default heuristic: fallback to noun
                tagged.append((token, "NN"))

        return tagged
