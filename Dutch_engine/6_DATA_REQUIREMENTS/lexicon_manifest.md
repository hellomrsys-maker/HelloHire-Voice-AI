# Dutch Lexical Data Requirements & Corpus Manifest

## 1. Corpus Sources & Lexicographical Standards

The Dutch Language Engine draws lexical calibration from canonical linguistic corpora:
- **Universal Dependencies (UD) Dutch-Alpino & LassySmall**:
  - Provides dependency trees, V2 fronting tags, and verb cluster annotations for European Dutch.
- **Woordenlijst Nederlandse Taal (*Groene Boekje*)**:
  - Maintained by the *Nederlandse Taalunie* (Dutch Language Union). Official standard for Dutch spelling, hyphenation, and gender classification across the Netherlands, Flanders, and Suriname.
- **OpenTaal & CELEX Lexical Database**:
  - Word frequency distributions, morphological breakdown, and syllable boundary data.

---

## 2. Lexicon Manifest & Distribution

| Lexical Category | Item Count | Storage Model | Primary Function |
| :--- | :--- | :--- | :--- |
| **Common Gender Nouns (*De*-words)** | 48,000+ | Direct hash map | Default masculine/feminine merged gender classification |
| **Neuter Gender Nouns (*Het*-words)** | 16,000+ | Fast bitset / trie | Explicit neuter determination (*het boek, het huis, het meisje*) |
| **Strong & Irregular Verbs** | 320 roots | Exact tabular map | Ablaut classes I-VII (*zingen/zong/gezongen*, *brengen/bracht/gebracht*) |
| **Separable Verbs (*Scheidbare werkwoorden*)** | 2,400+ | Prefix-stem pair trie | Detection of split verb-bracket structures (*hij belt haar op*) |
| **Diminutive Suffix Patterns** | 5 morph classes | Rule engine | Automatic allomorph generation (*-tje, -je, -pje, -etje, -kje*) |
| **Modal Particles & Clusters** | 24 patterns | Pragmatic analyzer | Politeness calibration (*maar even, toch maar eens*) |

---

## 3. Memory & Performance Constraints
- In accordance with the **Zero-Bridge Synchronous Memory Rule**, core lexical lookups and syntactic taggers interface with the 64-byte Atomic Memory State Vector (AMSV) at magic signature `0x4E454452` ("NEDR").
- All operations execute in O(1) or O(k) bounded time with zero heap reallocation on hot linguistic paths.
