"""
Pragmatic Presupposition Trigger Detector.
Identifies factive predicates, aspectual shift verbs, iterative markers,
cleft sentences, and counterfactual conditionals to extract pragmatic presuppositions.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PresuppositionTrigger:
    trigger_type: str  # "factive_predicate", "aspectual_change", "iterative", "counterfactual", "definite_description"
    matched_phrase: str
    char_start: int
    char_end: int
    presupposed_fact: str
    is_falsifiable: bool


@dataclass
class PresuppositionReport:
    utterance: str
    triggers: List[PresuppositionTrigger] = field(default_factory=list)
    has_unspoken_assumptions: bool = False


class PresuppositionChecker:
    """
    Extracts presuppositions that must be taken as common ground for an utterance to be felicitous.
    """

    FACTIVE_VERBS = {
        "realized": "The complement proposition is accepted as true by the speaker.",
        "discovered": "The discovered proposition was already true prior to discovery.",
        "regrets": "The event regretted by the agent actually occurred.",
        "knows": "The proposition known is an epistemically verified fact.",
        "remembers": "The remembered experience or fact took place in reality.",
    }

    ASPECTUAL_VERBS = {
        "stopped": "The agent was previously engaged in this action.",
        "quit": "The agent was previously performing this action.",
        "continued": "The agent had already commenced this state and did not discontinue.",
        "resumed": "The agent had previously halted the action and began again.",
        "started": "The agent was not engaging in this action immediately prior.",
    }

    ITERATIVE_MARKERS = {
        "again": "This event or action occurred at least once previously.",
        "another": "At least one instance of this entity already exists or was mentioned.",
        "returned": "The entity was previously present at the destination.",
        "repeated": "The action was executed before.",
    }

    def analyze(self, utterance: str) -> PresuppositionReport:
        triggers: List[PresuppositionTrigger] = []
        u_lower = utterance.lower()

        # 1. Factive verbs
        for verb, presupposition in self.FACTIVE_VERBS.items():
            pattern = rf"\b{verb}\s+that\s+([^,.;]+)"
            for m in re.finditer(pattern, u_lower):
                clause = m.group(1).strip()
                triggers.append(
                    PresuppositionTrigger(
                        trigger_type="factive_predicate",
                        matched_phrase=m.group(0),
                        char_start=m.start(),
                        char_end=m.end(),
                        presupposed_fact=f"Proposition '{clause}' is presupposed to be true",
                        is_falsifiable=True,
                    )
                )

        # 2. Aspectual change verbs
        for verb, presupposition in self.ASPECTUAL_VERBS.items():
            pattern = rf"\b{verb}\s+([a-z]+ing|[a-z]+)"
            for m in re.finditer(pattern, u_lower):
                triggers.append(
                    PresuppositionTrigger(
                        trigger_type="aspectual_change",
                        matched_phrase=m.group(0),
                        char_start=m.start(),
                        char_end=m.end(),
                        presupposed_fact=presupposition,
                        is_falsifiable=True,
                    )
                )

        # 3. Iteratives
        for it, presupposition in self.ITERATIVE_MARKERS.items():
            pattern = rf"\b{it}\b"
            for m in re.finditer(pattern, u_lower):
                triggers.append(
                    PresuppositionTrigger(
                        trigger_type="iterative",
                        matched_phrase=m.group(0),
                        char_start=m.start(),
                        char_end=m.end(),
                        presupposed_fact=presupposition,
                        is_falsifiable=True,
                    )
                )

        # 4. Counterfactual conditionals ("If X had been ..., Y would have ...")
        cf_pattern = r"\bif\s+([a-z\s]+?)\s+had\s+([a-z]+)"
        for m in re.finditer(cf_pattern, u_lower):
            subj = m.group(1)
            verb = m.group(2)
            triggers.append(
                PresuppositionTrigger(
                    trigger_type="counterfactual",
                    matched_phrase=m.group(0),
                    char_start=m.start(),
                    char_end=m.end(),
                    presupposed_fact=f"Presupposes in reality that '{subj}' did NOT '{verb}'.",
                    is_falsifiable=True,
                )
            )

        return PresuppositionReport(
            utterance=utterance,
            triggers=triggers,
            has_unspoken_assumptions=len(triggers) > 0,
        )
