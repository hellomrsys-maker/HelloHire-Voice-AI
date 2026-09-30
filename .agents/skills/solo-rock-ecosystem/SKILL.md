---
name: solo-rock-ecosystem
description: >-
  Comprehensive guide and execution workflow for the Solo Rock AI & BandhuPrime linguistic intelligence ecosystem.
  Use this skill whenever the user asks to develop, modify, debug, test, train, or architect any part of Solo Rock,
  BandhuPrime, the Six-Language Matrix (Rust, Julia, Python, C++, CUDA/Triton, Java), the 4-Stage Matrix Pattern,
  the 64-byte Atomic Memory State Vector (AMSV), grammar engines, 24 parallel core nodes, or single-file training pipelines.
---

# Solo Rock & BandhuPrime Ecosystem Skill

This skill governs all development, implementation, debugging, and verification tasks across the Solo Rock and BandhuPrime codebase.

## 1. Core Architectural Constraints

Always verify that code adheres to these strict rules:

1. **The Zero-Bridge Synchronous Memory Rule**:
   - Zero traditional bridges (Cython, Pybind11, ctypes wrappers over sockets, gRPC, REST, IPC queues).
   - Python, C++20, Rust, Java, Julia, and CUDA share the exact physical memory space of the **64-byte Atomic Memory State Vector (AMSV)**.
   - All state updates must be 0-nanosecond hardware synchronized on a single 64-byte cache line.
   - Standard AMSV Memory Layout:
     - `0x00 - 0x07` (8B): `vce_phoneme_state`
     - `0x08 - 0x0F` (8B): `vce_prosody_state` ($F_0$ Q8.8, speech rate, fluency)
     - `0x10 - 0x17` (8B): `ccte_cog_bank_alpha` (Thinking, Focus, Memory, Creative Q16)
     - `0x18 - 0x1F` (8B): `ccte_cog_bank_beta` (Imagination, Analytical, Verbal, Emotional Q16)
     - `0x20 - 0x27` (8B): `rsse_scenario_state` (Scenario ID, Turn, Register Q16, Phase)
     - `0x28 - 0x2F` (8B): `aeee_examination_state` (IRT Ability Theta, SEM Q16, Question Index)
     - `0x30 - 0x37` (8B): `maio_global_state_alpha` (Competency Index, Skill ID, Era ID, Struct Q16)
     - `0x38 - 0x3F` (8B): `maio_global_state_beta` (Intervention Directives, Cross-Module Attention)

2. **The Six-Language Matrix Distribution**:
   - **Rust**: Systems safety, zero-allocation memory invariants, C-ABI export via `cdylib`.
   - **Julia**: Analytical acoustics, dynamical simulations, nPVI/rPVI rhythm metrics, IRT estimation.
   - **Python**: High-level AI orchestration, PyTorch Transformer encoders, `UniversalSubwordTokenizer`.
   - **C++**: Microsecond-level 1000Hz global surveillance loop, FFT/Mel filterbanks, lock-free AMSV sync.
   - **CUDA & Triton**: Massively parallel phoneme burst detection, acoustic spotters, semantic alignment.
   - **Java**: JDK 21 Spring REST controllers, candidate scheduling, direct `ByteBuffer` AMSV mapping.

3. **Reusable Four-Stage 6-Language Matrix Pattern**:
   - **Stage 1 (Reserved Entry Boundary)**: Payload intake, strict schema and safety contract validation.
   - **Stage 2 (Base Matrix $\leftrightarrow$ AI Model + Training)**: Deterministic physical state ingestion in AMSV paired with neural inference/weight adaptation.
   - **Stage 3 (Connected Internal Groups)**: $2\times 2$ Network ($M_{11\dots 22}$) $\rightarrow$ Central Hub ($M_{\text{hub}}$) $\rightarrow$ $2\times 2$ Network ($M_{31\dots 42}$) with backward cyclic refinement.
   - **Stage 4 (Verify, Learn, Analyze, Result)**: Check/Correct $\rightarrow$ Base Matrix $\rightarrow$ AI Model $\rightarrow$ Analyzer $\rightarrow$ Result.

4. **Observational Listening & Legal Protocol**:
   - Strictly observational listening model: zero permanent storage of raw audio/video files.
   - Zero copyright metadata: never store movie/book/actor/producer titles.
   - All communicative interactions follow generic speaker tokens: `Speaker_A`, `Speaker_B`, `Instructor`.
   - Conversational latency calibrated nominal gap: **518 ms**.

5. **Verbatim Production Integrity**:
   - Zero placeholders (`# TODO`, `pass`), zero stubs, zero dummy data.
   - 100% test coverage across all integrated modules.

---

## 2. Common Development & Execution Workflows

### A. Running Single-Screen Node.js Training
Each engine and the root workspace support single-screen execution:
```powershell
node train.js --language English
node train.js --language Hindustani
node train.js --all
```

### B. Running Unified Python Engine Training
```powershell
python training/train_language_engine.py --language English
```

### C. Validating 64-Byte AMSV Memory Alignment
When modifying or adding AMSV state fields, ensure bit offsets and alignments are checked in:
- C++: `alignas(64) struct AtomicStateVector`
- Rust: `#[repr(C, align(64))] struct AtomicStateVector`
- Java: `ByteBuffer.allocateDirect(64)`
- Node.js: `Buffer.alloc(64)`

### D. References
- Master Specification: [AGENTS.md](file:///d:/gra.voi/AGENTS.md)
- Complete Rulebook: [RULEBOOK.md](file:///d:/gra.voi/RULEBOOK.md)
