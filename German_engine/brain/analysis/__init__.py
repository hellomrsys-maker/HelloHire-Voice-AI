"""
German Engine — Cognitive Analyzers Package
"""

from .satzklammer_analyzer import SatzklammerAnalyzer
from .case_government_analyzer import CaseGovernmentAnalyzer
from .adjective_agreement_analyzer import AdjectiveAgreementAnalyzer

__all__ = [
    "SatzklammerAnalyzer",
    "CaseGovernmentAnalyzer",
    "AdjectiveAgreementAnalyzer"
]
