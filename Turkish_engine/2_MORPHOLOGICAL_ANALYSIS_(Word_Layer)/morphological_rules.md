# Layer 2: Morphological Analysis & Agglutinative Architecture (Turkish Language Engine)

## 1. Agglutinative Suffix Chain Topography

Turkish morphology is characterized by clean, transparent agglutinative suffix chains appended to invariant lexical roots. Each bound morpheme expresses a single distinct grammatical category, ordered according to strict morphological slot constraints:

### 1.1 Nominal Inflectional Template (İsim Çekimi)

```
[Root / Stem] + [Derivation] + [Plural] + [Possessive] + [Case]
    (Kök)           (Yapım)       (Çoğul)    (İyelik)     (Hâl)
```

Example Expansion:
- *ev* (house)
- *ev-ler* (houses)
- *ev-ler-imiz* (our houses)
- *ev-ler-imiz-den* (from our houses)
- *ev-ler-imiz-de-ki* (the one in our houses - Relational *-ki*)

### 1.2 Verbal Inflectional Template (Fiil Çekimi)

```
[Verb Root] + [Voice] + [Ability] + [Negation] + [TAM 1] + [TAM 2 / Copula] + [Person]
```

Example Expansion:
- *oku* (read)
- *oku-t* (cause to read / teach - Causative)
- *oku-t-ul* (be taught - Passive)
- *oku-t-ul-abil* (can be taught - Abilitative)
- *oku-t-ul-a-ma* (cannot be taught - Negative Abilitative)
- *oku-t-ul-a-ma-mış-tı* (it had reportedly not been able to be taught - Pluperfect Evidential)

---

## 2. The Turkish Case System (İsmin Hâlleri)

Turkish distinguishes six nominal cases, each realized through harmonic suffix allomorphs:

| Case | Grammatical Function | Harmonic Suffix Pattern | Buffer Consonant | Example (ev / araba) |
| :--- | :--- | :--- | :--- | :--- |
| **Nominative** | Subject, citation form, non-specific object | $\emptyset$ (unmarked) | None | *ev*, *araba* |
| **Accusative** | Definite / specific direct object | *-i / -ı / -ü / -u* (4-way) | *y* / *n* | *ev-i*, *araba-y-ı*, *kapı-s-ı-n-ı* |
| **Dative** | Goal, recipient, direction, postpositional | *-e / -a* (2-way) | *y* / *n* | *ev-e*, *araba-y-a*, *oda-s-ı-n-a* |
| **Locative** | Static physical or temporal location | *-de / -da / -te / -ta* | *n* (after 3sg poss) | *ev-de*, *araba-da*, *masa-s-ı-n-da* |
| **Ablative** | Source, point of departure, comparison | *-den / -dan / -ten / -tan*| *n* (after 3sg poss) | *ev-den*, *araba-dan*, *ev-i-n-den* |
| **Genitive** | Possessor, subject of nominal clause | *-(n)in / -(n)ın / -(n)ün / -(n)un* | *n* | *ev-in*, *araba-n-ın* |

---

## 3. Buffer Consonants (Kaynaştırma Harfleri: Y, Ş, S, N)

When a suffix beginning with a vowel attaches to a vowel-final stem, a phonological buffer consonant is inserted to prevent hiatus:

1. **Y (General Hiatus Breaker)**:
   - Dative: *masa-y-a* (to the table).
   - Accusative: *pencere-y-i* (the window - DO).
   - Past / Participle: *oku-y-an* (the one reading).
2. **N (Pronominal & Genitive Buffer)**:
   - Genitive: *araba-n-ın* (of the car).
   - Case marker following 3rd person possessive: *araba-sı-n-dan* (from his/her car), *ev-i-n-de* (in his/her house).
3. **S (3rd Person Possessive Buffer)**:
   - *anne-s-i* (his/her mother), *araba-s-ı* (his/her car).
4. **Ş (Distributive Numeral Buffer)**:
   - *iki-ş-er* (two each), *altı-ş-ar* (six each).

---

## 4. Verbal Tense, Aspect, Modality (TAM) & Evidentiality

### 4.1 Major Tenses & Aspect Markers

| Category | Suffix | Meaning | Example (*yazmak* - write) |
| :--- | :--- | :--- | :--- |
| **Present Continuous** | *-(i)yor* | Progressive, current activity | *yaz-ıyor* (is writing) |
| **Definite Past** | *-di / -dı / -tü / -tu* | Direct sensory eyewitness past | *yaz-dı* (wrote) |
| **Evidential / Hearsay Past**| *-miş / -mış / -müş / -muş*| Inferred, reported, mirative past | *yaz-mış* (reportedly wrote / has written) |
| **Future** | *-(y)ecek / -(y)acak* | Planned or definite future | *yaz-acak* (will write) |
| **Aorist / Simple Present** | *-r / -er / -ar / -ir* | Habitual, timeless fact, polite request| *yaz-ar* (writes / will write) |
| **Necessitative** | *-meli / -malı* | Obligation, necessity (must, should) | *yaz-malı* (must write) |
| **Conditional** | *-se / -sa* | Real or hypothetical condition | *yaz-sa* (if he wrote) |
| **Optative / Subjunctive** | *-(y)e / -(y)a* | Desire, exhortation, suggestion | *yaz-a-lım* (let us write) |

### 4.2 Evidentiality (*-miş*) Semantics
The evidential suffix encodes epistemic source of knowledge:
1. **Hearsay / Indirect Report**: *Ahmet dün gelmiş.* ("Ahmet reportedly came yesterday [someone told me]").
2. **Inference from Physical Evidence**: *Yağmur yağmış.* ("It must have rained [the streets are wet]").
3. **Mirativity (Surprise / Immediate Realization)**: *Cüzdanımı evde unutmuşum!* ("I [suddenly realize that I] left my wallet at home!").
