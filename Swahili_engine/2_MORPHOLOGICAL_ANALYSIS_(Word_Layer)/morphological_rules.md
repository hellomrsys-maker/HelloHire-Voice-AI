# Swahili Engine — Layer 2: Morphological Analysis (Word Layer)

## 1. The 18 Bantu Noun Classes (Ngeli za Nomino)

In Swahili morphology, every noun belongs to an intrinsic noun class (*ngeli*) which governs the agreement affixes attached to adjectives, demonstratives, possessives, associatives, and verbs:

### 1.1 Complete Noun Class Agreement Concord Table
| Class | Semantic Category | Noun Prefix | Adjective Prefix | Possessive / Associative | Dem (This / That) | Verb SP | Verb OP | Canonical Examples |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 (M/MW)** | Human Sing. | `m- / mw-` | `m- / mw-` | `w- (wa)` | `huyu / yule` | `a-` | `-m- / -mw-` | *mtu, mtoto, mwalimu* |
| **2 (WA)** | Human Plur. | `wa-` | `wa-` | `w- (wa)` | `hawa / wale` | `wa-` | `-wa-` | *watu, watoto, walimu* |
| **3 (M/MW)** | Trees / Non-human Sing. | `m- / mw-` | `m- / mw-` | `w- (wa)` | `huu / ule` | `u-` | `-u-` | *mti, mto, mji, mkono* |
| **4 (MI)** | Trees / Non-human Plur. | `mi-` | `mi-` | `y- (ya)` | `hii / ile` | `i-` | `-i-` | *miti, mito, miji, mikono* |
| **5 (JI/Ø)** | Fruits / Augmentative Sing. | `ji- / Ø` | `ji- / Ø` | `l- (la)` | `hili / lile` | `li-` | `-li-` | *jicho, jina, embe, gari* |
| **6 (MA)** | Fruits Plur. / Collectives | `ma-` | `ma-` | `y- (ya)` | `haya / yale` | `ya-` | `-ya-` | *macho, majina, maembe, maji* |
| **7 (KI/CH)** | Artifacts / Diminutive Sing. | `ki- / ch-` | `ki- / ch-` | `ch- (cha)` | `hiki / kile` | `ki-` | `-ki-` | *kitabu, kiti, chumba, chakula* |
| **8 (VI/VY)** | Artifacts / Diminutive Plur. | `vi- / vy-` | `vi- / vy-` | `vy- (vya)` | `hivi / vile` | `vi-` | `-vi-` | *vitabu, viti, vyumba, vyakula* |
| **9 (N/Ø)** | Animals / Invariable Loans Sing.| `n- / ny- / Ø` | `n- / ny- / Ø` | `y- (ya)` | `hii / ile` | `i-` | `-i-` | *nyumba, safari, simba, meza* |
| **10 (N/Ø)** | Animals / Invariable Loans Plur.| `n- / ny- / Ø` | `n- / ny- / Ø` | `z- (za)` | `hizi / zile` | `zi-` | `-zi-` | *nyumba, safari, simba, meza* |
| **11/14 (U)** | Abstract / Long Sing. | `u- / w-` | `m- / mw-` | `w- (wa)` | `huu / ule` | `u-` | `-u-` | *uhuru, ukuta, ufunguo* |
| **15 (KU)** | Infinitives / Gerunds | `ku- / kw-` | `ku- / kw-` | `kw- (kwa)` | `huku / kule` | `ku-` | `-ku-` | *kusoma, kuimba, kucheza* |
| **16 (PA)** | Specific Definite Location | `pa-` | `pa-` | `p- (pa)` | `hapa / pale` | `pa-` | `-pa-` | *mahali hapa, pale* |
| **17 (KU)** | Indefinite / Directional Location| `ku-` | `ku-` | `kw- (kwa)` | `huku / kule` | `ku-` | `-ku-` | *mahali huku, kule* |
| **18 (MU)** | Internal / Enclosed Location | `mu- / m-` | `mu- / m-` | `mw- (mwa)` | `humu / mle` | `mu-` | `-mu-` | *mahali humu, mle* |

