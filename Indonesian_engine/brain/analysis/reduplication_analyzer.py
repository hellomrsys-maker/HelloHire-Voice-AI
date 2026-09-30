"""
Indonesian Engine — Reduplication Analyzer
Audits Indonesian reduplication compliance, enforces hyphenation, and flags informal numeric shorthand (*buku2 -> buku-buku).
"""

import re
from typing import Dict, Any, List
from ..skills.reduplication_engine import analyze_reduplication

# Regex catching non-standard informal numeric reduplication (e.g. anak2, buku2)
NUMERIC_REDUP_RE = re.compile(r"\b([a-zA-Z]+)2\b")

class ReduplicationAnalyzer:
    """Cognitive analyzer for Indonesian reduplication syntax and orthography."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        violations = []
        reduplications_found = []
        
        # 1. Detect informal numeric reduplication (*buku2)
        numeric_matches = NUMERIC_REDUP_RE.findall(text)
        for base in numeric_matches:
            violations.append({
                "token": f"{base}2",
                "rule": "informal_numeric_reduplication",
                "error": f"Informal numeric abbreviation '{base}2' must be written in standard hyphenated reduplication as '{base}-{base}'."
            })
            
        # 2. Inspect standard hyphenated words
        words = text.split()
        for w in words:
            clean = w.strip(".,!?;:\"'()").lower()
            if "-" in clean:
                res = analyze_reduplication(clean)
                if res["is_reduplicated"]:
                    reduplications_found.append(res)
                    
        return {
            "text": text,
            "reduplications_found": reduplications_found,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
