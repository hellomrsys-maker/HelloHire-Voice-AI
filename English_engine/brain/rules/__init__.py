"""
English Rules Engine Package.
Contains declarative grammar, syntax, style, punctuation, and register rule specifications.
"""

from English_engine.brain.rules.rules_engine import RulesEngine, RuleViolation, RegisterProfile

__all__ = [
    "RulesEngine",
    "RuleViolation",
    "RegisterProfile",
]
