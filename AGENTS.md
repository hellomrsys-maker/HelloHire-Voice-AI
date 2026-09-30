# Solo Rock AI & BandhuPrime System Rulebook
## Supreme Engineering & Architectural Specifications

This document serves as the permanent, non-negotiable rulebook for all autonomous agents, developers, and compilers operating on the **Solo Rock** and **BandhuPrime** linguistic intelligence ecosystem. Every subsystem, module, and engine must comply with the rules outlined herein.

---

## 1. The Zero-Bridge Synchronous Memory Rule

Under no circumstances should a traditional communication bridge (such as Cython, Pybind11, ctypes wrappers over sockets, gRPC, REST over HTTP, or message queues) be built to connect the real-time C/C++ hardware layer to the Python AI layer or Java enterprise layer for intra-process state synchronization.

1. **Embedded Physical Memory Sharing**:
   - The Python runtime, C++ engine, Rust core, Java runtime, and GPU kernels must share the exact physical memory space of the **64-byte Atomic Memory State Vector (AMSV)** (`AtomicStateVector`).
   - Bit allocations and byte alignments (`alignas(64)`) must match identically across all six languages.
   - Zero serialization and zero deserialization: state updates achieve 0-nanosecond hardware synchronization on a single CPU cache line.

2. **AMSV 64-Byte Memory Layout Standard**:
   ```text
   Offset 0x00 - 0x07 (8B): vce_phoneme_state     (Phoneme ID, Articulation Q16, Acoustic Energy)
   Offset 0x08 - 0x0F (8B): vce_prosody_state     (F0 Q8.8, Speech Rate Q16, Fluency Q16)
   Offset 0x10 - 0x17 (8B): ccte_cog_bank_alpha   (Thinking, Focus, Memory, Creative Q16)
   Offset 0x18 - 0x1F (8B): ccte_cog_bank_beta    (Imagination, Analytical, Verbal, Emotional Q16)
   Offset 0x20 - 0x27 (8B): rsse_scenario_state   (Scenario ID, Turn, Register Q16, Phase)
   Offset 0x28 - 0x2F (8B): aeee_examination_state(IRT Ability Theta, SEM Q16, Question Index)
   Offset 0x30 - 0x37 (8B): maio_global_state_alpha(Competency Index, Skill ID, Era ID, Struct Q16)
   Offset 0x38 - 0x3F (8B): maio_global_state_beta(Intervention Directives, Cross-Module Attention)
   ```

---

## 2. The Strict Six-Language Matrix Standard

Every domain module within the Solo Rock ecosystem must be represented and coordinated across the **Six-Language Matrix**:

1. **Rust (Systems Safety & Data Processing)**:
   - High-throughput, zero-allocation domain invariant enforcement.
   - Pure C-ABI export via `cdylib` dynamic libraries (`extern "C"`).
   - Zero memory allocations on real-time critical paths.

2. **Julia (Mathematical Formulations & Dynamical Simulations)**:
   - Analytical acoustics, Item Response Theory (IRT) parameter estimation.
   - Normalized Pairwise Variability Index (nPVI/rPVI) speech rhythm metrics.
   - Conversational entropy, turn-taking Markov matrices, and cognitive trajectory modeling.

3. **Python (High-Level AI Orchestration & PyTorch Deep Learning)**:
   - Deep bidirectional Transformer encoders with native UTF-8 `UniversalSubwordTokenizer`.
   - Multi-agent meta-orchestrator (`BandhuPrimeOrchestrator`) coordinating skill routing.
   - Multi-task training pipelines optimizing Kendall & Gal uncertainty loss with PCGrad.

4. **C++ (C++20 Real-Time Engine Core)**:
   - Microsecond-level 1000Hz global surveillance monitoring loop.
   - Fast Fourier Transform (FFT) and Mel-frequency filterbank feature extraction.
   - Lock-free synchronization directly with the 64-byte AMSV.

5. **CUDA & Triton (GPU Massively Parallel Kernels)**:
   - Parallel phoneme burst audibility, acoustic keyword spotting, and vocal jitter/shimmer analysis.
   - Triton block-level kernels for high-throughput semantic alignment and distance matrices.

