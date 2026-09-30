# =============================================================================
# engine/python/src/polyglot_engine/language_engine.py
# Canonical language engine training file loader.
# Implements the spec: one canonical training file per language engine.
# =============================================================================

from __future__ import annotations

import yaml
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import hashlib
import re

logger = logging.getLogger(__name__)

# =============================================================================
# Data classes matching the spec's training file structure
# =============================================================================

@dataclass
class EngineRegistry:
    engine_id:            str
    language_name:        str
    language_code:        str
    writing_systems:      list[str]
    language_family:      str
    supported_variants:   list[str]
    canonical_training_file: str


@dataclass
class ComponentFamilyEntry:
    """Single entry in a component family (per spec Section 5 and 6)."""
    id:               str
    forms:            list[str]
    register:         str          # neutral | formal | informal | technical
    creativity_weight: float = 1.0
    is_fixed_expression: bool = False


@dataclass
class ComponentFamily:
    """A named family of interchangeable sentence components."""
    family_name:  str
    entries:      list[ComponentFamilyEntry]
    is_optional:  bool  = False
    description:  str   = ""


@dataclass
class SentenceTemplate:
    """
    A slot-order template that combines component families.
    Per spec: compositions of families, not memorized full sentences.
    """
    template_id:           str
    communication_intent:  str
    slot_order:            list[str]
    blocked_combinations:  list[str]
    default_register:      str = "neutral"


@dataclass
class TrainingItem:
    """
    A single training item following the spec's training record format.
    Per spec Section 6: every training item must follow this internal tree.
    """
    item_id:              str
    language:             str
    source:               dict[str, str]
    communication_intent: str
    meaning_frame:        str

    # Component families for this item
    component_families:   dict[str, ComponentFamily] = field(default_factory=dict)
    slot_order:           list[str]                  = field(default_factory=list)
    allowed_combinations: list[str]                  = field(default_factory=list)
    blocked_combinations: list[str]                  = field(default_factory=list)

    # Per-spec required fields
    normalized_components:  list[str] = field(default_factory=list)
    sentence_breakdown:     str       = ""
    literal_meaning:        str       = ""
    natural_meaning:        str       = ""
    grammar_rules_used:     list[str] = field(default_factory=list)
    vocabulary:             list[str] = field(default_factory=list)
    pronunciation:          dict      = field(default_factory=dict)
    register:               str       = "neutral"
    dialect:                str       = "standard"
    generated_examples:     list[str] = field(default_factory=list)
    fixed_exceptions:       list[str] = field(default_factory=list)
    explanation:            str       = ""
    confidence:             float     = 1.0
    review_status:          str       = "approved"
    version:                str       = "1.0"


@dataclass
class EvaluationRule:
    """An evaluation rule (per spec section: evaluation)."""
    rule_id:     str
    category:    str       # grammar_accuracy | meaning_accuracy | etc.
    description: str
    test_cases:  list[dict]
    passing_threshold: float = 0.9


@dataclass
class CanonicalEngineFile:
    """
    The complete canonical training file for one language engine.
    Per spec: ONE ENGINE = ONE CANONICAL TRAINING FILE.

    This Python representation mirrors the full YAML structure.
    """

    # Registry
    engine_registry:   EngineRegistry

    # AI Core
    artificial_intelligence_core: dict[str, Any]

    # Brain
    brain: dict[str, Any]

    # Skills
    skills: dict[str, Any]

    # Creativity
    creativity: dict[str, Any]

    # Language engine
    language_engine: dict[str, Any]

    # Sentence system
    sentence_system: SentenceSystemSection

    # Training data
    training_data: list[TrainingItem]

    # Evaluation
    evaluation: list[EvaluationRule]

    # Connections
    connections: dict[str, Any]

    # Governance
    governance: dict[str, Any]

    # File metadata
    file_path: str       = ""
    file_hash: str       = ""
    version:   str       = "1.0"


@dataclass
class SentenceSystemSection:
    """
    The sentence_system section of the canonical engine file.
    Contains component families and sentence templates.
    Per spec: stores reusable parts and their relationships.
    """
    families:   dict[str, ComponentFamily]
    templates:  dict[str, SentenceTemplate]
    rules:      list[dict]   # Combination rules
    fixed_expressions: list[dict]  # Idioms, quotes, etc.


