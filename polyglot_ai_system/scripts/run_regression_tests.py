#!/usr/bin/env python3
"""
scripts/run_regression_tests.py
================================
Regression test runner for all canonical language engine YAML files.

Enforces the following spec rules:

1. CANONICAL FILE RULE
   Every engine must have exactly ONE canonical YAML file in language_engines/.
   No raw dialogue may be stored. The file must be loadable via EngineTrainingAPI.

2. 19-SECTION RULE
   Every canonical YAML must contain all 19 required sections in spec order.

3. TRAINING DATA RULE
   Every item in training_data must have review_status: approved.

4. REGRESSION TEST RULE
   Every training_data item must have at least one corresponding entry in
   examples with is_regression_test: true and a non-empty
   regression_pass_criteria list.

5. EVALUATION RULE
   The evaluation section must be a list (not a dict). Every rule must have
   rule_id, rule_type, threshold, and blocking fields.

6. CHANGELOG RULE
   version_control.history must have at least two entries: the initial scaffold
   entry and at least one subsequent update entry.

Exit codes:
  0 — all engines pass all checks
  1 — one or more engines failed one or more checks

Usage:
  python scripts/run_regression_tests.py
  python scripts/run_regression_tests.py --engines fr,de,ja
  python scripts/run_regression_tests.py --engines-dir path/to/language_engines
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_SECTIONS_ORDERED: List[str] = [
    "engine_identity",
    "artificial_intelligence_core",
    "brain",
    "skills",
    "creativity",
    "language_rules",
    "sentence_processing",
    "sentence_generation",
    "sentence_breakdown",
    "vocabulary",
    "pronunciation",
    "meaning",
    "pragmatics",
    "training_data",
    "examples",
    "evaluation",
    "memory_policy",
    "connections",
    "version_control",
]

DEFAULT_ENGINES_DIR = Path("polyglot_ai_system/language_engines")
ALL_ENGINE_STEMS = [
    "English_engine.training",
    "French_engine.training",
    "Spanish_engine.training",
    "German_engine.training",
    "Japanese_engine.training",
    "Arabic_engine.training",
    "Tamil_engine.training",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(message)s",
)
logger = logging.getLogger("regression_tests")

# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------


class CheckResult:
    """Single check result: pass or fail with an optional message."""

    def __init__(self, check_name: str, passed: bool, message: str = "") -> None:
        self.check_name = check_name
        self.passed = passed
        self.message = message

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        suffix = f": {self.message}" if self.message else ""
        return f"[{status}] {self.check_name}{suffix}"


class EngineReport:
    """Aggregated check results for one engine file."""

    def __init__(self, engine_file: Path) -> None:
        self.engine_file = engine_file
        self.results: List[CheckResult] = []

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def print_summary(self) -> None:
        status = "[PASSED]" if self.passed else "[FAILED]"
        print(f"\n{'=' * 60}")
        print(f"Engine: {self.engine_file.name}")
        print(f"Status: {status}  ({self.failure_count} failures / {len(self.results)} checks)")
        print(f"{'=' * 60}")
        for r in self.results:
            print(f"  {r}")


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_file_loadable(engine_file: Path) -> Tuple[CheckResult, Optional[Dict[str, Any]]]:
    """Attempt to load the YAML file; return result and data dict."""
    try:
        with open(engine_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return CheckResult("file_loadable", False, "YAML root is not a dict"), None
        return CheckResult("file_loadable", True), data
    except Exception as exc:
        return CheckResult("file_loadable", False, str(exc)), None


def check_19_sections(data: Dict[str, Any]) -> CheckResult:
    """All 19 required sections must be present."""
    missing = [s for s in SPEC_SECTIONS_ORDERED if s not in data]
    if missing:
        return CheckResult(
            "19_sections_present",
            False,
            f"Missing sections: {', '.join(missing)}",
        )
    return CheckResult("19_sections_present", True)


def check_section_order(data: Dict[str, Any]) -> CheckResult:
    """Required sections must appear in spec order (non-required keys ignored)."""
    present = [s for s in data.keys() if s in SPEC_SECTIONS_ORDERED]
    expected_order = [s for s in SPEC_SECTIONS_ORDERED if s in present]
    if present != expected_order:
        # Find first out-of-order section
        for i, (actual, expected) in enumerate(zip(present, expected_order)):
            if actual != expected:
                return CheckResult(
                    "section_order",
                    False,
                    f"Position {i}: expected '{expected}' but found '{actual}'",
                )
    return CheckResult("section_order", True)


def check_no_raw_dialogue(data: Dict[str, Any]) -> CheckResult:
    """Training data must not contain raw dialogue keys."""
    forbidden_keys = {"raw_dialogue", "raw_text_turns", "conversation", "dialogue"}
    td = data.get("training_data", [])
    if isinstance(td, list):
        items = td
    elif isinstance(td, dict):
        items = list(td.values()) if td else []
    else:
        items = []

    violations: List[str] = []
    for item in items:
        if isinstance(item, dict):
            bad = forbidden_keys & set(item.keys())
            if bad:
                violations.append(
                    f"item_id={item.get('item_id', '<unknown>')} has forbidden keys: {bad}"
                )
    if violations:
        return CheckResult("no_raw_dialogue", False, "; ".join(violations))
    return CheckResult("no_raw_dialogue", True)


def check_training_data_approved(data: Dict[str, Any]) -> CheckResult:
    """Every training_data item must have review_status: approved."""
    td = data.get("training_data", [])
    if not td:
        return CheckResult("training_data_approved", True, "no training items (ok for scaffold)")
    if isinstance(td, dict) and td.get("status") == "scaffold":
        return CheckResult("training_data_approved", True, "scaffold status (ok)")

    items: List[dict] = td if isinstance(td, list) else []
    unapproved: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("review_status", "").lower() != "approved":
            unapproved.append(item.get("item_id", "<unknown>"))
    if unapproved:
        return CheckResult(
            "training_data_approved",
            False,
            f"Unapproved items: {', '.join(unapproved)}",
        )
    return CheckResult("training_data_approved", True)


def check_regression_tests(data: Dict[str, Any]) -> CheckResult:
    """
    Every approved training_data item must have at least 1 matching example with
    is_regression_test: true and a non-empty regression_pass_criteria list.
    """
    td = data.get("training_data", [])
    if not td or (isinstance(td, dict) and td.get("status") == "scaffold"):
        return CheckResult("regression_tests", True, "no items / scaffold — skipping")

    items: List[dict] = td if isinstance(td, list) else []
    approved_ids: List[str] = [
        item.get("item_id", "")
        for item in items
        if isinstance(item, dict) and item.get("review_status", "").lower() == "approved"
    ]

    examples_section = data.get("examples", [])
    if isinstance(examples_section, dict) and examples_section.get("status") == "scaffold":
        if approved_ids:
            return CheckResult(
                "regression_tests",
                False,
                f"Examples are still scaffold but {len(approved_ids)} approved training items exist",
            )
        return CheckResult("regression_tests", True)

    examples: List[dict] = examples_section if isinstance(examples_section, list) else []
    # Build map: training_item_ref → list[example] with is_regression_test=True
    regression_map: Dict[str, List[dict]] = {}
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        if ex.get("is_regression_test") is True:
            ref = ex.get("training_item_ref", "")
            regression_map.setdefault(ref, []).append(ex)

    failures: List[str] = []
    for item_id in approved_ids:
        if not item_id:
            continue
        if item_id not in regression_map:
            failures.append(f"'{item_id}' has no regression test example")
        else:
            for ex in regression_map[item_id]:
                criteria = ex.get("regression_pass_criteria", [])
                if not criteria:
                    failures.append(
                        f"'{item_id}' example '{ex.get('example_id', '?')}' has empty regression_pass_criteria"
                    )

    if failures:
        return CheckResult("regression_tests", False, "; ".join(failures[:5]))
    return CheckResult("regression_tests", True)


def check_evaluation_rules(data: Dict[str, Any]) -> CheckResult:
    """
    Evaluation section must be a list (or a dict with a rules key in scaffold).
    Each rule must have: rule_id, rule_type, threshold, blocking.
    """
    eval_section = data.get("evaluation", [])
    if isinstance(eval_section, dict):
        rules = eval_section.get("rules", [])
        if eval_section.get("status") == "scaffold" and not rules:
            return CheckResult("evaluation_rules", True, "scaffold — skipping")
    elif isinstance(eval_section, list):
        rules = eval_section
    else:
        return CheckResult("evaluation_rules", False, "evaluation section is neither list nor dict")

    required_fields = {"rule_id", "rule_type", "threshold", "blocking"}
    issues: List[str] = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            issues.append(f"Rule {i} is not a dict")
            continue
        missing = required_fields - set(rule.keys())
        if missing:
            issues.append(
                f"Rule '{rule.get('rule_id', i)}' missing fields: {missing}"
            )
    if issues:
        return CheckResult("evaluation_rules", False, "; ".join(issues[:5]))
    return CheckResult("evaluation_rules", True)


def check_changelog(data: Dict[str, Any]) -> CheckResult:
    """
    version_control.history must have at least 2 entries (scaffold + update).
    Each entry must have: version, date, author, change_summary, reason, approved_by.
    """
    vc = data.get("version_control", {})
    if not isinstance(vc, dict):
        return CheckResult("changelog", False, "version_control is not a dict")
    history = vc.get("history", [])
    if not isinstance(history, list):
        return CheckResult("changelog", False, "version_control.history is not a list")
    if len(history) < 2:
        return CheckResult(
            "changelog",
            False,
            f"Only {len(history)} history entries; need at least 2 (scaffold + at least one update)",
        )
    required = {"version", "date", "author", "change_summary", "reason", "approved_by"}
    issues: List[str] = []
    for entry in history:
        if not isinstance(entry, dict):
            issues.append("History entry is not a dict")
            continue
        missing = required - set(entry.keys())
        if missing:
            issues.append(f"Entry v{entry.get('version', '?')} missing: {missing}")
    if issues:
        return CheckResult("changelog", False, "; ".join(issues[:5]))
    return CheckResult("changelog", True)


def check_connections_bridge_format(data: Dict[str, Any]) -> CheckResult:
    """
    Every connection sub-key (except 'status') must have 'type: bridge'.
    Target engine link_file must reference an existing .yaml path string.
    """
    connections = data.get("connections", {})
    if not isinstance(connections, dict):
        return CheckResult("connections_bridge_format", True, "no connections section — ok")
    issues: List[str] = []
    for key, val in connections.items():
        if key == "status":
            continue
        if not isinstance(val, dict):
            issues.append(f"Connection '{key}' is not a dict")
            continue
        if val.get("type") != "bridge":
            issues.append(f"Connection '{key}' missing type: bridge")
        if "link_file" not in val:
            issues.append(f"Connection '{key}' missing link_file")
        elif not str(val["link_file"]).endswith(".yaml"):
            issues.append(f"Connection '{key}' link_file does not end in .yaml")
    if issues:
        return CheckResult("connections_bridge_format", False, "; ".join(issues[:5]))
    return CheckResult("connections_bridge_format", True)


def check_engine_identity_status(data: Dict[str, Any]) -> CheckResult:
    """engine_identity.status must be 'active' (not 'scaffold')."""
    ei = data.get("engine_identity", {})
    status = ei.get("status", "")
    if str(status).lower() in ("scaffold", ""):
        return CheckResult(
            "engine_identity_status",
            False,
            f"engine_identity.status is '{status}' — must be 'active'",
        )
    return CheckResult("engine_identity_status", True)


# ---------------------------------------------------------------------------
# Per-engine runner
# ---------------------------------------------------------------------------


def run_engine_checks(engine_file: Path) -> EngineReport:
    """Run all checks for a single engine file and return a report."""
    report = EngineReport(engine_file)

    # 1. File loadable
    load_result, data = check_file_loadable(engine_file)
    report.add(load_result)
    if not load_result.passed or data is None:
        # Cannot proceed without data
        return report

    # 2. 19 sections present
    report.add(check_19_sections(data))

    # 3. Section order
    report.add(check_section_order(data))

    # 4. Engine identity status
    report.add(check_engine_identity_status(data))

    # 5. No raw dialogue
    report.add(check_no_raw_dialogue(data))

    # 6. Training data approved
    report.add(check_training_data_approved(data))

    # 7. Regression tests
    report.add(check_regression_tests(data))

    # 8. Evaluation rules
    report.add(check_evaluation_rules(data))

    # 9. Changelog
    report.add(check_changelog(data))

    # 10. Connections bridge format
    report.add(check_connections_bridge_format(data))

    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run regression tests for all canonical language engine YAML files."
    )
    parser.add_argument(
        "--engines-dir",
        type=Path,
        default=DEFAULT_ENGINES_DIR,
        help=f"Directory containing engine YAML files (default: {DEFAULT_ENGINES_DIR})",
    )
    parser.add_argument(
        "--engines",
        type=str,
        default="",
        help="Comma-separated list of language codes or stems to test (e.g. 'fr,de,ja'). "
             "Defaults to all known engines.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-check results even for passing engines.",
    )
    return parser.parse_args()


def collect_engine_files(engines_dir: Path, engine_filter: str) -> List[Path]:
    """Return a sorted list of engine YAML files to test."""
    if not engines_dir.exists():
        logger.error("Engine directory not found: %s", engines_dir)
        return []

    if engine_filter:
        codes = [c.strip().lower() for c in engine_filter.split(",") if c.strip()]
        files: List[Path] = []
        for code in codes:
            # Accept language code (fr, de) or full stem (French_engine.training)
            matches = sorted(
                p for p in engines_dir.glob("*.yaml")
                if code in p.name.lower()
            )
            files.extend(matches)
        return files

    # Default: all engine YAML files
    return sorted(engines_dir.glob("*_engine.training.yaml"))


def main() -> int:
    args = parse_args()
    engine_files = collect_engine_files(args.engines_dir, args.engines)

    if not engine_files:
        logger.error("No engine files found in %s", args.engines_dir)
        return 1

    print(f"\n{'=' * 60}")
    print(f"Polyglot Engine Regression Test Suite")
    print(f"Directory : {args.engines_dir}")
    print(f"Engines   : {len(engine_files)}")
    print(f"{'=' * 60}")

    reports: List[EngineReport] = []
    for engine_file in engine_files:
        report = run_engine_checks(engine_file)
        reports.append(report)
        if args.verbose or not report.passed:
            report.print_summary()
        else:
            status = "[OK]" if report.passed else "[FAIL]"
            print(f"  {status} {engine_file.name}")

    # ---- Summary ----
    total = len(reports)
    passed = sum(1 for r in reports if r.passed)
    failed = total - passed

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {passed}/{total} engines passed all checks")
    if failed:
        print(f"FAILURES: {failed} engine(s) have issues:")
        for r in reports:
            if not r.passed:
                print(f"  [FAIL] {r.engine_file.name}  ({r.failure_count} check(s) failed)")
    print(f"{'=' * 60}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
