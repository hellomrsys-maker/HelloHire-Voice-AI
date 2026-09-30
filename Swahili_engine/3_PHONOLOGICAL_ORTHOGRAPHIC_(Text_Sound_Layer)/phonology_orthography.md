# Swahili Engine — Layer 3: Phonological & Orthographic Layer

## 1. Phonemic Inventory & Orthographic Mapping

Swahili uses a 24-letter Latin alphabet supplemented by specific digraphs:

### 1.1 Vowel System (Mfumo wa Irabu)
Swahili possesses a symmetrical 5-vowel system without distinctive vowel length or phonemic nasalization:
- `/a/` (*a*): low central unrounded (*baba*)
- `/e/` (*e*): mid-front unrounded (*mwezi*)
- `/i/` (*i*): high-front unrounded (*kiti*)
- `/o/` (*o*): mid-back rounded (*moto*)
- `/u/` (*u*): high-back rounded (*kuku*)

> **No Diphthongs**: Adjacent vowels always belong to separate syllables (*kuelea* = `ku-e-le-a`, 4 syllables; *ziara* = `zi-a-ra`, 3 syllables).

### 1.2 Consonant Digraphs & Arabic Influx Sounds
| Digraph | IPA | Phonetic Description | Canonical Example | Source |
| :--- | :--- | :--- | :--- | :--- |
| `ch` | /tʃ/ | Voiceless postalveolar affricate | *chumba* (room) | Bantu |
| `sh` | /ʃ/ | Voiceless postalveolar fricative | *shule* (school) | Loan / Bantu |
| `ny` | /ɲ/ | Palatal nasal | *nyumba* (house) | Bantu |
| `ng'` | /ŋ/ | Velar nasal (without following stop) | *ng'ombe* (cow), *ng'aa* (shine) | Bantu |
| `ng` | /ŋɡ/ | Pre-nasalized voiced velar stop | *ngoma* (drum) | Bantu |
| `dh` | /ð/ | Voiced dental fricative | *dhahabu* (gold), *fedha* (money) | Arabic |
| `th` | /θ/ | Voiceless dental fricative | *thelathini* (thirty), *hadithi* (story)| Arabic |
| `gh` | /ɣ/ | Voiced velar fricative | *ghali* (expensive), *lugha* (language) | Arabic |
| `kh` | /x/ | Voiceless velar fricative | *habari* / *kheri* (blessing) | Arabic |

---

## 2. Syllable Structure & The Penultimate Stress Law (Mkazo)

### 2.1 Universal Penultimate Stress
In standard Swahili, stress falls invariably on the **second syllable from the end (penultimate syllable)** of the word:
- `ki-TA-bu` (book)
- `wa-na-SO-ma` (they are reading)
- `wa-li-o-ki-SO-ma` (those who read it)

When suffixes are attached, stress automatically shifts rightward to maintain penultimate position:
- *kitabu* (`ki-TA-bu`) $\to$ *kitabuni* (`ki-ta-BU-ni` - "in the book").

### 2.2 Open Syllable Constraint (Silabi Wazi)
Indigenous Bantu words end exclusively in vowels. Consonant clusters are strictly restricted to:
1. **Pre-nasalized stops/fricatives**: `mb, nd, ng, nj, mv, nz` (*mbele, ndege, nguvu, njia*).
2. **Syllabic nasals**: When `m` or `n` carries its own syllabic beat:
   - *m-tu* (person, 2 syllables: `M-tu`)
   - *m-bwa* (dog, 2 syllables: `M-bwa`)
   - *n-chi* (country, 2 syllables: `N-chi`)

---

## 3. Monosyllabic Verbs & The Dummy *Ku-* Prefix

Because Swahili phonology requires words to be at least disyllabic to bear penultimate stress, monosyllabic verb stems (*vitenzi vyenye mzizi wa silabi moja*) require special morphological handling:

### 3.1 Monosyllabic Stems Inventory
`-la` (eat), `-nywa` (drink), `-ja` (come), `-fa` (die), `-pa` (give), `-cha` (rise/fear), `-enda` (go), `-isha` (finish).

### 3.2 The *Ku-* Retention Rule
Whenever a monosyllabic verb stem is conjugated with a monosyllabic tense prefix (*-na-, -li-, -ta-, -me-*), the infinitive prefix `ku-` is **obligatorily retained** as a stress-bearing dummy morpheme:
- *A-na-**ku**-la.* (He is eating — `a-na-KU-la`, 3 syllables).
  - *\*Anala* is completely ungrammatical.
- *A-li-**ku**-la.* (He ate).
- *A-ta-**ku**-la.* (He will eat).
- *A-me-**ku**-la.* (He has eaten).

### 3.3 The *Ku-* Dropping Rule
The dummy `ku-` is **dropped** whenever:
1. An Object Prefix is present: *A-li-**ki**-la.* ("He ate it" — *-ki-* bears the stress: `a-li-KI-la`).
2. Negative Present tense: *Ha-li.* ("He does not eat").
3. Habitual aspect: *Hu-la.* ("He usually eats").
4. Subjunctive mood: *A-l-e.* ("That he may eat").

---

## 4. Vowel Harmony in Verbal Extensions (Upatanisho wa Irabu)

Swahili verbal extensions (applicative *-i-/-e-*, causative *-ish-/-esh-*, stative *-ik-/-ek-*) follow strict height-assimilation vowel harmony:

$$\text{Root Vowel } \{a, i, u\} \implies \text{Extension Vowel } [i]$$
$$\text{Root Vowel } \{e, o\} \implies \text{Extension Vowel } [e]$$

| Verb Root | Root Vowel | Applicative (*-ia / -ea*) | Causative (*-isha / -esha*) | Stative (*-ika / -eka*) |
| :--- | :--- | :--- | :--- | :--- |
| *pika* (cook) | `i` | *pikia* (cook for) | *pikisha* (cause to cook) | *pikika* (be cookable) |
| *funga* (close) | `u` | *fungia* (close for) | *fungisha* (cause to close)| *fungika* (be closeable) |
| *pata* (get) | `a` | *patia* (get for) | *patisha* (cause to get) | *patika* (be obtainable)|
| *soma* (read) | `o` | *somea* (read to/for) | *somesha* (teach) | *someka* (be readable) |
| *tenda* (do) | `e` | *tendea* (do for) | *tendesha* (cause to do) | *tendeka* (be doable) |