6. **Java (JDK 21 Enterprise Service Layer)**:
   - Enterprise session lifecycle management, candidate scheduling, and Spring/REST controllers.
   - Direct `ByteBuffer` memory-mapping to the 64-byte AMSV physical vector.
   - Type-safe DTO request/response contracts for cloud integrations.

---

## 3. The Reusable Four-Stage 6-Language Matrix Pattern

Every engine, module, subsystem, and pipeline across Solo Rock and BandhuPrime must strictly implement and conform to the **Reusable Four-Stage 6-Language Matrix Pattern**.

This pattern establishes a domain-neutral, recursive architecture where **every single operational unit ($M$) is a complete 6-Language Matrix execution box** housing all six technical lanes:
- **Rust**: Ingest / safe data / zero-allocation memory invariants
- **Python**: Build / orchestrate / deep learning & sequence tokenization
- **C++**: Core / fast math / 1000Hz surveillance / atomic zero-bridge sync
- **CUDA/Triton**: Parallel GPU compute / acoustic & semantic kernels
- **Java**: Services / coordination / Spring REST / ByteBuffer mapping
- **Julia**: Scientific mathematics / dynamical models / acoustic entropy

```
STAGE 1 — RESERVED ENTRY BOUNDARY (Requirement / Input)
          Define input, context, quality rules, success criteria, and requirement contract
                                       │
                                       ▼
STAGE 2 — BASE MATRIX  ◄──────────────────────────────►  AI MODEL + TRAINING
          [6-Language Matrix M_base]   shared state + feedback   [6-Language Matrix M_ai]
          (Base / tool side)                                     (AI / model + training side)
                                       │
                                       ▼
STAGE 3 — CONNECTED INTERNAL GROUPS (2x2 Network ──► Central Hub ──► 2x2 Network)
          ┌─────────────────────┐       ┌──────────────┐       ┌─────────────────────┐
          │  3.1: 2x2 Network   │ ────► │ 3.2: Central │ ────► │  3.3: 2x2 Network   │
          │  [M11] ───► [M12]   │       │     Hub      │       │  [M31] ───► [M32]   │
          │   ▲          │      │       │     [M]      │       │   ▲          │      │
          │   │          ▼      │       │              │       │   │          ▼      │
          │  [M21] ◄─── [M22]   │       │              │       │  [M41] ◄─── [M42]   │
          └─────────────────────┘       └──────────────┘       └─────────────────────┘
                     ▲                                                    │
                     └─────────────── cyclic refinement / feedback loop ──┘
                                       │
                                       ▼
STAGE 4 — VERIFY, LEARN, ANALYZE, RESULT
          ┌────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
          │  4.1: Check /  │ ──► │  4.2: Base   │ ──► │ 4.3: AI Model│ ──► │4.4: Analyzer │ ──► OUT (Result)
          │    Correct     │     │    Matrix    │     │  + Training  │     │              │        │
          └────────────────┘     └──────────────┘     └──────────────┘     └──────────────┘        │
                  ▲                                                                                │
                  └─────────────────────────────── recursive feedback ─────────────────────────────┘
```

### Rule 3.2: Grammar Engines × 6 Languages Matrix & Parallel Cores (24 Core Nodes)
All parallel multi-engine topologies must implement the dedicated **Engines × 6 Languages Matrix**:
1. **Engine A: Written Grammar & Discourse Engine (WGCE)**
2. **Engine B: Spoken & Verbal Communication Engine (RSSE / RVCE)**
3. **Engine C: Auditory & Phonological Voice Engine (VCE / Listening)**
4. **Engine D: Cognitive Capabilities & Adaptive Examination Engine (CCTE / AEEE)**
5. **Drive Core & Master Synthesis**:
   - `drive_core/linguistic_drive_core.py`: Motive force, intent steering, attention routing (AMSV Offset `0x38–0x3F`).
   - `master_synthesis/master_grammar_synthesis.py`: Global Competency Index (GCI) fusion across all 24 sub-cores.
   - `grammar_cores_orchestrator.py`: Full orchestrator executing the 24 sub-cores and Four-Stage Matrix.

