# Layer 6: Data Requirements & Lexicon Manifest — Indonesian Language Engine

## 1. Primary Linguistic Corpora
The Indonesian Engine is grounded upon standard national and academic lexical resources:
1. **KBBI (Kamus Besar Bahasa Indonesia - Edisi V)**:
   - The definitive authoritative dictionary of the Indonesian language published by Badan Pengembangan dan Pembinaan Bahasa (Ministry of Education and Culture).
   - Contains >110,000 headwords, root lemmas, and derivational affixation entries.
2. **Universal Dependencies Indonesian (UD Indonesian-GSD & UD Indonesian-CSUI)**:
   - Treebanks providing annotated gold-standard dependencies, POS tags, and morphological feature sets.
3. **SEAlang Library Indonesian Corpus & Leipzig Indonesian Web Corpora**:
   - Millions of sentences across contemporary journalism, government gazettes, and literature.

## 2. Morphological Lexicon Specifications
- **Root Lemma Lexicon**: Triliteral and polysyllabic roots categorized by part of speech.
- **Nasal Assimilation Matrix**: Deterministic mapping table for `p, t, s, k` deletion vs `b, d, j, g` retention under `meN-` and `peN-`.
- **Affix Combination Permissibility Table**:
  - Valid prefixes: *meN-, di-, ter-, ber-, peN-, per-, se-*.
  - Valid suffixes: *-kan, -i, -an*.
  - Valid circumfixes: *ke-...-an, peN-...-an, per-...-an, ber-...-an, ber-...-kan*.
- **Numeral Classifier Manifest**: Comprehensive noun-to-classifier semantic pairing table (*orang, ekor, buah, lembar, batang, butir, pucuk, bilah*).
