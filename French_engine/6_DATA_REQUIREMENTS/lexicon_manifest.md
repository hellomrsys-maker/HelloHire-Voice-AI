# French Lexical Requirements & Corpus Manifests (Data Layer)

## 1. Core Lexicon Architecture
The French engine requires access to structured inflectional databases covering:
1. **Verbal Lemmas**:
   - 1st Group: 4,000+ regular -er verbs.
   - 2nd Group: 300+ regular -ir/-issant verbs.
   - 3rd Group: ~350 irregular stems across 12 tense-mood paradigms.
   - Auxiliary mapping: 16 *être* intransitives + reflexive recognition flag.
2. **Grammatical Function Words**:
   - Closed-class determiners (*le, la, les, l', un, une, des, du, de la, mon, ton, son, notre, votre, leur*).
   - Prepositions (*à, de, dans, en, par, pour, sur, avec, sans, sous*).
   - Clitics (*me, te, se, nous, vous, le, la, les, l', lui, leur, y, en*).
   - Relative pronouns (*qui, que, qu', dont, où, lequel, laquelle, lesquels, lesquelles*).
3. **Phonological Lexicon**:
   - Explicit flag for *h aspiré* words (avoiding illicit elision / liaison).
   - Consonantal liaison latent codas (/z/, /t/, /n/, /p/, /ʁ/).

## 2. Benchmark Evaluation Datasets
- **Universal Dependencies French-GSD**: 16,341 sentences annotated with UD POS and dependency trees.
- **Lefff (Lexique des Formes Fléchies du Français)**: Morphological database of inflected forms.
- **Liaison & Elision Test Suite**: Targeted phonological boundary evaluation set.
