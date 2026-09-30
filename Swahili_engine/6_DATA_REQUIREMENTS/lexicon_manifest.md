# Swahili Engine — Layer 6: Data Requirements & Lexicon Manifest

## 1. Core Corpora & Dependency Treebanks

The Swahili Engine integrates standard computational linguistic resources:

1. **Universal Dependencies (UD) Swahili Treebank**:
   - **UD Swahili-Helsinki**: Annotated with Universal POS (UPOS), Bantu noun class tags, morphological features, and dependency structures.
   - Provides syntactic ground truth for head-initial noun phrases and concordial dependencies.
2. **The Helsinki Corpus of Swahili (HCS)**:
   - 25 million tokens of modern Swahili texts covering newspapers (*Taifa Leo, Nipashe, Daily News*), parliamentary records (Hansards from Kenya and Tanzania), books, and broadcast transcriptions.
3. **Lexicographical Authorities**:
   - **Kamusi Kuu ya Kiswahili (BAKITA / Longhorn)**: The official dictionary of the National Swahili Council of Tanzania (*Baraza la Kiswahili la Taifa*). Over 50,000 headwords with canonical ngeli classification and verbal extension patterns.
   - **TATAKI / TUKI (Taasisi ya Taaluma za Kiswahili, University of Dar es Salaam)**: English-Swahili and Swahili-English academic lexicons.

---

## 2. Noun Class Lexical Concord Lists (Orodha ya Ngeli)

The engine stores explicit stem-to-class mappings for all 18 noun classes:
- **Class 1/2**: *mtu/watu, mtoto/watoto, mwalimu/walimu, mgeni/wageni, daktari/madaktari* (animate rule).
- **Class 3/4**: *mti/miti, mto/mito, mkono/mikono, mji/miji, mpira/mipira, mwezi/miezi*.
- **Class 5/6**: *jicho/macho, jina/majina, gari/magari, duka/maduka, embe/maembe, yai/mayai*.
- **Class 7/8**: *kitabu/vitabu, kiti/viti, chumba/vyumba, chakula/vyakula, kisu/visu*.
- **Class 9/10**: *nyumba/nyumba, safari/safari, barabara/barabara, meza/meza, simba/simba, kazi/kazi*.
- **Class 11/14**: *uhuru, ukuta/kuta, ufunguo/funguo, wimbo/nyimbo, uzuri*.
- **Class 15**: *kusoma, kuimba, kucheza, kuandika*.
- **Class 16/17/18**: *mahali, nyumbani, shuleni, mtoni*.

---

## 3. Verbal Morpheme & Extension Lexicon

### 3.1 Subject and Object Prefixes Table
Mapping of person/number and noun classes 1–18 to their respective `SP` and `OP` graphemes.

### 3.2 Verbal Extension Derivation Table
Root vowel height assimilation rules (/a, i, u/ $\to$ *-i-* vs. /e, o/ $\to$ *-e-*) across:
- Applicative (*-ia / -ea*)
- Causative (*-isha / -esha / -za*)
- Passive (*-wa*)
- Reciprocal (*-ana*)
- Stative (*-ika / -eka*)

### 3.3 Monosyllabic Verb Stems Inventory
Explicit registration of all stress-requiring monosyllabic verbs:
`-la, -nywa, -ja, -fa, -pa, -cha, -enda, -isha`.