# =============================================================================
# LanguageEngineLoader
# =============================================================================

class LanguageEngineLoader:
    """
    Loads and parses a canonical language engine training YAML file.
    Per spec: one canonical file per engine; all capabilities inside that file.

    Enforces the single-file rule: raises ValueError if the file is missing
    required sections.

    Example:
        >>> loader = LanguageEngineLoader()
        >>> engine_file = loader.load("language_engines/English_engine.training.yaml")
        >>> print(engine_file.engine_registry.language_name)
        'English'
    """

    # Required top-level sections per the spec
    REQUIRED_SECTIONS = [
        "engine_registry",
        "artificial_intelligence_core",
        "brain",
        "skills",
        "creativity",
        "language_engine",
        "sentence_system",
        "training_data",
        "evaluation",
        "connections",
        "governance",
    ]

    def load(self, file_path: str | Path) -> CanonicalEngineFile:
        """
        Loads and validates a canonical engine training YAML file.

        Args:
            file_path: Path to the .yaml / .json / .toml training file.

        Returns:
            CanonicalEngineFile with all sections populated.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If required sections are missing.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Engine training file not found: {path}")

        raw = path.read_text(encoding="utf-8")
        file_hash = hashlib.sha256(raw.encode()).hexdigest()

        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            data = yaml.safe_load(raw)
        elif suffix == ".json":
            data = json.loads(raw)
        else:
            raise ValueError(f"Unsupported training file format: {suffix}")

        # Validate required sections
        missing = [s for s in self.REQUIRED_SECTIONS if s not in data]
        if missing:
            raise ValueError(
                f"Canonical engine file missing required sections: {missing}\n"
                f"File: {path}\n"
                "Per spec: every section must be present in the canonical training file."
            )

        return self._parse(data, str(path), file_hash)

    def load_or_create_default(self, file_path: str | Path) -> CanonicalEngineFile:
        """
        Loads the file if it exists; creates and saves a default English engine
        file if not.
        """
        path = Path(file_path)
        if not path.exists():
            logger.info("Training file not found — creating default: %s", path)
            self._create_default_file(path)
        return self.load(path)

    # -------------------------------------------------------------------------
    # Parsing helpers
    # -------------------------------------------------------------------------

    def _parse(self, data: dict, file_path: str, file_hash: str) -> CanonicalEngineFile:
        registry_data = data.get("engine_registry", {})
        registry = EngineRegistry(
            engine_id=registry_data.get("engine_id", ""),
            language_name=registry_data.get("language_name", ""),
            language_code=registry_data.get("language_code", "en"),
            writing_systems=registry_data.get("writing_systems", ["Latin"]),
            language_family=registry_data.get("language_family", ""),
            supported_variants=registry_data.get("supported_variants", []),
            canonical_training_file=registry_data.get("canonical_training_file", file_path),
        )

        # Parse sentence system
        ss_data = data.get("sentence_system", {})
        sentence_system = self._parse_sentence_system(ss_data)

        # Parse training data
        td_list = data.get("training_data", [])
        training_items = [self._parse_training_item(td) for td in td_list
                          if isinstance(td, dict)]

        # Parse evaluation rules
        eval_list = data.get("evaluation", [])
        eval_rules = [self._parse_eval_rule(er) for er in eval_list
                      if isinstance(er, dict)]

        return CanonicalEngineFile(
            engine_registry=registry,
            artificial_intelligence_core=data.get("artificial_intelligence_core", {}),
            brain=data.get("brain", {}),
            skills=data.get("skills", {}),
            creativity=data.get("creativity", {}),
            language_engine=data.get("language_engine", {}),
            sentence_system=sentence_system,
            training_data=training_items,
            evaluation=eval_rules,
            connections=data.get("connections", {}),
            governance=data.get("governance", {}),
            file_path=file_path,
            file_hash=file_hash,
            version=data.get("version", "1.0"),
        )

    def _parse_sentence_system(self, data: dict) -> SentenceSystemSection:
        families = {}
        for fname, fdata in data.get("communication_families", {}).items():
            family = self._parse_family(fname, fdata)
            families[fname] = family

        templates = {}
        for tname, tdata in data.get("templates", {}).items():
            template = self._parse_template(tname, tdata)
            templates[tname] = template

        return SentenceSystemSection(
            families=families,
            templates=templates,
            rules=data.get("combination_rules", []),
            fixed_expressions=data.get("fixed_expressions", []),
        )

    def _parse_family(self, name: str, data: dict) -> ComponentFamily:
        entries = []
        for entry_data in data.get("entries", []):
            entries.append(ComponentFamilyEntry(
                id=entry_data.get("id", ""),
                forms=entry_data.get("forms", []),
                register=entry_data.get("register", "neutral"),
                creativity_weight=float(entry_data.get("creativity_weight", 1.0)),
                is_fixed_expression=bool(entry_data.get("is_fixed_expression", False)),
            ))
        return ComponentFamily(
            family_name=name,
            entries=entries,
            is_optional=bool(data.get("is_optional", False)),
            description=data.get("description", ""),
        )

    def _parse_template(self, name: str, data: dict) -> SentenceTemplate:
        return SentenceTemplate(
            template_id=name,
            communication_intent=data.get("communication_intent", ""),
            slot_order=data.get("slot_order", []),
            blocked_combinations=data.get("blocked_combinations", []),
            default_register=data.get("default_register", "neutral"),
        )

    def _parse_training_item(self, data: dict) -> TrainingItem:
        families = {}
        for fname, fdata in data.get("component_families", {}).items():
            if isinstance(fdata, dict):
                families[fname] = self._parse_family(fname, fdata)
        return TrainingItem(
            item_id=data.get("item_id", ""),
            language=data.get("language", "en"),
            source=data.get("source", {}),
            communication_intent=data.get("communication_intent", ""),
            meaning_frame=data.get("meaning_frame", ""),
            component_families=families,
            slot_order=data.get("slot_order", []),
            allowed_combinations=data.get("allowed_combinations", []),
            blocked_combinations=data.get("blocked_combinations", []),
            normalized_components=data.get("normalized_components", []),
            sentence_breakdown=data.get("sentence_breakdown", ""),
            literal_meaning=data.get("literal_meaning", ""),
            natural_meaning=data.get("natural_meaning", ""),
            grammar_rules_used=data.get("grammar_rules_used", []),
            vocabulary=data.get("vocabulary", []),
            pronunciation=data.get("pronunciation", {}),
            register=data.get("register", "neutral"),
            dialect=data.get("dialect", "standard"),
            generated_examples=data.get("generated_examples", []),
            fixed_exceptions=data.get("fixed_exceptions", []),
            explanation=data.get("explanation", ""),
            confidence=float(data.get("confidence", 1.0)),
            review_status=data.get("review_status", "approved"),
            version=data.get("version", "1.0"),
        )

    def _parse_eval_rule(self, data: dict) -> EvaluationRule:
        return EvaluationRule(
            rule_id=data.get("rule_id", ""),
            category=data.get("category", ""),
            description=data.get("description", ""),
            test_cases=data.get("test_cases", []),
            passing_threshold=float(data.get("passing_threshold", 0.9)),
        )

    def _create_default_file(self, path: Path) -> None:
        """Creates a default English engine training file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        # The full English engine YAML is in language_engines/English_engine.training.yaml
        # This method creates a minimal stub so the loader can proceed.
        stub = {
            "version": "1.0",
            "engine_registry": {
                "engine_id": "english_engine_v1",
                "language_name": "English",
                "language_code": "en",
                "writing_systems": ["Latin"],
                "language_family": "Indo-European/Germanic",
                "supported_variants": ["en-US", "en-GB", "en-AU"],
                "canonical_training_file": str(path),
            },
            "artificial_intelligence_core": {},
            "brain": {},
            "skills": {},
            "creativity": {},
            "language_engine": {},
            "sentence_system": {
                "communication_families": {},
                "templates": {},
                "combination_rules": [],
                "fixed_expressions": [],
            },
            "training_data": [],
            "evaluation": [],
            "connections": {},
            "governance": {
                "data_provenance": "developer_supplied",
                "version_history": [],
                "approval_status": "approved",
                "privacy_policy": "no_private_data",
                "deletion_policy": "on_request",
                "conflict_resolution": "latest_approved_wins",
                "export_and_import_policy": "yaml_only",
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(stub, f, default_flow_style=False, allow_unicode=True)
        logger.info("Created default engine training file: %s", path)
