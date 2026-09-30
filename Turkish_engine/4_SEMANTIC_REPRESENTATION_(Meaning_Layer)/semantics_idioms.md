# Layer 4: Semantic Representation & Idiomatic Systems (Turkish Language Engine)

## 1. Epistemic Modality, Evidentiality & Valency Geometry

Turkish semantic architecture constructs complex events through recursive derivational voice morphology and fine-grained epistemic marking:

### 1.1 Voice Derivations & Valency Alternations
Voice suffixes can be recursively chained onto a verbal root, directly altering its argument structure:

| Voice Suffix | Morphological Marker | Semantic Function | Example Base | Derived Form & Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **Causative** | *-dir / -t / -ir / -er* | Increases valency by adding an external causer | *oku-* (read) | *oku-t-* (cause to read / teach) |
| **Double Causative** | *-t-tir* | Introduces secondary delegative agency | *temizle-* (clean) | *temizle-t-tir-* (have someone get it cleaned) |
| **Passive** | *-il / -in* (after vowels/l) | Suppresses agent, promotes patient to subject | *yaz-* (write) | *yaz-ıl-* (be written) |
| **Reflexive** | *-in* | Subject and direct object are coreferential | *yıka-* (wash) | *yıka-n-* (wash oneself, bathe) |
| **Reciprocal** | *-iş* | Mutual or collective joint action | *gör-* (see) | *gör-üş-* (meet, see one another) |

### 1.2 Compound Verbs with Auxiliaries (Birleşik Fiiller)
Nominal concepts (often of Arabic, Persian, or French origin) are verbalized using invariant Turkish light auxiliary verbs:
- **etmek** (do/perform): *yardım etmek* (to help), *kabul etmek* (to accept), *teşekkür etmek* (to thank).
- **olmak** (be/become): *sahip olmak* (to own/possess), *memnun olmak* (to be pleased).
- **kılmak** (render): *mümkün kılmak* (to make possible), *etkisiz kılmak* (to neutralize).

---

## 2. Idiomatic Inventory & Phrasal Semantics (Deyimler)

Turkish idiomatic expressions (*deyimler*) are rich in somatic metaphors, sensory extensions, and cultural allegories:

### 2.1 Somatic Idioms (Vücut Organı Deyimleri)
1. **Gözden düşmek** (*lit.* to fall from the eye)
   - *Meaning*: To lose favor, fall out of esteem, be discredited.
   - *Antonym*: *Göze girmek* (to find favor, impress someone).

2. **Kulak kabartmak** (*lit.* to fluff one's ear)
   - *Meaning*: To listen intently without showing it, eavesdrop discreetly.
   - *Related*: *Kulak ardı etmek* (to brush aside, ignore).

3. **Burun kıvırmak** (*lit.* to curl one's nose)
   - *Meaning*: To look down upon, disparage, turn up one's nose at.

4. **Ağzı kulaklarına varmak** (*lit.* one's mouth reaching one's ears)
   - *Meaning*: To be overjoyed, grin from ear to ear.

5. **Etekleri zil çalmak** (*lit.* the bells on one's skirts ringing)
   - *Meaning*: To be thrilled with excitement, rejoice intensely.

### 2.2 Proverbial & Conceptual Idioms
1. **Pireyi deve yapmak** (*lit.* to make a camel out of a flea)
   - *Meaning*: To exaggerate greatly, make a mountain out of a molehill.

2. **Çantada keklik** (*lit.* partridge in the bag)
   - *Meaning*: A sure thing, something guaranteed or easily obtained.

3. **Saman alevi gibi** (*lit.* like a straw flame)
   - *Meaning*: Short-lived enthusiasm or anger that flares up and vanishes quickly.

4. **İki ayağını bir pabuca sokmak** (*lit.* to put two feet into one shoe)
   - *Meaning*: To rush someone frantically, cause undue haste.

---

## 3. Computational Semantic Graph & Conceptual Integration

```
[Agent] --(Genitive / Nominative)--> [Causative Event] --(Dative: Causee)--> [Patient (Accusative)]
   |                                          |
(Source: Ablative)                      (Goal: Dative)
   |                                          |
   v                                          v
[Physical / Conceptual Origin]        [Destination / Terminus]
```

- **Differential Object Marking**: Direct objects marked with Accusative (*-i*) introduce a specificity operator into semantic scope, whereas unmarked objects undergo semantic incorporation into the verbal complex.
- **Evidential Modality Mapping**: Sentences inflected with *-miş* wrap the entire propositional content in a modal epistemic operator $\mathcal{E}_{\text{indirect}}(P)$, projecting uncertainty or indirect testimony into discourse state.
