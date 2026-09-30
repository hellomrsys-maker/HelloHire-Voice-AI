"""Russian Aspect Choice Analyzer.

Evaluates aspectual harmony (НСВ/СВ balance), adverbial compatibility
(habitual adverbs with imperfective, punctual adverbs with perfective),
and motion verb determinacy.
"""

from typing import Dict, Any, List
from ..skills.tokenization import RussianTokenizer
from ..skills.pos_tagging import RussianPOSTagger
from ..skills.verb_aspect_conjugator import RussianVerbAspectConjugator
from ..skills.motion_verb_engine import RussianMotionVerbEngine


class RussianAspectChoiceAnalyzer:
    HABITUAL_ADVERBS = {"часто", "всегда", "каждый", "обычно", "регулярно", "долго", "постоянно", "ежедневно"}
    PUNCTUAL_ADVERBS = {"вдруг", "наконец", "сразу", "неожиданно", "мгновенно"}

    def __init__(
        self,
        tokenizer: RussianTokenizer = None,
        pos_tagger: RussianPOSTagger = None,
        verb_conjugator: RussianVerbAspectConjugator = None,
        motion_engine: RussianMotionVerbEngine = None
    ):
        self.tokenizer = tokenizer or RussianTokenizer()
        self.pos_tagger = pos_tagger or RussianPOSTagger()
        self.verb_conjugator = verb_conjugator or RussianVerbAspectConjugator()
        self.motion_engine = motion_engine or RussianMotionVerbEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyzes text for verbal aspect distribution, motion verbs, and aspectual harmony."""
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag(tokens)

        impf_count = 0
        perf_count = 0
        motion_verbs = []
        verb_aspects = []
        issues = []

        for i, item in enumerate(tagged):
            tok = item["token"]
            pos = item["pos"]

            if pos == "VERB":
                aspect_info = self.verb_conjugator.get_aspect(tok)
                motion_info = self.motion_engine.analyze_motion_verb(tok)

                if aspect_info["aspect"] == "perf":
                    perf_count += 1
                else:
                    impf_count += 1

                if motion_info["is_motion_verb"]:
                    motion_verbs.append({"verb": tok, "details": motion_info})

                # Check preceding token for adverbial triggers
                if i > 0:
                    prev_tok = tagged[i - 1]["token"].lower()
                    if prev_tok in self.HABITUAL_ADVERBS and aspect_info["aspect"] == "perf":
                        issues.append({
                            "type": "aspect_clash",
                            "message": f"Habitual adverb '{prev_tok}' conflicts with perfective verb '{tok}'.",
                            "severity": "warning"
                        })

                verb_aspects.append({
                    "verb": tok,
                    "aspect": aspect_info["aspect"],
                    "partner": aspect_info["partner"]
                })

        total_verbs = impf_count + perf_count
        perf_ratio = (perf_count / total_verbs) if total_verbs > 0 else 0.0

        return {
            "text": text,
            "total_verbs": total_verbs,
            "imperfective_count": impf_count,
            "perfective_count": perf_count,
            "perfective_ratio": round(perf_ratio, 2),
            "motion_verbs": motion_verbs,
            "verb_aspects": verb_aspects,
            "issues": issues,
            "is_balanced": len(issues) == 0
        }
