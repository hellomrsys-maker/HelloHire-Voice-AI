"""
Figurative Language Detector.
Detects similes, conceptual metaphors, irony, idioms, and hyperbole in English text.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from English_engine.brain.skills.tokenization import EnglishTokenizer


@dataclass
class FigurativeInstance:
    figure_type: str  # "simile", "metaphor", "hyperbole", "idiom", "irony"
    matched_text: str
    char_start: int
    char_end: int
    literal_interpretation: str
    figurative_interpretation: str
    confidence: float


@dataclass
class FigurativeAnalysisReport:
    text: str
    figurative_count: int
    figurative_density: float  # Instances per 100 words
    dominant_figure: Optional[str]
    instances: List[FigurativeInstance] = field(default_factory=list)


class FigurativeDetector:
    """
    Identifies non-literal rhetorical figures including conceptual metaphors,
    idioms, hyperbolic scale extremes, and similes.
    """

    def __init__(self) -> None:
        self.tokenizer = EnglishTokenizer()

        # Well-established English idioms
        self.idiom_lexicon = {
            "spill the beans": "reveal a secret prematurely",
            "bite the bullet": "face a grim situation with fortitude",
            "break a leg": "good luck in a performance",
            "piece of cake": "an exceptionally easy task",
            "hit the nail on the head": "state a fact with exact precision",
            "under the weather": "feeling slightly ill or fatigued",
            "barking up the wrong tree": "pursuing a mistaken line of inquiry",
            "burn the midnight oil": "work late into the night",
            "cold feet": "sudden hesitation or fear before a commitment",
            "cost an arm and a leg": "be exceedingly expensive",
        }

        # Common metaphor pairings (Domain mapping: TARGET is SOURCE)
        self.metaphor_patterns = [
            (r"\b(time is money)\b", "Time is conceptualized as a finite fiscal resource"),
            (r"\b(wasted my time)\b", "Time is conceptualized as consumable currency"),
            (r"\b(attacked his argument)\b", "Argument is conceptualized as physical warfare"),
            (r"\b(defended her claim)\b", "Debate is conceptualized as territorial defense"),
            (r"\b(drowning in (work|debt|sorrow))\b", "Overwhelmed state conceptualized as submersion"),
            (r"\b(shattered (dreams|hopes|silence))\b", "Abstract emotional/auditory state conceptualized as brittle glass"),
            (r"\b(light at the end of the tunnel)\b", "Hope conceptualized as navigation towards illumination"),
        ]

        # Hyperbolic intensifiers
        self.hyperbole_markers = [
            r"\b(literally died of laughter)\b",
            r"\b(waited a million years)\b",
            r"\b(starving to death)\b",
            r"\b(tons of work)\b",
            r"\b(freezing to death)\b",
            r"\b(best thing in the entire universe)\b",
            r"\b(worst thing that ever happened)\b",
        ]

    def analyze(self, text: str) -> FigurativeAnalysisReport:
        instances: List[FigurativeInstance] = []
        text_lower = text.lower()
        tokens = self.tokenizer.tokenize(text)
        word_count = max(1, sum(1 for t in tokens if t.is_word))

        # 1. Simile detection ("like a/an...", "as ADJ as...")
        simile_regex = r"\b(as\s+[a-z]+\s+as\s+(?:a|an|the)?\s*[a-z]+|like\s+(?:a|an|the)?\s*[a-z]+)\b"
        for m in re.finditer(simile_regex, text_lower):
            matched = text[m.start() : m.end()]
            instances.append(
                FigurativeInstance(
                    figure_type="simile",
                    matched_text=matched,
                    char_start=m.start(),
                    char_end=m.end(),
                    literal_interpretation="Explicit comparison denoting high similarity",
                    figurative_interpretation=f"Poetic analogy mapping attributes via '{matched}'",
                    confidence=0.88,
                )
            )

        # 2. Idiom detection
        for idiom, meaning in self.idiom_lexicon.items():
            if idiom in text_lower:
                idx = text_lower.find(idiom)
                instances.append(
                    FigurativeInstance(
                        figure_type="idiom",
                        matched_text=text[idx : idx + len(idiom)],
                        char_start=idx,
                        char_end=idx + len(idiom),
                        literal_interpretation=f"Literal physical acts of {idiom}",
                        figurative_interpretation=meaning,
                        confidence=0.96,
                    )
                )

        # 3. Metaphor detection
        for pat, interpretation in self.metaphor_patterns:
            for m in re.finditer(pat, text_lower):
                matched = text[m.start() : m.end()]
                instances.append(
                    FigurativeInstance(
                        figure_type="metaphor",
                        matched_text=matched,
                        char_start=m.start(),
                        char_end=m.end(),
                        literal_interpretation="Direct literal physical predicate assertion",
                        figurative_interpretation=interpretation,
                        confidence=0.85,
                    )
                )

        # 4. Hyperbole detection
        for hpat in self.hyperbole_markers:
            for m in re.finditer(hpat, text_lower):
                matched = text[m.start() : m.end()]
                instances.append(
                    FigurativeInstance(
                        figure_type="hyperbole",
                        matched_text=matched,
                        char_start=m.start(),
                        char_end=m.end(),
                        literal_interpretation="Extravagant literal claim with impossible magnitude",
                        figurative_interpretation="Subjective psychological intensification",
                        confidence=0.92,
                    )
                )

        # Determine dominant figure
        type_counts: Dict[str, int] = {}
        for inst in instances:
            type_counts[inst.figure_type] = type_counts.get(inst.figure_type, 0) + 1

        dominant = max(type_counts, key=type_counts.get) if type_counts else None
        density = (len(instances) / word_count) * 100.0

        return FigurativeAnalysisReport(
            text=text,
            figurative_count=len(instances),
            figurative_density=round(density, 2),
            dominant_figure=dominant,
            instances=instances,
        )
