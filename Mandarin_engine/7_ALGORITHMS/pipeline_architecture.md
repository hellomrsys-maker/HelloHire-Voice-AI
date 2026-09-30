# Mandarin Engine — Layer 7: Algorithms & Parsing Pipeline
## Chinese Computational Linguistics Pipeline Architecture

### 7-Stage Execution Flow
```text
1. RAW UNSPACED CHINESE TEXT
          │
          ▼
2. CHAR-LEVEL SCRIPT DETECTION & NORMALIZATION (Simplified vs Traditional, Fullwidth to Halfwidth)
          │
          ▼
3. WORD SEGMENTATION (Maximum Forward/Backward Matching + Bidirectional Neural Transformer)
          │
          ▼
4. PART-OF-SPEECH TAGGING (Penn Chinese Treebank 33-tag inventory: NN, VV, AD, CD, M, etc.)
          │
          ▼
5. SYNTACTIC & DEPENDENCY PARSING (Topic-Comment detection, 把 disposal, 被 passive frames)
          │
          ▼
6. PHONOLOGY & PINYIN G2P CONVERSION (Tone assignment, 3rd tone sandhi, 一/不 sandhi propagation)
          │
          ▼
7. PRAGMATIC & COGNITIVE MAPPING (Mianzi politeness scoring, register level, 64-byte AMSV lock-free sync)
```
