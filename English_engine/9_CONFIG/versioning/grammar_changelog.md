# English Engine Grammar Changelog

## [1.0.0] - 2026-09-18

### Added
- Complete 9-layer architectural tree implementation:
  - `1_SYNTACTIC_STRUCTURE_(Sentence_Layer)/`: Penn Treebank (36 tags), UD 17 tags, closed-class words, clause types, coordination/subordination, X-bar phrase structure, subject-verb agreement, pronoun-antecedent rules, 12 tense-aspect grid, conditional types, active/passive voice transformations.
  - `2_MORPHOLOGICAL_ANALYSIS_(Word_Layer)/`: 8 inflectional affixes, derivational affixes, compounding patterns, Latin/Greek/Anglo-Saxon roots, irregular verb paradigms, irregular plural paradigms, allomorphy rules, phonological alternations.
  - `3_PHONOLOGICAL_ORTHOGRAPHIC_(Text_Sound_Layer)/`: IPA to ARPAbet mapping, vowel formants, consonant manner/place/voicing, G2P rules, P2G homophone disambiguation, silent letters, GenAm vs RP splits, connected speech elision/assimilation.
  - `4_SEMANTIC_REPRESENTATION_(Meaning_Layer)/`: WordNet core synsets, selectional restrictions, PropBank thematic roles, lambda calculus templates, quantifier scope resolution, homonym inventory, garden-path sentence patterns.
  - `5_PRAGMATIC_(Use_Layer)/`: Deictic expressions, anaphora resolution pipeline, RST coherence relations, Gricean maxims, conceptual metaphors, non-compositional idioms.
  - `6_DATA_REQUIREMENTS/`: Corpora manifest, lexicon manifest, grammar theories matrix.
  - `7_ALGORITHMS/`: 7-stage parsing pipeline, model registry, hybrid engine routing policy.
  - `8_EVOLUTION_VARIATION/`: Dialect matrices, AAVE/Chicano/Creole features, neologism tracking, Biber register feature matrix.
  - `9_CONFIG/`: Three core questions YAML, uncertainty policy YAML, versioning changelog, and automated rollback script.
- **Dedicated Sub-AIs** (`syntax_sub_ai.py`, `phonology_sub_ai.py`, `pragmatic_sub_ai.py`, `editorial_sub_ai.py`).
- **Six-Language Matrix**: Rust (safety & data processing), C++20 (core trie engine & memory alignment), CUDA (GPU attention kernels), Java 21 (virtual threads), Julia (grammar dynamics), and Python (coordinator).
- **The Zero-Bridge Synchronous Memory Rule**: Direct 0-nanosecond physical memory writes to the 64-byte `AtomicMemoryStateVector` (AMSV).
