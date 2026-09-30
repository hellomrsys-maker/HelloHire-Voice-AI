# Cantonese Lexicon & Corpora Requirements (Data Layer)

## 1. Primary Corpora & Treebanks
1. **Universal Dependencies Cantonese-HK (HKUD)**:
   - Gold-standard Universal Dependencies treebank developed for Hong Kong Cantonese.
   - Standard benchmark for Double Object Construction (DOC) dependencies and Sentence-Final Particle attachments.
2. **CantoMap / The Hong Kong Cantonese Corpus (HKCAC)**:
   - Phonetically transcribed conversational Cantonese corpus recorded by City University of Hong Kong.
   - Authoritative source for SFP cluster frequencies and spoken aspect marker distributions.
3. **pycantonese & words.hk (粵典)**:
   - Open Cantonese-English comprehensive lexical dictionary covering over 50,000 contemporary colloquial words.
   - Gold standard for Jyutping pronunciation and part-of-speech mappings.

## 2. Orthographic Standards
1. **Hong Kong Supplementary Character Set (HKSCS - 香港增補字符集)**:
   - Standard character encoding extension covering indigenous Cantonese morphemes (*哋, 唔, 喺, 咗, 嘅, 乜, 嘢, 點, 邊, 睇, 諗, 講, 食, 飲*).
2. **Linguistic Society of Hong Kong (LSHK) Jyutping**:
   - The authoritative romanization scheme mapping onsets, nuclei, codas, and tone numerals (1..6).

## 3. Computational Annotations
- Double Object Construction validation tables: Marking verbs that undergo `V + DO + IO` order (*畀, 教, 送, 還*).
- SFP combinatorial matrix: Verifying valid SFP clusters (*喇喎, 呀嘛, 㗎喇, 啫嘛*).
- Diglossic dictionary: Mapping written formal Chinese (書面語) to spoken colloquial Cantonese (口語) pairs.