---

## 2. Agglutinative Verbal Prefix/Suffix Template

The Swahili finite verb is a micro-sentence constructed across 8 rigid morphological slots:

$$\text{Verb} = [\text{Slot 1: Neg}] + [\text{Slot 2: SP}] + [\text{Slot 3: TAM}] + [\text{Slot 4: Rel}] + [\text{Slot 5: OP}] + [\text{Slot 6: Root}] + [\text{Slot 7: Ext}] + [\text{Slot 8: FV}]$$

### 2.1 Slot Breakdown
1. **Slot 1 (Pre-initial / Negation)**: `ha-` (except 1sg which fuses with SP: `si-`).
2. **Slot 2 (Subject Prefix SP)**:
   - 1sg: `ni-` (Neg: `si-`) | 1pl: `tu-` (Neg: `ha-tu-`)
   - 2sg: `u-` (Neg: `h-u-`) | 2pl: `m-` (Neg: `ha-m-`)
   - 3sg: `a-` (Neg: `h-a-`) | 3pl: `wa-` (Neg: `ha-wa-`)
   - Classes 3..18: `u-, i-, li-, ya-, ki-, vi-, zi-, ku-, pa-, mu-`
3. **Slot 3 (TAM Tense/Aspect/Mood)**:
   - Present Continuous: `-na-`
   - Simple Past: `-li-`
   - Future: `-ta-`
   - Perfect: `-me-`
   - Conditional: `-ki-` ("if / while")
   - Hypothetical: `-nge-` ("would")
   - Narrative: `-ka-` ("and then")
   - Habitual: `hu-` (replaces SP + TAM: *husema*, *hula*)
4. **Slot 4 (Infix Relative)**: `-ye-` (Cl 1), `-o-` (Cl 2), `-cho-` (Cl 7), `-vyo-` (Cl 8), `-lo-` (Cl 5), `-yo-` (Cl 4/9), `-zo-` (Cl 10).
5. **Slot 5 (Object Prefix OP)**: `-ni-, -ku-, -m-, -tu-, -wa-, -ki-, -vi-, -zi-, etc.`
6. **Slot 6 (Verb Root)**: The lexical core (e.g. `-som-` [read], `-pik-` [cook], `-on-` [see]).
7. **Slot 7 (Verbal Extensions)**: `-i-/-e-` (App), `-ish-/-esh-` (Caus), `-w-` (Pass), `-an-` (Recip), `-ik-/-ek-` (Stat).
8. **Slot 8 (Final Vowel FV)**:
   - Indicative default: `-a` (*anasoma*)
   - Present negative: `-i` (*hasomi*)
   - Subjunctive / Optative / Imperative Plural: `-e` (*asome, someni*)

---

## 3. Systematic Negation Architecture

Negation in Swahili triggers simultaneous shifts in both the pre-initial prefix and the TAM / Final Vowel:

| Tense / Aspect | Affirmative Form | Negative Form | Example (Affirmative / Negative) |
| :--- | :--- | :--- | :--- |
| **Present (*-na-*)** | `SP + -na- + Root + -a` | `NEG-SP + Root + -i` | *ninasoma* $\to$ *sisomi* / *wanasoma* $\to$ *hawasomi* |
| **Past (*-li-*)** | `SP + -li- + Root + -a` | `NEG-SP + -ku- + Root + -a` | *nilisoma* $\to$ *sikosoma* / *walisoma* $\to$ *hawakusoma* |
| **Future (*-ta-*)** | `SP + -ta- + Root + -a` | `NEG-SP + -ta- + Root + -a` | *nitasoma* $\to$ *sitasoma* / *watasoma* $\to$ *hawatasooma* |
| **Perfect (*-me-*)** | `SP + -me- + Root + -a` | `NEG-SP + -ja- + Root + -a` ("not yet") | *nimesoma* $\to$ *sijasoma* / *wamesoma* $\to$ *hawajasoma* |
| **Subjunctive (*-e*)** | `SP + Root + -e` | `SP + -si- + Root + -e` | *asome* $\to$ *asisome* ("he should not read") |
