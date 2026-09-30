"""
Second Language Acquisition (SLA) and Cognitive Neurolinguistics Engine.

Applies empirical psycholinguistic and cognitive learning principles:
  - Larry Selinker's Interlanguage Hypothesis (Interlanguage stage tracking)
  - Error Fossilization Risk Index
  - Stephen Krashen's Comprehensible Input ($i+1$) & Affective Filter Model
  - John Sweller's Cognitive Load Theory (Intrinsic, Extraneous, Germane load)
  - Neurobiological spaced retrieval and consciousness-raising interventions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SLADiagnosisResult:
    interlanguage_stage: str  # Basilect, Mesolect, Acrolect
    fossilization_risk_score: float  # 0.0 to 1.0
    fossilized_patterns_flagged: List[str]
    krashen_input_zone: str
    cognitive_load_profile: Dict[str, str]
    neurolinguistic_remediation_regimen: List[str]


class SLAEngine:
    """
    SLA and cognitive neurolinguistic diagnostician.
    """

    def diagnose_learner(
        self,
        errors_detected: List[str],
        l1: str = "Spanish",
        l2: str = "English",
        exposure_years: float = 2.0
    ) -> SLADiagnosisResult:
        error_count = len(errors_detected)

        # 1. Interlanguage Stage
        if error_count <= 1:
            stage = "Acrolect (Advanced near-native interlanguage; subtle stylistic nuances remain)"
            fossilization_risk = 0.15
        elif error_count <= 4:
            stage = "Mesolect (Intermediate interlanguage; core syntax stabilized, morphological errors persist)"
            fossilization_risk = 0.45
        else:
            stage = "Basilect (Emergent interlanguage; heavy L1 structural substrate interference)"
            fossilization_risk = 0.75

        # Exposure penalty on fossilization
        if exposure_years >= 3.0 and error_count >= 2:
            fossilization_risk = min(1.0, fossilization_risk + 0.20)

        # 2. Fossilized patterns
        fossilized = []
        for e in errors_detected:
            if "Subject-Verb Agreement" in e or "Third Person" in e:
                fossilized.append("3rd-person singular present -s omission (Classic morphological fossilization target).")
            if "Article" in e:
                fossilized.append("Definite/indefinite article omission or over-generalization from article-less L1.")
            if "Preposition" in e:
                fossilized.append("L1 collocational preposition calquing (Direct literal translation of L1 adpositions).")

        if not fossilized:
            fossilized.append("No entrenched fossilized patterns detected; errors are developmental rather than permanent.")

        # 3. Krashen's i+1 Zone
        krashen_zone = (
            f"Current Competency Zone: i (Interlanguage stage: {stage.split()[0]}). "
            f"Target Pedagogical Influx: i + 1 (Slightly beyond current productive mastery, accessible via structural scaffolding)."
        )

        # 4. Cognitive Load Modeling (Sweller)
        cog_load = {
            "Intrinsic Load": "Inherent complexity of syntactic movement operations (e.g., Wh-extraction, Subjunctive inversion).",
            "Extraneous Load": "Unhelpful instruction that presents disconnected grammatical rules rather than functional communicative patterns.",
            "Germane Load": "Mental effort dedicated to schema construction, parameter resetting, and internalizing automated morphosyntactic patterns."
        }

        # 5. Neurolinguistic Remediation
        remediation = [
            "Consciousness-Raising Tasks: Explicitly contrast erroneous interlanguage output with native target models.",
            "Spaced Retrieval Schedule: Re-test targeted grammatical constraints at expanding intervals (1 day, 3 days, 1 week, 3 weeks).",
            "Enhanced Input Scaffolding: Provide reading passages flooded with high-frequency instances of the target structure.",
            "Dual-Coding Integration: Pair abstract syntactic tree diagrams with concrete situational role-playing."
        ]

        return SLADiagnosisResult(
            interlanguage_stage=stage,
            fossilization_risk_score=round(fossilization_risk, 2),
            fossilized_patterns_flagged=list(set(fossilized)),
            krashen_input_zone=krashen_zone,
            cognitive_load_profile=cog_load,
            neurolinguistic_remediation_regimen=remediation
        )
