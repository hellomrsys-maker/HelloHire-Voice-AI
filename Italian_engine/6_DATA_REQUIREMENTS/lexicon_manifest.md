# Layer 6: Data Requirements & Lexicon Manifest — Italian Language Engine

## 1. Corpus Foundations
The Italian Engine integrates standard linguistic corpora and computational lexicons:
1. **Universal Dependencies Italian (UD Italian-ISDT & UD Italian-ParTUT)**:
   - Gold-standard annotated treebanks for POS tagging, morphological feature tagging, and dependency parsing.
2. **CoLFIS (Corpus e Lessico di Frequenza dell'Italiano Scritto)**:
   - 3-million-word balanced written corpus providing lemma and wordform frequencies.
3. **De Mauro / Gradit (Grande Dizionario Italiano dell'Uso)**:
   - Lexical frequency strata: Vocabolario Fondamentale (FO - 2,000 words), Alto Uso (AU - 2,750 words), Alta Disponibilità (AD - 2,300 words).
4. **VerbNet Italian & ItalWordNet**:
   - Semantic frame alignment and argument structure for transitive, unergative, and unaccusative verbs.

## 2. Morphological Lexicon Specifications
- **Lemmas**: Complete base dictionary of nouns, verbs, adjectives, adverbs, pronouns, prepositions, conjunctions, interjections.
- **Auxiliary Classification Table**:
  - `class="avere"`: Transitive (*leggere, scrivere, mangiare*) and unergative (*lavorare, ridere, viaggiare*).
  - `class="essere"`: Unaccusative (*andare, venire, partire, arrivare, morire, nascere, cadere, succedere*).
  - `class="both"`: Alternating verbs changing auxiliary depending on transitivity (*salire, scendere, cambiare, passare, correre*).
- **Articulated Preposition Table**: Deterministic fusions for `di, a, da, in, su` across all 7 article allomorphs.
- **Combined Clitic Table**: Complete transition matrix for double clitic chains (`glielo, me la, te ne, ce li...`).
