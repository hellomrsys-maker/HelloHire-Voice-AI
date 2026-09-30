# Layer 6: Data Requirements & Lexicon Manifest (Turkish Language Engine)

## 1. Corpus Foundations & Treebank Specifications

The Turkish Computational Cognitive Engine is grounded in modern standardized Turkic linguistic resources:

### 1.1 Core Treebank Sources
1. **Universal Dependencies (UD) Turkish-IMST & Turkish-BOUN**:
   - Primary gold standard for dependency syntactic annotations, agglutinative lemma splitting, and morphological feature representation (`Case=Nom|Acc|Dat|Loc|Abl|Gen`, `Evident=Nfh`, `Polarity=Neg`).
2. **TDK Güncel Türkçe Sözlük (Turkish Language Association Dictionary)**:
   - Modern standard orthographic rules, loanword assimilation guidelines, and official hyphenation standards.
3. **METU Turkish Corpus (ODTÜ Türkçe Derlemi)**:
   - 2-million-word balanced corpus across journalism, literature, academic prose, and technical registers.

---

## 2. Core Lexicon Inventories & Exception Dictionaries

### 2.1 Consonant Lenition / Mutation Lexicon (Ünsüz Yumuşaması)
While polysyllabic native roots systematically lenite before vowel-initial suffixes, computational engines must strictly account for exceptions:
- **Regular Leniting Roots**:
  - *kitap* $\to$ *kitab-* (*-ı, -a*)
  - *ağaç* $\to$ *ağac-* (*-ı, -a*)
  - *kanat* $\to$ *kanad-* (*-ı, -a*)
  - *çocuk* $\to$ *çocuğ-* (*-u, -a*)
- **Monosyllabic Non-Leniting Exceptions (Tek Heceli İstisnalar)**:
  - *top* $\to$ *topu* (not \**tobu*)
  - *ip* $\to$ *ipi* (not \**ibi*)
  - *saç* $\to$ *saçı* (not \**sacı*)
  - *süt* $\to$ *sütü* (not \**südü*)
  - *kat* $\to$ *katı* (not \**kadı*)
- **Loanword Non-Leniting Exceptions (Yabancı Kökenli İstisnalar)**:
  - *hukuk* $\to$ *hukuku* (not \**hukuğu*)
  - *devlet* $\to$ *devleti* (not \**devledi*)
  - *millet* $\to$ *milleti* (not \**milledi*)
  - *cumhuriyet* $\to$ *cumhuriyeti* (not \**cumhuriyedi*)

### 2.2 Postposition Valency Dictionary (Edat Valans Tablosu)

| Postposition (Edat) | Obligatory Case Requirement | Meaning | Example Phrase |
| :--- | :--- | :--- | :--- |
| **için** | Nominative (Pronouns: Genitive) | for, on behalf of | *sağlık için*, *benim için* |
| **ile / -le / -la** | Nominative / Genitive | with, by means of | *arkadaşım ile*, *uçakla* |
| **gibi** | Nominative / Genitive | like, as | *kartal gibi*, *senin gibi* |
| **kadar** | Dative (*-e / -a*) | until, up to, as much as | *sabaha kadar*, *dağa kadar* |
| **doğru** | Dative (*-e / -a*) | towards | *şehre doğru* |
| **göre** | Dative (*-e / -a*) | according to | *bize göre*, *kanuna göre* |
| **rağmen / karşın** | Dative (*-e / -a*) | despite, in spite of | *zorluklara rağmen* |
| **sonra** | Ablative (*-den / -dan*) | after | *öğleden sonra* |
| **önce** | Ablative (*-den / -dan*) | before | *yemekten önce* |
| **beri** | Ablative (*-den / -dan*) | since | *dünden beri* |
| **ötürü / dolayı** | Ablative (*-den / -dan*) | owing to, because of | *hatadan dolayı* |

---

## 3. Computational Storage & JSON Schema

The Turkish engine organizes rule databases under `Turkish_engine/brain/rules/`:
1. `vowel_harmony_matrix.json`: 2-way (*A-type*) and 4-way (*I-type*) harmony mappings, backness/rounding features.
2. `consonant_mutation_matrix.json`: Consonant lenition (*k/ğ, p/b, t/d, ç/c*), assimilation (*d/t, c/ç*), and non-leniting wordlists.
3. `agglutinative_suffix_chain.json`: Ordered slot positions for nominal and verbal inflectional morphemes.
4. `pragmatic_honorific_matrix.json`: T-V address triggers, postpositive honorifics (*Bey, Hanım, Hocam*), epistolary formulas.
