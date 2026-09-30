# Pipeline Architecture & Algorithms for Tamil (Algorithmic Layer)
## Sovereign Engine: `Tamil_engine` | Cognitive Pipeline

### 1. 9-Layer Cognitive Flow

```mermaid
graph TD
    A["Raw Tamil Input (Script/Text)"] --> B["Layer 1: Unicode Normalization & Tamil Tokenizer"]
    B --> C["Layer 2: Sandhi (Puṇarcci) Analyzer & Splitter"]
    C --> D["Layer 3: Morphological Agglutinative Stem Peeler"]
    D --> E["Layer 4: 8-Case & PNG Agreement Validator"]
    E --> F["Layer 5: Retroflex & Phonological Conformity Verifier"]
    F --> G["Layer 6: Diglossic Register Classifier (Centamiḻ vs Koṭuntamiḻ)"]
    G --> H["Layer 7: Editorial Multi-Factor Quality Synthesizer"]
    H --> I["Layer 8: Synchronous Memory Sync -> 64-byte AMSV (0x54414D4C)"]
    I --> J["Layer 9: Downstream Application / Hardware Inference"]
```

---

### 2. Strict 64-Byte AMSV Memory Map (`0x54414D4C` "TAML")

| Byte Range | Field Name | Width | Type | Sub-AI / Component | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x00..0x03` | `magic` | 4 B | `char[4]` | `TamilMatrixBridge` | ASCII `"TAML"` (`0x54414D4C`) |
| `0x04` | `version_major` | 1 B | `uint8` | System Header | `0x01` |
| `0x05` | `version_minor` | 1 B | `uint8` | System Header | `0x00` |
| `0x06` | `engine_mode` | 1 B | `uint8` | Orchestrator | `0x01` (Inference) |
| `0x07` | `dialect_mode` | 1 B | `uint8` | Config | `0x01` (Standard / Centamiḻ) |
| `0x08..0x11` | `reserved_head` | 10 B | `uint8[10]`| Reserved | Zero padding |
| `0x12` (18) | `syntax_capability` | 1 B | `uint8` | `TamilSyntaxSubAI` | Bitfield: S, O, V, Postposition |
| `0x13` (19) | `case_agglutination` | 1 B | `uint8` | `TamilEditorialSubAI` | `0x01` (8-case agglutination verified) |
| `0x14` (20) | `retroflex_orthography`| 1 B | `uint8` | `TamilPhonologySubAI` | Bitfield: Valid, Retroflex, ழ (*ḻ*) present |
| `0x15` (21) | `png_concord_flag` | 1 B | `uint8` | `TamilEditorialSubAI` | `0x01` (Subject-Verb PNG matches) |
| `0x16` (22) | `register_tier` | 1 B | `uint8` | `TamilPragmaticSubAI` | `1` (Centamiḻ), `2` (Koṭuntamiḻ) |
| `0x17` (23) | `sandhi_concord_flag`| 1 B | `uint8` | `TamilPragmaticSubAI` | `0x01` (Sandhi plosive doubling valid) |
| `0x18..0x1B` (24..27)| `editorial_confidence`| 4 B | `float32` | `TamilEditorialSubAI` | Float32 little-endian (`0.0` .. `1.0`) |
| `0x1C..0x33` | `reserved_payload` | 24 B | `uint8[24]`| Reserved | Zero padding |
| `0x34` (52) | `sub_ai_syntax` | 1 B | `uint8` | `TamilSyntaxSubAI` | `0x01` (Active) |
| `0x35` (53) | `sub_ai_phonology` | 1 B | `uint8` | `TamilPhonologySubAI` | `0x01` (Active) |
| `0x36` (54) | `sub_ai_pragmatic` | 1 B | `uint8` | `TamilPragmaticSubAI` | `0x01` (Active) |
| `0x37` (55) | `sub_ai_editorial` | 1 B | `uint8` | `TamilEditorialSubAI` | `0x01` (Active) |
| `0x38..0x3F` | `reserved_tail` | 8 B | `uint8[8]` | Alignment | Zero padding to 64-byte boundary |
