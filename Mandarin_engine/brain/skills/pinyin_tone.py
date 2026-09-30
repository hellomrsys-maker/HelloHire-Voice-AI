"""
Mandarin Pinyin G2P and Tone Sandhi Skill.
Maps Chinese characters to Pinyin, generates phonemic tone sequences,
and executes 3rd tone sandhi, 一 (yī) sandhi, and 不 (bù) sandhi.
"""

from typing import List, Dict, Any, Tuple

# Comprehensive character to (pinyin_base, tone) dictionary
CHAR_PINYIN_MAP: Dict[str, Tuple[str, int]] = {
    "我": ("wo", 3), "你": ("ni", 3), "您": ("nin", 2), "他": ("ta", 1), "她": ("ta", 1), "它": ("ta", 1),
    "们": ("men", 0), "好": ("hao", 3), "是": ("shi", 4), "不": ("bu", 4), "一": ("yi", 1),
    "了": ("le", 0), "的": ("de", 0), "得": ("de", 0), "地": ("de", 0), "在": ("zai", 4),
    "有": ("you", 3), "个": ("ge", 4), "书": ("shu", 1), "把": ("ba", 3), "被": ("bei", 4),
    "看": ("kan", 4), "写": ("xie", 3), "做": ("zuo", 4), "学": ("xue", 2), "生": ("sheng", 1),
    "老": ("lao", 3), "师": ("shi", 1), "总": ("zong", 3), "请": ("qing", 3), "谢": ("xie", 4),
    "很": ("hen", 3), "大": ("da", 4), "小": ("xiao", 3), "买": ("mai", 3), "卖": ("mai", 4),
    "吃": ("chi", 1), "饭": ("fan", 4), "想": ("xiang", 3), "来": ("lai", 2), "去": ("qu", 4),
    "人": ("ren", 2), "工": ("gong", 1), "作": ("zuo", 4), "定": ("ding", 4), "天": ("tian", 1),
    "年": ("nian", 2), "起": ("qi", 3), "对": ("dui", 4), "行": ("xing", 2), "门": ("men", 2),
    "关": ("guan", 1), "完": ("wan", 2), "推": ("tui", 1), "迟": ("chi", 2), "打": ("da", 3),
    "破": ("po", 4), "杯": ("bei", 1), "子": ("zi", 0), "水": ("shui", 3), "果": ("guo", 3)
}

TONE_DIACRITICS = {
    "a": ["a", "ā", "á", "ǎ", "à"],
    "e": ["e", "ē", "é", "ě", "è"],
    "i": ["i", "ī", "í", "ǐ", "ì"],
    "o": ["o", "ō", "ó", "ǒ", "ò"],
    "u": ["u", "ū", "ú", "ǔ", "ù"],
    "v": ["ü", "ǖ", "ǘ", "ǚ", "ǜ"]
}


class PinyinToneEngine:
    """
    Phonological G2P and tone sandhi rule engine for Mandarin Chinese.
    """

    def hanzi_to_raw_pinyin(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Maps characters to (char, base_pinyin, tone_number).
        """
        res: List[Tuple[str, str, int]] = []
        for char in text:
            if char in CHAR_PINYIN_MAP:
                base, tone = CHAR_PINYIN_MAP[char]
                res.append((char, base, tone))
            elif char.isspace() or char in {"，", "。", "！", "？", "、"}:
                res.append((char, "", -1))
            else:
                res.append((char, "x", 1))
        return res

    def apply_tone_sandhi(self, pinyin_list: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
        """
        Applies Mandarin tone sandhi:
        1. 3+3 -> 2+3 (Third tone sandhi, e.g. 你好 nǐ hǎo -> ní hǎo)
        2. 一 (yī) before 4th tone -> 2nd tone (yí); before 1st/2nd/3rd -> 4th tone (yì)
        3. 不 (bù) before 4th tone -> 2nd tone (bú)
        """
        n = len(pinyin_list)
        sandhi_result: List[Tuple[str, str, int]] = []

        for i in range(n):
            char, base, tone = pinyin_list[i]

            if tone == -1:
                sandhi_result.append((char, base, tone))
                continue

            # Look ahead to next syllable
            next_tone = -1
            if i + 1 < n:
                next_tone = pinyin_list[i + 1][2]

            # Rule 1: Third Tone Sandhi (3 + 3 -> 2 + 3)
            if tone == 3 and next_tone == 3:
                sandhi_result.append((char, base, 2))
                continue

            # Rule 2: "一" (yī) Sandhi
            if char == "一":
                if next_tone == 4:
                    sandhi_result.append((char, base, 2))  # yí dìng
                    continue
                elif next_tone in {1, 2, 3}:
                    sandhi_result.append((char, base, 4))  # yì tiān, yì nián, yì qǐ
                    continue

            # Rule 3: "不" (bù) Sandhi
            if char == "不":
                if next_tone == 4:
                    sandhi_result.append((char, base, 2))  # bú shì, bú duì
                    continue

            # Default: Retain lexical tone
            sandhi_result.append((char, base, tone))

        return sandhi_result

    def format_with_diacritics(self, base: str, tone: int) -> str:
        """Converts base pinyin and tone number (0-4) to pinyin with tone mark."""
        if tone <= 0 or tone > 4 or not base:
            return base

        # Priority of vowel receiving tone mark: a, o, e, iu/ui (second vowel), otherwise first vowel
        target_vowel = ""
        if "a" in base:
            target_vowel = "a"
        elif "o" in base:
            target_vowel = "o"
        elif "e" in base:
            target_vowel = "e"
        elif "ui" in base:
            target_vowel = "i"
        elif "iu" in base:
            target_vowel = "u"
        else:
            for v in ["i", "u", "v"]:
                if v in base:
                    target_vowel = v
                    break

        if not target_vowel:
            return base

        marked = TONE_DIACRITICS[target_vowel][tone]
        return base.replace(target_vowel, marked, 1)

    def text_to_pinyin_string(self, text: str, apply_sandhi: bool = True) -> str:
        """Translates Hanzi text into spaced Pinyin string with tone marks."""
        raw = self.hanzi_to_raw_pinyin(text)
        processed = self.apply_tone_sandhi(raw) if apply_sandhi else raw

        out = []
        for char, base, tone in processed:
            if tone == -1:
                out.append(char)
            else:
                out.append(self.format_with_diacritics(base, tone))

        return " ".join(out).replace(" ，", "，").replace(" 。", "。")
