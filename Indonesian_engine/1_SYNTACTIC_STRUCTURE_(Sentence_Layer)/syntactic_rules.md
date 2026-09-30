# Layer 1: Syntactic Structure (Sentence Layer) — Indonesian Language Engine

## 1. Canonical SVO Constituent Architecture
Standard Indonesian (Bahasa Indonesia) is a head-initial, **SVO** (Subject-Verb-Object) language:
$$\text{Clause} = (\text{Topic}) + \text{Subject} + (\text{Aspect/Aux}) + (\text{Neg}) + \text{Verb} + \text{Direct Object} + (\text{Prepositional Phrase}) + (\text{Adjuncts})$$

### 1.1 Symmetrical Voice Alternation
Indonesian exhibits symmetrical voice alternation between Active Voice (*meN-*) and Passive Voice (*di-*):
- **Active Voice (Fokus Pelaku)**: Agent in subject position, verb marked with *meN-*:
  - *Budi membaca buku itu.* (Budi reads that book).
- **Canonical Passive (Fokus Penderita / Pasif Kanonikal)**: Patient in subject position, verb marked with *di-*, agent marked optionally by *oleh*:
  - *Buku itu dibaca (oleh) Budi.* (That book is read by Budi).
- **Zero-Passive / Pronominal Passive (Pasif Orang Pertama/Kedua)**: For 1st and 2nd person agents, the prefix *di-* is prohibited; instead, the bare stem is directly preceded by the cliticized agent:
  - *Buku itu sudah saya baca.* (That book I have read - not *\*Buku itu dibaca oleh saya* in standard formal style).
  - *Surat itu harus kau tulis.* (That letter you must write).

### 1.2 Zero-Copula Predication (Equational Clauses)
In standard Indonesian, non-verbal predicates (nominal, adjectival, prepositional, numeral) require **no copula verb**:
- Nominal: *Dia guru.* (She is a teacher).
- Adjectival: *Rumah itu besar.* (That house is big).
- Prepositional: *Ayah di kantor.* (Father is at the office).
- Numeral: *Anaknya tiga.* (Her children are three).
*(The word 'adalah' serves as a formal identifying copula in complex definition clauses, while 'merupakan' denotes 'constitutes').*

### 1.3 Negation Distribution: Tidak vs Bukan
Negation selection is strictly constrained by syntactic category:
1. **Tidak**: Negates verbs, adjectives, and prepositional phrases:
   - *Saya tidak makan.* (I do not eat).
   - *Dia tidak senang.* (He is not happy).
2. **Bukan**: Negates nouns, nominal predicates, pronouns, and contrastive clauses:
   - *Ini bukan buku saya.* (This is not my book).
   - *Dia bukan dokter, melainkan perawat.* (He is not a doctor, but a nurse).
   - Violation: *\*Saya bukan makan* or *\*Ini tidak buku*.

### 1.4 Preverbal Aspectual Modification
Verbs do not inflect for tense; TAM is encoded via preverbal particles:
- Completed / Perfective: *sudah*, *telah*.
- Negative Perfective: *belum* ("not yet").
- Progressive: *sedang*, *tengah*, *lagi* (informal).
- Prospective / Future: *akan*.
- Habitual / Frequentative: *sering*, *selalu*, *biasanya*.
