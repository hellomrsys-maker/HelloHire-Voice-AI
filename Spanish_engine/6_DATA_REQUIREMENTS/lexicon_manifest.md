# Layer 6: Data Requirements & Lexicon Manifest — Spanish Engine

## 1. Corpus Sources & Lexical Inventories
- **Primary Corpora**:
  - **AnCora-ES**: Universal Dependencies treebank with dependency syntactic trees and named entities.
  - **CREA / CORPES XXI**: Real Academia Española reference corpora for contemporary Spanish frequency statistics.
- **Lexical Coverage Targets**:
  - Top 10,000 frequent lemmas covering 96.5% of running texts.
  - Full inflectional lookup table for regular and irregular verbs: 14 tenses $\times$ 6 grammatical persons = 84 inflected forms per verb.
  - Closed-class function words: determiners, prepositions, clitic chains, coordinating and subordinating conjunctions.

---

## 2. Invariant Tagset Standard: Universal Dependencies (UD)
- `NOUN`: Sustantivo (*libro, ciudad*)
- `VERB`: Verbo principal (*cantar, estudiar*)
- `AUX`: Verbo auxiliar (*haber, ser, estar*)
- `PRON`: Pronombre personal / demostrativo / relativo (*él, me, que*)
- `DET`: Determinante / artículo (*el, una, este*)
- `ADJ`: Adjetivo calificativo / relacional (*grande, español*)
- `ADP`: Preposición (*de, en, por, para, a*)
- `ADV`: Adverbio (*rápidamente, no, muy*)
- `CCONJ`: Conjunción coordinante (*y, pero, o*)
- `SCONJ`: Conjunción subordinante (*que, si, porque, aunque*)
