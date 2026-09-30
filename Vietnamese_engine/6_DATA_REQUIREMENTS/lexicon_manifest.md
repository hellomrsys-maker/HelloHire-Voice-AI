# Vietnamese Lexicon & Corpora Requirements (Data Layer)

## 1. Primary Corpora & Treebanks
1. **Universal Dependencies Vietnamese-VTB (Vietnamese Treebank)**:
   - Treebank developed by the VLSP (Vietnamese Language and Speech Processing) consortium.
   - Contains gold-standard dependency annotations for isolating SVO syntax, classifier-noun dependencies, and serial verbs.
2. **Vietnamese Lexicon Consortium (VLSP Lexicon)**:
   - Exhaustive lexicon of ~75,000 compound words (*từ ghép*) and reduplications (*từ láy*).
   - Serves as the primary reference for distinguishing single multi-syllable compound words from independent morphemes.
3. **Leipzig Vietnamese Corpora**:
   - Millions of sentences extracted from online news corpora (VnExpress, Tuổi Trẻ, Dân Trí).
   - Benchmark for contemporary vocabulary, Sino-Vietnamese terminology, and modern colloquial particles.

## 2. Standard Dictionaries & Authority Manifests
1. **Từ điển Tiếng Việt (Viện Ngôn ngữ học - Hoàng Phê Chủ biên)**:
   - The definitive prescriptive dictionary of the Vietnamese language published by the Institute of Linguistics, Vietnam Academy of Social Sciences.
   - Authoritative source for headword definitions, classifier assignments, and spelling standards.
2. **Ministry of Education and Training (Bộ Giáo dục và Đào tạo - MOET) Spelling Standards**:
   - Standard 2018 guidelines for diacritic placement on diphthongs (*hòa* vs *hoà*, *thủy* vs *thuỷ*).
   - Capitalization and punctuation norms for official government decrees.

## 3. Computational Annotations
- Diacritic Unicode normalization: Converting decomposed Unicode (NFD) into precomposed Unicode (NFC) for all 134 accented vowel combinations.
- Classifier collocation database: Mapping 50+ classifiers to compatible semantic noun categories.
- Kinship address cross-reference tables: Symmetry verification for *anh-em*, *ông-cháu*, *thầy-trò*.
