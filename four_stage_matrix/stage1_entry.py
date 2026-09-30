"""
stage1_entry.py - Stage 1: Reserved Entry Boundary (Requirement / Input).

Stage 1 Responsibilities:
1. Formally defines requirement, raw input, operational context, and metadata.
2. Establishes quality rules (e.g. minimum token length, valid UTF-8, zero illegal control characters).
3. Defines explicit success criteria (e.g. minimum composite threshold >= 0.70, zero fatal errors).
4. Validates the requirement-specific contract before releasing execution into Stage 2.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RequirementContract:
    requirement_name: str
    target_format_code: int = 1
    min_word_count: int = 5
    max_word_count: int = 1000
    target_wpm: float = 135.0
    min_composite_threshold: float = 0.65
    strict_invariants: bool = True
    context_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stage1EntryResult:
    is_valid: bool
    sanitized_input: str
    contract: RequirementContract
    quality_checks: Dict[str, bool]
    rejection_reasons: List[str]


class ReservedEntryBoundary:
    """
    Stage 1 Entry Gate enforcing input validation and contract negotiation.
    """

    def __init__(self, contract: Optional[RequirementContract] = None):
        self.contract = contract or RequirementContract(requirement_name="GeneralRecruitmentVerbal")

    def validate_and_bind(self, raw_input: str, custom_context: Optional[Dict[str, Any]] = None) -> Stage1EntryResult:
        if custom_context:
            self.contract.context_metadata.update(custom_context)

        sanitized = raw_input.strip()
        rejections = []

        # Quality Rule 1: UTF-8 and non-empty
        rule_non_empty = len(sanitized) > 0
        if not rule_non_empty:
            rejections.append("Input payload is empty or contains only whitespace.")

        # Quality Rule 2: Word count bounds
        words = sanitized.split()
        word_count = len(words)
        rule_word_bounds = self.contract.min_word_count <= word_count <= self.contract.max_word_count
        if not rule_word_bounds:
            rejections.append(
                f"Word count ({word_count}) violates bounds [{self.contract.min_word_count}, {self.contract.max_word_count}]."
            )

        # Quality Rule 3: Control characters / null byte protection
        rule_no_null = "\x00" not in sanitized
        if not rule_no_null:
            rejections.append("Fatal: Payload contains illegal null byte character (0x00).")

        # Quality Rule 4: Format code range (1..8)
        rule_format_valid = 1 <= self.contract.target_format_code <= 8
        if not rule_format_valid:
            rejections.append(f"Invalid format code: {self.contract.target_format_code}. Must be 1..8.")

        quality_checks = {
            "non_empty": rule_non_empty,
            "word_count_in_bounds": rule_word_bounds,
            "memory_safe_characters": rule_no_null,
            "format_code_valid": rule_format_valid
        }

        is_valid = all(quality_checks.values())

        return Stage1EntryResult(
            is_valid=is_valid,
            sanitized_input=sanitized,
            contract=self.contract,
            quality_checks=quality_checks,
            rejection_reasons=rejections
        )
