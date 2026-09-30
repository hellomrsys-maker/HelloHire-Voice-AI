"""
Cantonese Aspect Enclitic Engine.
Identifies, validates, and analyzes postverbal aspectual enclitics in Cantonese:
咗 (perfective), 緊 (progressive), 過 (experiential), 開 (habitual),
住 (durative), 吓 (delimitative), 晒 (completive), 埋 (inclusive), 返/翻 (restorative).
"""

from typing import Dict, List, Optional

ASPECT_PROFILES = {
    "咗": {
        "jyutping": "zo2",
        "aspect": "perfective",
        "meaning": "completed event / change of state",
        "mandarin_eq": "了"
    },
    "緊": {
        "jyutping": "gan2",
        "aspect": "progressive",
        "meaning": "action in active progress",
        "mandarin_eq": "正在 / 着"
    },
    "過": {
        "jyutping": "gwo3",
        "aspect": "experiential",
        "meaning": "past experience / completion across threshold",
        "mandarin_eq": "過"
    },
    "開": {
        "jyutping": "hoi1",
        "aspect": "habitual",
        "meaning": "customary / habitual action",
        "mandarin_eq": "習慣做"
    },
    "住": {
        "jyutping": "zyu6",
        "aspect": "durative",
        "meaning": "continuous action / stative maintenance",
        "mandarin_eq": "着"
    },
    "吓": {
        "jyutping": "haa5",
        "aspect": "delimitative",
        "meaning": "brief / tentative action (a little bit)",
        "mandarin_eq": "一下"
    },
    "晒": {
        "jyutping": "saai3",
        "aspect": "quantifying_completive",
        "meaning": "entirely / exhaustively completed",
        "mandarin_eq": "光 / 完 / 全都"
    },
    "埋": {
        "jyutping": "maai4",
        "aspect": "additive_inclusive",
        "meaning": "including also / finished off alongside",
        "mandarin_eq": "連同 / 一起做完"
    },
    "返": {
        "jyutping": "faan1",
        "aspect": "restorative",
        "meaning": "restoration to baseline / return",
        "mandarin_eq": "回 / 恢復"
    },
    "翻": {
        "jyutping": "faan1",
        "aspect": "restorative",
        "meaning": "restoration to baseline / return",
        "mandarin_eq": "回 / 恢復"
    }
}

def extract_aspect_markers(text: str) -> List[Dict[str, any]]:
    """
    Scans a sentence or clause for Cantonese postverbal aspect markers
    and returns their semantic profiles.
    """
    found = []
    for marker, profile in ASPECT_PROFILES.items():
        if marker in text:
            # Locate index
            idx = text.find(marker)
            # Find preceding predicate verb if any
            preceding = text[max(0, idx - 2):idx] if idx > 0 else ""
            found.append({
                "marker": marker,
                "position": idx,
                "aspect": profile["aspect"],
                "meaning": profile["meaning"],
                "jyutping": profile["jyutping"],
                "mandarin_eq": profile["mandarin_eq"],
                "preceding_predicate": preceding
            })
    return found

def has_aspect(text: str, aspect_type: str) -> bool:
    """
    Checks whether a sentence contains a marker corresponding to the given aspect type
    (e.g. 'perfective', 'progressive', 'durative').
    """
    markers = extract_aspect_markers(text)
    return any(m["aspect"] == aspect_type for m in markers)
