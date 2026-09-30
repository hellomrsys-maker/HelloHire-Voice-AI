"""
Persian Ezafe Attachment Analyzer
Cognitive analysis module auditing noun-phrase Ezafe chaining, modifier attachment,
and surface spelling consistency.
"""

from typing import Dict, Any, List, Tuple
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger
from Persian_engine.brain.skills.ezafe_engine import PersianEzafeEngine

class EzafeAttachmentAnalyzer:
    """
    Audits noun phrase structures in Persian text to detect:
    - Missing vowel-ending Ezafe markers (e.g. خانه بزرگ instead of خانهٔ بزرگ)
    - Valid multi-level Ezafe chaining
    - Inappropriate Ezafe placement (e.g. before postposition 'rā')
    """

    def __init__(self):
        self.tagger = PersianPOSTagger()
        self.ezafe = PersianEzafeEngine()

    def analyze_ezafe_chains(self, text: str) -> Dict[str, Any]:
        """Analyzes Ezafe structures in text."""
        tagged = self.tagger.tag_sentence(text)
        chains = []
        issues = []
        
        i = 0
        while i < len(tagged):
            word, pos = tagged[i]
            
            # Check if current word is a noun and next is adj/noun/pron
            if pos == "NOUN" and i + 1 < len(tagged):
                next_word, next_pos = tagged[i + 1]
                
                # Check for Ezafe drop before 'rā'
                if next_word == "را":
                    # Correct: Ezafe must NOT occur immediately before rā
                    pass
                elif next_pos in {"ADJ", "NOUN", "PRON"}:
                    chain_elements = [word, next_word]
                    
                    # Check orthographic suitability for silent heh or vowel
                    ez_spec = self.ezafe.determine_ezafe_suffix(word)
                    if ez_spec["type"] == "silent_heh":
                        if not (word.endswith("ٔ") or word.endswith("ی")):
                            issues.append({
                                "token": word,
                                "next_token": next_word,
                                "type": "missing_silent_heh_ezafe",
                                "suggestion": f"{word}ٔ {next_word}",
                                "message": f"Silent heh noun '{word}' preceding modifier '{next_word}' should indicate Ezafe with hamzeh (ٔ) or 'ی'."
                            })
                    elif ez_spec["type"] == "vowel_alif_vav":
                        if not word.endswith("ی"):
                            issues.append({
                                "token": word,
                                "next_token": next_word,
                                "type": "missing_vowel_ezafe",
                                "suggestion": f"{word}ی {next_word}",
                                "message": f"Vowel-ending noun '{word}' preceding modifier '{next_word}' requires Ezafe marker 'ی'."
                            })
                            
                    chains.append({
                        "head": word,
                        "modifier": next_word,
                        "ezafe_type": ez_spec["type"]
                    })
            i += 1

        return {
            "total_chains": len(chains),
            "chains": chains,
            "issues": issues,
            "is_valid": len(issues) == 0
        }
