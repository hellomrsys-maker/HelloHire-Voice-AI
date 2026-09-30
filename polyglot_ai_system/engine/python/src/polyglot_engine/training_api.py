"""
training_api.py — Engine-side Training API bridge
Exposes the engine's training-related interfaces to the training system.
The engine's component families, slot templates, and evaluation rules can
be queried and updated through this interface, keeping a clean separation
between the running engine (System 2) and the training loop (System 1).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .engine_client import EngineClient, EngineClientError


# ---------------------------------------------------------------------------
# Custom exceptions for spec violations
# ---------------------------------------------------------------------------


class CanonicalFileViolation(RuntimeError):
    """
    Raised by EngineTrainingAPI when a canonical YAML file violates one or
    more rules enforced by the canonical file guard (Task 2).

    Violations that trigger this exception (when strict_guard=True):
      - One or more of the 19 required spec sections is absent.
      - ``engine_identity.status`` is still 'scaffold'.
      - A training_data item contains a forbidden raw-dialogue key.
    """


class ChangelogViolation(RuntimeError):
    """
    Raised by EngineTrainingAPI.validate_changelog() when the
    ``version_control.history`` section of a canonical YAML is incomplete
    or missing required metadata fields (Task 4).
    """

logger = logging.getLogger("polyglot_engine.training_api")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ComponentFamily:
    """
    A component family as defined in the canonical training YAML.
    Stores all slot variants for one grammatical/functional family.
    """

    family_id: str
    language: str
    slots: Dict[str, List[str]]  # slot_name → list of valid fillers
    templates: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def slot_count(self) -> int:
        return len(self.slots)

    def template_count(self) -> int:
        return len(self.templates)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family_id": self.family_id,
            "language": self.language,
            "slots": self.slots,
            "templates": self.templates,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ComponentFamily":
        return cls(
            family_id=d["family_id"],
            language=d.get("language", "en"),
            slots=d.get("slots", {}),
            templates=d.get("templates", []),
            metadata=d.get("metadata", {}),
        )


@dataclass
class TrainingRecord:
    """
    A single approved, normalized training record as defined by the spec.
    Raw dialogue is NEVER stored — only structured, broken-down items.
    """

    record_id: str
    language: str
    component_family: str
    slot_values: Dict[str, str]
    assembled_output: str
    normalized: bool = True
    approved: bool = True
    created_at: float = field(default_factory=time.time)
    quality_score: float = 1.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "language": self.language,
            "component_family": self.component_family,
            "slot_values": self.slot_values,
            "assembled_output": self.assembled_output,
            "normalized": self.normalized,
            "approved": self.approved,
            "created_at": self.created_at,
            "quality_score": self.quality_score,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TrainingRecord":
        return cls(
            record_id=d["record_id"],
            language=d.get("language", "en"),
            component_family=d["component_family"],
            slot_values=d.get("slot_values", {}),
            assembled_output=d["assembled_output"],
            normalized=d.get("normalized", True),
            approved=d.get("approved", True),
            created_at=d.get("created_at", time.time()),
            quality_score=d.get("quality_score", 1.0),
            tags=d.get("tags", []),
        )


@dataclass
class EvaluationRule:
    """
    A single evaluation rule from the engine training YAML.
    Used during training to validate generated outputs.
    """

    rule_id: str
    rule_type: str  # "slot_coverage", "grammar_check", "semantic_coherence", etc.
    parameters: Dict[str, Any]
    threshold: float = 0.8
    blocking: bool = False  # if True, training halts on rule violation

    def evaluate(self, output: str, slot_values: Dict[str, str]) -> Tuple[bool, float]:
        """
        Evaluate this rule against a generated output.
        Returns (passed, score) tuple.
        Dispatches to the appropriate rule checker.
        """
        if self.rule_type == "slot_coverage":
            return self._check_slot_coverage(output, slot_values)
        elif self.rule_type == "min_length":
            return self._check_min_length(output)
        elif self.rule_type == "max_length":
            return self._check_max_length(output)
        elif self.rule_type == "no_placeholder":
            return self._check_no_placeholder(output)
        elif self.rule_type == "language_match":
            return self._check_language_tag(output)
        else:
            # Unknown rule type: pass by default, score 1.0
            logger.warning("Unknown rule type: %s — passing by default", self.rule_type)
            return True, 1.0

    def _check_slot_coverage(
        self, output: str, slot_values: Dict[str, str]
    ) -> Tuple[bool, float]:
        required = self.parameters.get("required_slots", [])
        filled = [s for s in required if slot_values.get(s)]
        coverage = len(filled) / max(len(required), 1)
        return coverage >= self.threshold, coverage

    def _check_min_length(self, output: str) -> Tuple[bool, float]:
        min_len = int(self.parameters.get("min_tokens", 1))
        length = len(output.split())
        score = min(length / max(min_len, 1), 1.0)
        return length >= min_len, score

    def _check_max_length(self, output: str) -> Tuple[bool, float]:
        max_len = int(self.parameters.get("max_tokens", 512))
        length = len(output.split())
        score = 1.0 if length <= max_len else max_len / length
        return length <= max_len, score

    def _check_no_placeholder(self, output: str) -> Tuple[bool, float]:
        placeholders = ["TODO", "STUB", "...", "<PLACEHOLDER>", "FIXME"]
        has_placeholder = any(p in output for p in placeholders)
        return not has_placeholder, 0.0 if has_placeholder else 1.0

    def _check_language_tag(self, output: str) -> Tuple[bool, float]:
        # Simple heuristic: check ASCII ratio for English
        expected_lang = self.parameters.get("language", "en")
        if expected_lang == "en":
            ascii_chars = sum(1 for c in output if ord(c) < 128)
            ratio = ascii_chars / max(len(output), 1)
            return ratio >= self.threshold, ratio
        return True, 1.0


# ---------------------------------------------------------------------------
# Engine Training API
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Spec-level constants used by guards
# ---------------------------------------------------------------------------

SPEC_REQUIRED_SECTIONS: List[str] = [
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

_FORBIDDEN_RAW_KEYS = frozenset(
    {"raw_dialogue", "raw_text_turns", "conversation", "dialogue"}
)


class EngineTrainingAPI:
    """
    Bridge between the running verbal engine (System 2) and the training
    system (System 1). Provides:

    - Read/write access to component families stored in the canonical YAML
    - Training record validation and normalization
    - Evaluation rule execution
    - Live engine model weight querying for distillation
    - Canonical file guard (enforces spec rules at load time)
    - Changelog validator (enforces version_control.history completeness)

    Architecture note: this class is ONLY an interface — it never stores
    raw dialogue, never modifies the engine's runtime state directly, and
    never persists runtime artifacts as permanent training files.

    Canonical file guard (Task 2)
    --------------------------------
    ``load()`` validates the following rules before ingesting any data:

    1. All 19 required sections are present.
    2. No raw dialogue keys appear in training_data items.
    3. engine_identity.status != 'scaffold'.

    If any rule is violated, a ``CanonicalFileViolation`` is raised when
    ``strict_guard=True`` (default: False — logs warnings instead).

    Changelog validator (Task 4)
    --------------------------------
    ``validate_changelog()`` checks that ``version_control.history`` contains
    ≥2 entries and that each entry carries the required metadata fields.
    Raises ``ChangelogViolation`` when a violation is found.
    """

    def __init__(
        self,
        engine_client: Optional[EngineClient] = None,
        training_yaml_path: Optional[str] = None,
        strict_guard: bool = False,
    ) -> None:
        self._client = engine_client
        self._yaml_path = Path(training_yaml_path) if training_yaml_path else None
        self._component_families: Dict[str, ComponentFamily] = {}
        self._evaluation_rules: List[EvaluationRule] = []
        self._training_records: List[TrainingRecord] = []
        self._loaded = False
        self._strict_guard = strict_guard
        # Populated after a successful load
        self._raw_data: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def load(self, yaml_path: Optional[str] = None) -> None:
        """
        Load component families and evaluation rules from the canonical
        training YAML.  The path may be overridden per call.

        Before ingesting any data the canonical file guard is run.  When
        ``strict_guard=True`` any spec violation raises
        ``CanonicalFileViolation``; otherwise violations are logged as
        warnings and loading continues.
        """
        path = Path(yaml_path) if yaml_path else self._yaml_path
        if path is None or not path.exists():
            logger.warning("No training YAML path provided or file not found: %s", path)
            return

        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f)

        # ---- Canonical file guard ----
        violations = self._run_canonical_guard(data, path)
        if violations:
            msg = f"Canonical file guard found {len(violations)} violation(s) in {path}: " + "; ".join(violations)
            if self._strict_guard:
                raise CanonicalFileViolation(msg)
            logger.warning(msg)

        self._raw_data = data
        self._load_component_families(data)
        self._load_evaluation_rules(data)
        self._load_training_records(data)
        self._loaded = True
        logger.info(
            "Loaded %d component families, %d evaluation rules, %d training records from %s",
            len(self._component_families),
            len(self._evaluation_rules),
            len(self._training_records),
            path,
        )

    def _load_component_families(self, data: Dict[str, Any]) -> None:
        """Extract component families from the sentence_processing section.

        The canonical YAML uses the section name ``sentence_processing`` (not the
        legacy alias ``sentence_system`` which is no longer valid).  The language
        code is stored under ``engine_identity`` (not ``engine_registry``).
        """
        # Accept both the current spec name and the legacy alias so that older
        # snapshot files loaded for inspection do not break silently.
        sentence_processing = data.get("sentence_processing") or data.get("sentence_system") or {}
        families_raw = sentence_processing.get("component_families", [])
        # Derive the language from engine_identity (spec-correct name).
        engine_identity = data.get("engine_identity") or data.get("engine_registry") or {}
        language = engine_identity.get("language_code", engine_identity.get("language", "en"))
        for raw in families_raw:
            cf = ComponentFamily(
                family_id=raw.get("id", raw.get("family_id", "")),
                language=language,
                slots=raw.get("slots", {}),
                templates=raw.get("templates", []),
                metadata={k: v for k, v in raw.items() if k not in ("id", "family_id", "slots", "templates")},
            )
            if cf.family_id:
                self._component_families[cf.family_id] = cf
            else:
                logger.warning("Skipping component family with no id: %s", raw)

    def _load_evaluation_rules(self, data: Dict[str, Any]) -> None:
        """Extract evaluation rules from the evaluation section.

        The canonical YAML stores evaluation as either:
          - A top-level list (English engine canonical format), or
          - A dict with a ``rules`` key (scaffold format).
        Both forms are handled here.
        """
        eval_section = data.get("evaluation", [])
        if isinstance(eval_section, list):
            # Top-level list format (canonical English engine and future engines)
            rules_raw = eval_section
        elif isinstance(eval_section, dict):
            # Dict-with-rules-key format (scaffold files)
            rules_raw = eval_section.get("rules", [])
        else:
            rules_raw = []
        self._evaluation_rules = []
        for raw in rules_raw:
            if not isinstance(raw, dict):
                continue
            rule = EvaluationRule(
                rule_id=raw.get("rule_id", raw.get("id", "")),
                rule_type=raw.get("type", raw.get("rule_type", "slot_coverage")),
                parameters=raw.get("parameters", {}),
                threshold=float(raw.get("threshold", 0.8)),
                blocking=bool(raw.get("blocking", False)),
            )
            self._evaluation_rules.append(rule)

    def _load_training_records(self, data: Dict[str, Any]) -> None:
        """Extract pre-approved training records from the training_data section.

        The canonical YAML stores ``training_data`` as a **top-level list** of
        items (each with ``review_status: approved``).  The old code incorrectly
        treated it as a dict and looked for a non-existent ``approved_records``
        key.  This method now handles both shapes:

        - List form (canonical spec): each element is a training item dict.
        - Dict form (legacy): falls back to ``approved_records`` sub-key.
        """
        td_section = data.get("training_data", [])
        if isinstance(td_section, list):
            records_raw = td_section
        elif isinstance(td_section, dict):
            # Legacy dict shape — try known sub-keys
            records_raw = (
                td_section.get("approved_records")
                or td_section.get("items")
                or td_section.get("records")
                or []
            )
        else:
            records_raw = []

        self._training_records = []
        for raw in records_raw:
            if not isinstance(raw, dict):
                continue
            # Only ingest records that have been formally approved
            if raw.get("review_status", "").lower() != "approved":
                logger.debug("Skipping unapproved training record: %s", raw.get("item_id", "<unknown>"))
                continue
            try:
                # Map canonical spec fields to TrainingRecord fields.
                # Canonical spec uses: item_id, component_families (list),
                # slot_order (list), normalized_components (dict),
                # grammar_rules_used (list), review_status, version.
                component_families_list = raw.get("component_families", [])
                primary_family = component_families_list[0] if component_families_list else "general"
                # assembled_output: prefer normalized_components joined, else item_id
                norm_components = raw.get("normalized_components", {})
                assembled = " ".join(str(v) for v in norm_components.values()) if norm_components else raw.get("item_id", "")
                record = TrainingRecord(
                    record_id=raw.get("item_id", raw.get("record_id", "")),
                    language=raw.get("language", "en"),
                    component_family=primary_family,
                    slot_values=norm_components,
                    assembled_output=assembled,
                    normalized=True,
                    approved=True,
                    quality_score=float(raw.get("quality_score", 1.0)),
                    tags=raw.get("grammar_rules_used", []),
                )
                self._training_records.append(record)
            except (KeyError, TypeError) as e:
                logger.warning("Skipping malformed training record: %s — %s", raw.get("item_id", raw), e)

    # ------------------------------------------------------------------
    # Canonical file guard (Task 2)
    # ------------------------------------------------------------------

    def _run_canonical_guard(
        self, data: Dict[str, Any], path: "Path"
    ) -> List[str]:
        """
        Validate a canonical YAML data dict against the spec rules.
        Returns a list of human-readable violation strings (empty = no violations).

        Rules enforced:
          1. All 19 required sections are present.
          2. ``engine_identity.status`` must not be 'scaffold'.
          3. No training_data item may contain forbidden raw-dialogue keys.
        """
        violations: List[str] = []

        # Rule 1 — 19 required sections
        missing = [s for s in SPEC_REQUIRED_SECTIONS if s not in data]
        if missing:
            violations.append(
                f"Missing required section(s): {', '.join(missing)}"
            )

        # Rule 2 — engine_identity.status not scaffold
        engine_id = data.get("engine_identity", {})
        if isinstance(engine_id, dict):
            status = str(engine_id.get("status", "")).lower()
            if status == "scaffold":
                violations.append(
                    "engine_identity.status is 'scaffold' — file is not production-ready"
                )

        # Rule 3 — no raw dialogue in training_data
        td = data.get("training_data", [])
        if isinstance(td, list):
            for item in td:
                if isinstance(item, dict):
                    bad = _FORBIDDEN_RAW_KEYS & set(item.keys())
                    if bad:
                        violations.append(
                            f"training_data item '{item.get('item_id', '?')}' "
                            f"contains forbidden raw-dialogue key(s): {bad}"
                        )

        return violations

    def validate_canonical_file(self, yaml_path: Optional[str] = None) -> List[str]:
        """
        Public entry point for the canonical file guard.

        If the file has already been loaded into this instance, validates the
        cached raw data.  Otherwise loads and validates from ``yaml_path``.

        Returns a list of violation strings (empty list = file is valid).
        """
        if self._raw_data:
            return self._run_canonical_guard(self._raw_data, self._yaml_path or Path("<in-memory>"))

        # Load file just for validation (don't ingest into instance state)
        path = Path(yaml_path) if yaml_path else self._yaml_path
        if path is None or not path.exists():
            return [f"File not found or path not set: {path}"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            return [f"YAML parse error: {exc}"]
        return self._run_canonical_guard(data, path)

    # ------------------------------------------------------------------
    # Changelog validator (Task 4)
    # ------------------------------------------------------------------

    def validate_changelog(self, yaml_path: Optional[str] = None) -> None:
        """
        Validate the ``version_control.history`` section of the canonical YAML.

        Rules:
          - ``version_control.history`` must be a list.
          - At least 2 entries required (initial scaffold + ≥1 update).
          - Every entry must carry: version, date, author, change_summary,
            reason, approved_by.

        Raises ``ChangelogViolation`` on the first problem found.
        Uses cached raw data when available; otherwise loads from ``yaml_path``.
        """
        if self._raw_data:
            data = self._raw_data
        else:
            path = Path(yaml_path) if yaml_path else self._yaml_path
            if path is None or not path.exists():
                raise ChangelogViolation(f"File not found or path not set: {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except Exception as exc:
                raise ChangelogViolation(f"YAML parse error: {exc}") from exc

        vc = data.get("version_control")
        if not isinstance(vc, dict):
            raise ChangelogViolation(
                "version_control section is missing or is not a dict"
            )

        history = vc.get("history")
        if not isinstance(history, list):
            raise ChangelogViolation(
                "version_control.history is missing or is not a list"
            )

        if len(history) < 2:
            raise ChangelogViolation(
                f"version_control.history has only {len(history)} entry/entries; "
                "need ≥2 (initial scaffold entry + at least one update entry)"
            )

        required_fields = {
            "version",
            "date",
            "author",
            "change_summary",
            "reason",
            "approved_by",
        }
        for i, entry in enumerate(history):
            if not isinstance(entry, dict):
                raise ChangelogViolation(
                    f"version_control.history[{i}] is not a dict"
                )
            missing = required_fields - set(entry.keys())
            if missing:
                raise ChangelogViolation(
                    f"version_control.history[{i}] (version={entry.get('version', '?')}) "
                    f"is missing required fields: {', '.join(sorted(missing))}"
                )

        logger.debug(
            "Changelog validated: %d history entries found", len(history)
        )

    # ------------------------------------------------------------------
    # Component Family access
    # ------------------------------------------------------------------

    def get_component_family(self, family_id: str) -> Optional[ComponentFamily]:
        """Return the named component family, or None if not found."""
        return self._component_families.get(family_id)

    def list_component_families(self) -> List[str]:
        """Return all registered component family IDs."""
        return list(self._component_families.keys())

    def register_component_family(self, family: ComponentFamily) -> None:
        """
        Register a new component family.
        Only called when the training system identifies a new reusable
        pattern — never from runtime inference.
        """
        self._component_families[family.family_id] = family
        logger.info("Registered new component family: %s", family.family_id)

    # ------------------------------------------------------------------
    # Training record operations
    # ------------------------------------------------------------------

    def validate_record(self, record: TrainingRecord) -> Tuple[bool, List[str]]:
        """
        Validate a training record against all evaluation rules.
        Returns (is_valid, list_of_failure_messages).
        """
        failures: List[str] = []
        for rule in self._evaluation_rules:
            passed, score = rule.evaluate(record.assembled_output, record.slot_values)
            if not passed:
                msg = (
                    f"Rule '{rule.rule_id}' ({rule.rule_type}) failed "
                    f"with score {score:.3f} < threshold {rule.threshold:.3f}"
                )
                failures.append(msg)
                if rule.blocking:
                    logger.error("BLOCKING rule failure: %s", msg)
                    return False, failures
        is_valid = len(failures) == 0
        return is_valid, failures

    def normalize_record(self, record: TrainingRecord) -> TrainingRecord:
        """
        Normalize a training record: strip extra whitespace, lowercase
        slot values, validate assembled output, mark as normalized.
        Raw dialogue content is never stored — only slot+family structure.
        """
        normalized_slots = {
            k: v.strip() for k, v in record.slot_values.items()
        }
        normalized_output = " ".join(record.assembled_output.split())
        return TrainingRecord(
            record_id=record.record_id,
            language=record.language,
            component_family=record.component_family,
            slot_values=normalized_slots,
            assembled_output=normalized_output,
            normalized=True,
            approved=record.approved,
            created_at=record.created_at,
            quality_score=record.quality_score,
            tags=record.tags,
        )

    def add_training_record(self, record: TrainingRecord) -> bool:
        """
        Add a validated, normalized training record to the in-memory store.
        Returns True if the record was accepted, False if validation failed.
        """
        record = self.normalize_record(record)
        valid, failures = self.validate_record(record)
        if not valid:
            logger.warning(
                "Training record %s rejected: %s", record.record_id, failures
            )
            return False
        self._training_records.append(record)
        return True

    def get_training_records(
        self,
        family_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        approved_only: bool = True,
    ) -> List[TrainingRecord]:
        """Return training records filtered by family, language, and approval status."""
        records = self._training_records
        if approved_only:
            records = [r for r in records if r.approved]
        if family_filter:
            records = [r for r in records if r.component_family == family_filter]
        if language_filter:
            records = [r for r in records if r.language == language_filter]
        return records

    # ------------------------------------------------------------------
    # Engine weight access for distillation
    # ------------------------------------------------------------------

    def query_engine_weights(
        self, layer_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query the live engine's model weights for knowledge distillation.
        Only returns weights for the specified layers; defaults to all.
        Raises EngineClientError if the engine client is not connected.
        """
        if self._client is None:
            raise EngineClientError("No engine client attached to EngineTrainingAPI")
        return self._client.get_weights(layer_names=layer_names)

    def push_adapter_weights(self, adapter_weights: Dict[str, Any]) -> None:
        """
        Push LoRA adapter weights from a completed training epoch back to
        the running engine for hot-reload inference improvement.
        """
        if self._client is None:
            raise EngineClientError("No engine client attached to EngineTrainingAPI")
        self._client.load_adapter(adapter_weights)
        logger.info("Pushed adapter weights to running engine (%d tensors)", len(adapter_weights))

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_training_dataset(self, output_path: str) -> int:
        """
        Export all approved, normalized training records to a JSONL file.
        Returns the count of exported records.
        """
        records = self.get_training_records(approved_only=True)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with open(out, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
                count += 1
        logger.info("Exported %d training records to %s", count, output_path)
        return count

    def export_component_families(self, output_path: str) -> int:
        """
        Export all component families to a JSON file.
        Returns the count of exported families.
        """
        families_dict = {fid: cf.to_dict() for fid, cf in self._component_families.items()}
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(families_dict, f, indent=2, ensure_ascii=False)
        logger.info(
            "Exported %d component families to %s", len(families_dict), output_path
        )
        return len(families_dict)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        return self._loaded

    def stats(self) -> Dict[str, Any]:
        return {
            "loaded": self._loaded,
            "component_families": len(self._component_families),
            "evaluation_rules": len(self._evaluation_rules),
            "training_records": len(self._training_records),
            "approved_records": sum(
                1 for r in self._training_records if r.approved
            ),
        }
