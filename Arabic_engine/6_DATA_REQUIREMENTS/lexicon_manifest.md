# Arabic Engine — Layer 6: Data Requirements & Lexicon Manifest

## 1. Core Corpora & Universal Treebanks

1. **Universal Dependencies Arabic (UD_Arabic-PADT & UD_Arabic-NYUAD)**:
   - Prague Arabic Dependency Treebank (PADT) providing morphological tags, dependency trees, and syntactic structures for Modern Standard Arabic news texts.
2. **The Classical Arabic Corpus (CAC)**:
   - Standard baseline for ancient prose, classical poetry, and foundational grammatical treatises.
3. **Arabic Gigaword Corpus (LDC)**:
   - Comprehensive multi-decade journalistic corpus spanning Pan-Arab news outlets (Al-Ahram, Al-Hayat, Asharq Al-Awsat, Xinhua Arabic).

---

## 2. Morphological Lexica & Dictionaries

1. **Hans Wehr Dictionary of Modern Written Arabic** (ed. J. Milton Cowan):
   - Standard reference organizing vocabulary strictly by triconsonantal and quadriconsonantal root matrices.
2. **Al-Mu'jam al-Wasīṭ (المُعْجَمُ الوَسِيطُ)**:
   - Official authoritative lexicon published by the Academy of the Arabic Language in Cairo (مجمع اللغة العربية بالقاهرة).
3. **Buckwalter Morphological Analyzer (BAMA / SAMA)**:
   - Standard computational lexicon defining compatibility tables between Arabic prefixes, stems, and suffixes.
4. **Lisān al-'Arab (لِسَانُ العَرَبِ)**:
   - The magnum opus classical lexicon authored by Ibn Manẓūr (13th century CE), providing etymological depth.

---

## 3. Computational Rule Matrices Manifest

The engine embeds four high-fidelity declarative JSON matrices:
1. `root_pattern_matrix.json`: Contains 50+ core Semitic roots mapped to their valid Forms I–X derived paradigms and participles.
2. `broken_plural_matrix.json`: Catalogs singular-to-broken-plural template conversions across 10 major plural patterns.
3. `case_idafa_matrix.json`: Encodes I'rab terminal case vowel rules, Mudāf/Mudāf Ilayh constraints, and diptote behaviors.
4. `pragmatic_register_matrix.json`: Codifies Islamic ceremonial greeting adjacency pairs, diplomatic titles, and epistolary formulas.
