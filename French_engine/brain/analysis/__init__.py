"""
French Cognitive Analysis Package.
Exports non-pro-drop analysis, auxiliary/agreement diagnostics, and subjunctive trigger evaluation.
"""

from .non_pro_drop_analyzer import NonProDropAnalyzer
from .auxiliary_agreement_analyzer import AuxiliaryAgreementAnalyzer
from .subjunctive_trigger_evaluator import SubjunctiveTriggerEvaluator

__all__ = [
    "NonProDropAnalyzer",
    "AuxiliaryAgreementAnalyzer",
    "SubjunctiveTriggerEvaluator",
]
