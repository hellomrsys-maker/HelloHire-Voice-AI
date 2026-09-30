# Layer 7: Computational Algorithms & Pipeline Architecture - Bengali Engine (বাংলা)

## 1. Multi-Pass Analysis Pipeline
The Bengali engine executes an automated 7-stage computational analysis pipeline:

```
[Input Text (Bengali Script / Romanized)]
       │
       ▼
[Pass 1: Tokenization & Boundary Normalization]
  - Unicode NFC normalization, Dā̃ṛi (।) segmentation, enclitic classifier detachment (-Ta, -Ti, -gulo)
       │
       ▼
[Pass 2: Morphological Decomposition & POS Tagging]
  - Case suffix stripping (-ke, -er, -te), Ovisruti vowel harmony lookup, UD POS assignment
       │
       ▼
[Pass 3: Verbal Paradigm Inflection & Vector Verb Decomposition]
  - Stem identification, compound verb split (V1-conjunctive + V2-vector), tense-aspect-mood resolution
       │
       ▼
[Pass 4: Syntactic Parsing & Case Concord]
  - SOV dependency parsing, subject pro-drop recovery, differential object marking (-ke) validation
       │
       ▼
[Pass 5: Pragmatic & Register Verification]
  - 3-tier address concordance (Aapni/Tumi/Tui), Sadhu vs Cholito register purity (Anti-Guru-Chondali check)
       │
       ▼
[Pass 6: Dedicated Sub-AI Synthesis]
  - 4 Sub-AIs update designated 64-byte AMSV offsets synchronously with zero bridge
       │
       ▼
[Pass 7: Surface Generation / Proofreading Diagnostics]
```

---

## 2. Classifier Agreement & Detachment Algorithm
Classifiers are either attached to numerals or to nominal heads:
```python
def parse_classifier(token: str):
    classifiers = ["খানা", "খানি", "গুলো", "গুলি", "টা", "টি", "জন"]
    for c in classifiers:
        if token.endswith(c) and len(token) > len(c):
            stem = token[:-len(c)]
            return {"stem": stem, "classifier": c, "definiteness": True}
    return {"stem": token, "classifier": None, "definiteness": False}
```

---

## 3. Register Concordance & Guru-Chondali Prevention
The engine flags stylistic mixing where Sadhu suffixes (*-iteche*, *-iyache*) co-occur with modern Cholito pronouns or verbs:
```
Condition:
IF sentence contains Sadhu verb (e.g. "করিতেছেন") AND sentence contains Cholito pronoun (e.g. "তার")
THEN emit SolecismError: GURU_CHONDALI_VIOLATION
```

---

## 4. Zero-Bridge AMSV Memory Synchronization Layout
All Sub-AIs strictly write into the physical 64-byte Atomic Memory State Vector (`AMSVEmbeddedView`):

| Sub-AI Module | Physical Byte Range | Target Field / Capability | Description |
| :--- | :--- | :--- | :--- |
| **BengaliPhonologySubAI** | `0x00..0x07` (Bytes 0..7) | `PhonemeState` | Vowel harmony & retroflex articulatory state |
| **BengaliPhonologySubAI** | `0x08..0x0F` (Bytes 8..15) | `ProsodyState` | Pitch accent & syllabic duration |
| **BengaliPhonologySubAI** | `0x18` (Byte 24) | Capability 4 | Phonological & Orthographic Accuracy |
| **BengaliSyntaxSubAI** | `0x12` (Byte 18) | Capability 1 | SOV Parsing & Subject-Verb Agreement |
| **BengaliSyntaxSubAI** | `0x34` (Byte 52) | `GlobalStructuralScore` | Clause hierarchy & case integrity score |
| **BengaliEditorialSubAI** | `0x14` (Byte 20) | Capability 2 | Lexical Purity (Tatsama vs Tadbhav balance) |
| **BengaliEditorialSubAI** | `0x1A` (Byte 26) | Capability 5 | Editorial & Style Polish (Anti-Guru-Chondali) |
| **BengaliPragmaticSubAI** | `0x16` (Byte 22) | Capability 3 | 3-Tier Address Politeness (Aapni/Tumi/Tui) |
| **BengaliPragmaticSubAI** | `0x36` (Byte 54) | `GlobalRegisterScore` | Pragmatic Register Consistency |
