"""
Tamil Case & PNG Concord Cognitive Analyzer.
Audits nominal case agglutination and Subject-Verb Person-Number-Gender concord.
"""

from typing import Dict, List
from Tamil_engine.brain.skills.case_engine import analyze_noun_case
from Tamil_engine.brain.skills.png_concord_engine import check_png_concord
from Tamil_engine.brain.skills.tokenization import tokenize_tamil

class CasePngAnalyzer:
    """
    Evaluates Tamil case declensions and subject-verb PNG agreement.
    """
    def __init__(self):
        self.name = "Tamil Case & PNG Concord Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        tokens = tokenize_tamil(text.rstrip(".,!?"))
        cases_found = []
        for t in tokens:
            c_info = analyze_noun_case(t)
            if c_info["is_inflected"]:
                cases_found.append(c_info)
                
        # Check first token as potential pronominal subject and last token as verb
        png_res = {"is_concordant": True, "error": None}
        if len(tokens) >= 2:
            subj = tokens[0]
            verb = tokens[-1]
            if subj in ["நான்", "நாம்", "நாங்கள்", "நீ", "நீங்கள்", "அவன்", "அவள்", "அவர்", "அவர்கள்", "அது", "அவை"]:
                png_res = check_png_concord(subj, verb)
                
        is_sound = png_res["is_concordant"]
        score = 1.0 if is_sound else 0.5
        
        return {
            "text": text,
            "cases_found": cases_found,
            "png_concord": png_res,
            "is_grammatically_sound": is_sound,
            "score": score
        }
