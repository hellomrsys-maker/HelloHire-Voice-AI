# Korean Engine — Layer 7: Algorithms & Pipeline Architecture

## 1. End-to-End Processing Architecture

The Korean Engine executes an end-to-end cognitive pipeline across 9 distinct processing stages:

```
[Raw Korean Text]
       │
       ▼
1. Unicode Normalization (NFC Canonical Decomposition/Composition)
       │
       ▼
2. Jaso Decomposition (Initial 19, Medial 21, Final 28 unicode arithmetic)
       │
       ▼
3. Word (Eojeol) & Morpheme Segmentation (Stem + Particle / Ending isolation)
       │
       ▼
4. Particle Agreement & Batchim Verification (은/는, 이/가, 을/를, 과/와, 으로/로)
       │
       ▼
5. Irregular Verb Stem Resolver (ㄷ, ㅂ, ㅅ, 르, 으, ㅎ, 여 alternations)
       │
       ▼
6. Honorific Concord Engine (Subject 께서 / -(으)시-, Object 께 / 드리다)
       │
       ▼
7. Speech Level Classifier (Hasipsio-che, Haeyo-che, Haera-che, Hae-che)
       │
       ▼
8. Pragmatic Stance & Discourse Auditor (Kinship, professional titles, -님)
       │
       ▼
9. Zero-Bridge AMSV Synchronization (64-Byte Physical State Vector Update)
```

---

## 2. Core Algorithmic Engines

### 2.1 Unicode Jaso Decomposition & Composition Algorithm
The engine manipulates Korean syllables at both the syllabic block and individual phoneme (Jaso) levels via closed-form arithmetic:
$$\text{SIndex} = \text{ord}(C) - \text{0xAC00}$$
$$\text{Initial} = \lfloor \text{SIndex} / (21 \times 28) \rfloor$$
$$\text{Medial} = \lfloor (\text{SIndex} \pmod{21 \times 28}) / 28 \rfloor$$
$$\text{Final} = \text{SIndex} \pmod{28}$$

If $\text{Final} == 0$, the syllable ends in an open vowel (no batchim); if $\text{Final} > 0$, the syllable ends in a coda consonant (batchim present).

### 2.2 Particle Concord & Allomorph Selector
Evaluates the final syllable of a preceding nominal stem:
1. Extract `Final` index from syllable code.
2. If `Final > 0`: select consonant allomorph (`-은, -이, -을, -과, -이랑`). Special case: for directional `-으로/로`, if $\text{Final} == 8$ (ㄹ), select `-로`.
3. If `Final == 0`: select vowel allomorph (`-는, -가, -를, -와, -랑, -로`).

### 2.3 Honorific Concord Validator
Cross-checks three sentential components:
1. **Subject Marking**: Normal *이/가* vs. Honorific *께서*.
2. **Lexical Nominals**: Normal *밥, 집, 나이* vs. Honorific *진지, 댁, 연세*.
3. **Predicate Inflection**: Presence of pre-final suffix *-(으)시-* or suppletive verbs (*드시다, 주무시다, 계시다*).
If an honored subject is paired with a non-honorific verb (or vice versa), the engine flags an honorific concord violation.

---

## 3. The 64-Byte Atomic Memory State Vector (AMSV) Mapping

Under **The Zero-Bridge Synchronous Memory Rule**, the Python runtime shares physical memory addresses directly with the C engine space. The 64-byte vector layout for the Korean Engine is defined as follows:

| Byte Offset | Field Name | Data Type | Description |
|-------------|------------|-----------|-------------|
| 0..3        | `magic_header` | `uint32` | `0x4B4F5245` ("KORE" in ASCII) |
| 4..7        | `version` | `uint32` | Engine version (`0x00010000`) |
| 8..11       | `token_count` | `uint32` | Processed token count |
| 12..15      | `sentence_count` | `uint32` | Processed sentence count |
| 16..17      | `clause_type` | `uint16` | Bitmask: 0x01=Declarative, 0x02=Interrogative, 0x04=Imperative, 0x08=Propositive |
| 18          | `syntax_flags` | `uint8` | Bit 0: Head-final verb, Bit 1: Has Topic, Bit 2: Has Subject, Bit 3: Has Object |
| 19          | `particle_error_flags` | `uint8` | Bit 0: 은/는 error, Bit 1: 이/가 error, Bit 2: 을/를 error, Bit 3: 과/와 error |
| 20          | `phonology_flags` | `uint8` | Bit 0: Batchim present, Bit 1: Neutralization/Nasalization applied |
| 21          | `irregular_verb_flags` | `uint8` | Bit 0: Irregular stem active, Bit 1: Conjugation violation |
| 22          | `speech_level_code` | `uint8` | 1=Hasipsio, 2=Haeyo, 3=Hage, 4=Hao, 5=Haera, 6=Hae, 7=Mixed clash |
| 23          | `honorific_concord_flags`| `uint8` | Bit 0: -(으)시- active, Bit 1: 께서 active, Bit 2: Lexical hon active, Bit 3: Concord clash |
| 24..27      | `sub_ai_confidence` | `float32` | Editorial / Grammar confidence score (0.0 .. 1.0) |
| 28..31      | `syntax_latency_ns` | `uint32` | Syntax parsing time in nanoseconds |
| 32..35      | `morph_latency_ns` | `uint32` | Morphological analysis time in nanoseconds |
| 36..47      | `reserved_linguistic`| `uint8[12]`| Reserved for dialectal & pragmatic indicators |
| 48..51      | `crc32_checksum` | `uint32` | Hardware checksum over bytes 0..47 |
| 52          | `syntax_sub_ai_id` | `uint8` | Syntax Sub-AI active status (1=OK) |
| 53          | `phonology_sub_ai_id`| `uint8` | Phonology Sub-AI active status (1=OK) |
| 54          | `pragmatic_sub_ai_id`| `uint8` | Pragmatic Sub-AI active status (1=OK) |
| 55          | `editorial_sub_ai_id`| `uint8` | Editorial Sub-AI active status (1=OK) |
| 56..63      | `timestamp_epoch_ns` | `uint64` | 64-bit nanosecond epoch timestamp |