---

## 4. The Eight Cognitive Capabilities Framework (CCTE)

All cognitive assessment, reasoning, and communicative evaluations must model the eight universal cognitive dimensions:
1. **Thinking Ability**
2. **Concentration & Focus**
3. **Recall & Working Memory**
4. **Creative Thinking**
5. **Imagination & Mental Simulation**
6. **Analytical & Critical Thinking**
7. **Verbal Reasoning**
8. **Emotional Regulation**

---

## 5. Recruitment Scenario & Verbal Communication Standard (RSSE & RVCE)

Recruitment communication intelligence must explicitly evaluate candidates across eight standardized interview formats:
1. Technical Interview
2. Behavioral Interview (STAR Method)
3. Competency-Based Interview
4. Case Study / Business Case
5. Group Discussion
6. HR Screening
7. Executive Leadership
8. Multi-Examiner Panel

---

## 6. Verbatim Production Integrity Standard

1. **Zero Placeholders**: No `# TODO`, no `pass`, no stub functions, no dummy returns, and no mock data in production code.
2. **Authentic Supervised Training**: Neural models must be trained on authentic multilingual text and acoustic data. Every training run must log epoch-by-epoch loss convergence and calculate SHA-256 weight fingerprints.
3. **100% Test Coverage**: All components must provide automated test suites validating functionality across the Six-Language Matrix.

---

## 7. Observational Listening, Communicative Pathway & Legal Barrier Protocol

1. **Strictly Observational Human Listening Model**: Process dialogues ephemerally, learning abstract conversational mechanics, pitch contours, and turn-taking timing.
2. **Absolute Prohibition of Media Artifacts & Copyright Footprints**:
   - Zero storage of raw media files.
   - Zero copyright metadata (no movie titles, actor names, studio credits, URLs).
3. **Sentence-Level Communicative Dyad Standard**:
   $$\text{Context 1 (Utterance)} \longrightarrow \text{Calibrated Latency Gap} \longrightarrow \text{Context Reply (Response)}$$
   - Speaker labels must exclusively use generic roles (`Speaker_A`, `Speaker_B`, `Instructor`, etc.).
4. **Calibrated Conversational Latency Standard**:
   - Calibrated Common Gap: `518 ms` (Nominal conversational latency window: `300 ms` to `650 ms`).
   - Fundamental Pitch ($F_0$) Baseline: `230.0 Hz` ($180 - 320\text{ Hz}$).
   - Speech Tempo: $3.6\text{ syllables/second}$.
5. **Single Canonical Dataset Architecture Standard**:
   - Stored in `<Language>_engine/6_DATA_REQUIREMENTS/canonical_engine_data.json`.

---

## 8. Hierarchical Dialogue Intent Tree & Slot-Equivalence Framework

- Intent nodes decouple syntactic backbone from interchangeable lexical slot bags, achieving $O(1)$ response traversal.
- Direct hardware mapping to the 64-byte AMSV intent register byte (`amsv_intent_byte`).

---

## 9. Vocal Cord Bio-Acoustic Tuning & Situational Frequency Modulation Protocol

Synthetic voice generation must physically model laryngeal biophysics:
- Cricothyroid (CT) Muscle Tension ($F_0$), Thyroarytenoid (TA) Muscle Activity, Subglottal Pressure ($P_s$), Open Quotient ($O_q$).
- 6 Communicative Scenarios: Calm Reassurance, Confidence & Authority, Aggressive Violence / Threat, Emotional Vulnerability / Tremor, Deep Melancholy / Resignation, Whisper / Secrecy.

---

## 10. Single Total Training File Architecture Protocol

- **Python**: Unified single-file training per engine (e.g., `training/train_language_engine.py`, `<Language>_engine/train.py`).
- **Node.js**: Native single-screen runner `train.js` and `<Language>_engine/train.js` with `Buffer.alloc(64)` matching the exact AMSV physical memory layout.
- Mandatory 5-Phase pipeline: Sequential Syntax, Sub-AI adaptation, Dialogue Intent Tree (518ms), Vocal Cord Bio-Acoustics, and Zero-Bridge AMSV 64-byte synchronization.
