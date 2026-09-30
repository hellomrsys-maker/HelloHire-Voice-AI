# Training Ecosystem & Unified Language Architecture

This directory standardizes all training pipelines across the workspace into a clean, intuitive structure.

---

## 1. Master Single-File Training Entrypoints

Instead of running dozens of fragmented scripts, all training is organized into **Single Total Files**:

| Task | Primary Command | Alternative Shortcut | Description |
| :--- | :--- | :--- | :--- |
| **Total Grammar Training** | `py training/train_grammar.py` | `py training/train_grammar.py --language English` | Trains syntax trees, agreement, tense grids, and typology across all languages |
| **Universal Language Engine** | `py training/train_language.py --language <Lang>` | `py training/train_language.py --all` | Single universal file that trains ANY of the 45 language engines from its canonical file |
| **English Engine (Dedicated)** | `py English_engine/train.py` | `py training/train_english.py` | Completely self-contained trainer for English with gender-generic registers |
| **Hindustani Engine (Dedicated)** | `py Hindustani_engine/train.py` | `py training/train_hindustani.py` | Dedicated trainer for Hindustani SOV syntax, `Aap`/`Tum`/`Tu` deixis, and word prosody |

---

## 2. Directory Taxonomy & Organization

```
training/
├── train_grammar.py           <-- Total Grammar & Syntax Master Trainer (Single File)
├── train_language.py          <-- Universal Master Language Engine Trainer (Single File)
├── train_english.py           <-- Root shortcut to English_engine/train.py
├── train_hindustani.py        <-- Root shortcut to Hindustani_engine/train.py
│
├── core/                      <-- Shared Infrastructure & Neural Backbones
│   ├── multi_task_trainer.py
│   ├── checkpoint_sync.py
│   ├── gradient_routing.py
│   └── conversational_intent_tree.py
│
├── bubbles/                   <-- Multilingual Bubbles 1-5 (Scaffolding & Corpora)
│   ├── build_bubble[3-5]_scaffolding.py
│   ├── generate_multilingual_corpora_bubble[1-5].py
│   └── train_multilingual_bubble[1-5].py
│
└── cognitive/                 <-- High-Level Cognitive AI Modules
    ├── train_hcte_cognitive_ai.py
    ├── train_rvce_cognitive_ai.py
    └── train_all_cognitive_engines.py
```

---

## 3. Mandatory Standards

1. **One Language = One File**: Every engine has its self-contained training pipeline (`English_engine/train.py`, `Hindustani_engine/train.py`).
2. **Gender-Generic Acoustic Registries**: Pitch registers are defined solely by physical Hz ranges (`low_register`, `medium_register`, `high_register`) rather than gender labels.
3. **Generic Speaker Identity Tokens**: Standardized on `Speaker_A`, `Speaker_B`, and `Instructor`.
4. **Single Canonical Dataset**: Ingests exclusively from `<Language>_engine/6_DATA_REQUIREMENTS/canonical_engine_data.json`.
5. **Zero-Bridge 64-Byte AMSV Memory**: Direct in-memory physical mutation with 0-nanosecond latency.
