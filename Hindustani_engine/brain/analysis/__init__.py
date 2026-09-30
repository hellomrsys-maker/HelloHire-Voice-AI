"""
Hindustani Cognitive Analysis Package.
Exports ergative alignment analyzer, oblique concord analyzer, and honorific agreement analyzer.
"""

from .ergative_alignment_analyzer import ErgativeAlignmentAnalyzer
from .oblique_concord_analyzer import ObliqueConcordAnalyzer
from .honorific_agreement_analyzer import HonorificAgreementAnalyzer

__all__ = [
    "ErgativeAlignmentAnalyzer",
    "ObliqueConcordAnalyzer",
    "HonorificAgreementAnalyzer",
]
