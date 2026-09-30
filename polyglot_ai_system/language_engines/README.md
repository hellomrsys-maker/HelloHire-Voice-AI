# language_engines/ — One Engine, One Canonical File

This directory contains the **single canonical training file for each language engine**
in the Polyglot AI System, following the **Single-File Language Engine AI Specification**.

---

## The Core Rule

> **ONE ENGINE = ONE CANONICAL TRAINING FILE.**
>
> Every skill, rule, example, sentence pattern, creative behavior, linguistic
> explanation, training record, evaluation rule, and connection belonging to one
> language must be stored under that language engine's single root file.

No grammar rules go in a separate file.
No vocabulary goes in a separate file.
No training examples go in a separate file.
No creativity rules go in a separate file.

If it belongs to a language, it lives in that language's canonical file.

---

## Files in this Directory

| File | Language | Code | Status |
|------|----------|------|--------|
| [`English_engine.training.yaml`](English_engine.training.yaml) | English | `en` | ✅ Active |
| [`French_engine.training.yaml`](French_engine.training.yaml) | French | `fr` | 🔧 Scaffold |
| [`German_engine.training.yaml`](German_engine.training.yaml) | German | `de` | 🔧 Scaffold |
| [`Spanish_engine.training.yaml`](Spanish_engine.training.yaml) | Spanish | `es` | 🔧 Scaffold |
| [`Arabic_engine.training.yaml`](Arabic_engine.training.yaml) | Arabic | `ar` | 🔧 Scaffold |
| [`Japanese_engine.training.yaml`](Japanese_engine.training.yaml) | Japanese | `ja` | 🔧 Scaffold |
| [`Tamil_engine.training.yaml`](Tamil_engine.training.yaml) | Tamil | `ta` | 🔧 Scaffold |

**✅ Active** = All 19 sections fully populated, approved, and ready for use.  
**🔧 Scaffold** = All 19 sections defined, language-specific structure in place, content to be completed by developer.

---

## Required File Structure

Each engine file must contain exactly these **19 sections in order**:

```
engine_identity
artificial_intelligence_core
brain
skills
creativity
language_rules
sentence_processing
sentence_generation
sentence_breakdown
vocabulary
pronunciation
meaning
pragmatics
training_data
examples
evaluation
memory_policy
connections
version_control
```

---

## Sentence Storage Rule

Every sentence given to the engine must be broken down into **component families**
and **slot-order templates** — not stored as a raw complete sentence.

**Wrong** (never do this):
```yaml
training_data:
  - "Hi, I am Ash."
  - "Hey, I'm Ash."
  - "Hello, my name is Ash."
```

**Correct** (store reusable components once):
```yaml
sentence_processing:
  component_families:
    greeting_family:
      entries: [hi, hey, hello, hey_there]
    identity_connector_family:
      entries: [i_am, contracted_i_am, my_name_is]
    name_family:
      entries: [Ash, Alex, Sam, "{approved_person_name}"]
  slot_templates:
    identity_greeting_template:
      slot_order: [greeting_family, identity_connector_family, name_family]
```

The engine then generates "Hi, I am Ash." / "Hey, I'm Ash." / "Hello, my name is Ash."
at **runtime** from the same stored structure. The full sentence is a runtime output,
not a memorized training record.

---

## What Must NOT Be Stored as Training Data

| ❌ Prohibited | Reason |
|---------------|--------|
| Raw conversation transcripts | Must be extracted, reviewed, normalized, and approved first |
| Temporary agent thoughts | Runtime artifacts — discard at session end |
| Private user information | Requires explicit user approval; remove PII first |
| Repeated duplicate examples | Deduplicate into component families |
| Unverified claims | Must pass accuracy check before insertion |
| Tool status messages | Not language data |
| Accidental assistant mistakes | Not language data |
| Incomplete fragments without labels | Must be fully labeled before insertion |
| Generated text that has not passed review | Runtime output only until approved |

---

## How to Add a New Training Item

1. **Identify the communicative intent** (e.g., `greet_and_identify`)
2. **Check if the intent already has a slot template** — if yes, add to existing families
3. **If new**: create a new component family and slot template in `sentence_processing`
4. **Add a full `training_data` item** following the spec tree:
   - `item_id`, `language`, `source`, `communication_intent`, `meaning_frame`
   - `component_families`, `slot_order`, `allowed_combinations`, `blocked_combinations`
   - `normalized_components`, `sentence_breakdown_ref`, `literal_meaning`, `natural_meaning`
   - `grammar_rules_used`, `vocabulary`, `pronunciation`, `register`, `generated_examples`
   - `explanation`, `confidence`, `review_status: approved`, `version`
5. **Add a regression test** in `examples` pointing back to the item
6. **Add a `version_control` entry** recording the change
7. **Do NOT create a new file**

---

## How Cross-Language Translation Works

Each engine owns its own language data. Translation bridges connect engines
**without merging their internal knowledge**.

```
English_engine.training.yaml
  └── connections.engine_to_engine_translation_bridges
      └── english_to_french
          ├── source_engine: english_engine_v1
          ├── target_engine: french_engine_v1
          ├── target_file: French_engine.training.yaml
          └── data_isolation: strict
```

The English engine's grammar, vocabulary, and training data **never appear** in
the French engine file, and vice versa. The bridge is a labeled pointer only.

---

## Adding a New Language

1. Copy the scaffold structure from `Japanese_engine.training.yaml`
2. Rename to `{Language}_engine.training.yaml`
3. Fill in `engine_identity` for the new language
4. Populate `language_rules` with the language's actual grammar, script, and morphology
5. Populate `sentence_processing.component_families` with initial greeting/farewell families
6. Add at least one complete `training_data` item
7. Set `version_control.current_version: "1.0"` and `approval_status: approved` when ready
8. Add a connection bridge from English (and other active engines) to the new engine
9. Update this README table

---

## Governance Summary

| Rule | Enforcement |
|------|-------------|
| One file per language | `governance.export_and_import_policy.one_file_per_engine: true` |
| No raw dialogue | `evaluation.eval.{lang}.no_raw_dialogue.001` rule |
| No splitting | `governance.export_and_import_policy.no_splitting_allowed: true` |
| Approved items only | `training_data` items require `review_status: approved` |
| Runtime artifacts are temporary | `memory_policy.runtime_artifacts.auto_promotion_to_training: false` |
| Cross-language isolation | `connections.data_isolation: strict` on all bridges |
| Version history preserved | Every change recorded in `version_control.history` |
