# Persian Lexicon & Corpora Requirements (Data Layer)

## 1. Primary Corpora & Treebanks
1. **Bijankhan Corpus**:
   - ~2.6M tokens of tagged contemporary Persian text annotated by Tehran University.
   - Gold standard for POS tag crosswalks and light-verb frequency analysis.
2. **Universal Dependencies Persian-Seraji / PerDT**:
   - Universal Dependencies treebank with dependency structures for modern written Persian.
   - Gold standard for SOV root attachment, non-projective Ezafe dependencies, and *rā* direct object tracking.
3. **Uppsala Persian Corpus (UPC)**:
   - Modified version of the Bijankhan corpus with standardized orthography, ZWNJ regularization, and lemmatized heads.

## 2. Lexical Dictionaries
1. **Dehkhoda Dictionary (لغت‌نامه دهخدا)**:
   - Encyclopedic dictionary of classical and contemporary Persian literature (~30 volumes).
   - Source of classical poetic idioms and compound stems.
2. **Moin Encyclopedic Dictionary (فرهنگ فارسی معین)**:
   - Standard structural 6-volume dictionary documenting modern Persian morphology, compound verbs, and foreign borrowings.
3. **Academy of Persian Language and Literature (فرهنگستان زبان و ادب فارسی)**:
   - Neologism and loanword standardization registry (e.g. *rāyāneh* for computer, *bālgard* for helicopter).

## 3. Computational Annotations
- Dual-stem verb table: Infinitives mapped to regular past stem and present stem.
- Ezafe boundary marker database: Noun endings categorized by consonant, silent *heh*, or long vowel.
- DOM (*rā*) distribution corpus: Definiteness markers mapped to semantic animacy.
- Perso-Arabic unicode character mapping table: Handling Arabic vs Persian Unicode variants (e.g., Arabic ک `U+0643` vs Persian ک `U+06A9`, Arabic ي `U+064A` vs Persian ی `U+06CC`).
