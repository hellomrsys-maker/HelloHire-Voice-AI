# Layer 4: Semantic Representation & Idiomatic Systems (Russian Language Engine)

## 1. Theoretical Foundations: Russian Lexical Semantics & Conceptualization

The semantic architecture of Russian reflects a heavily aspectual, prefix-derivational, and case-relational worldview (Апресян, Зализняк, Вежбицкая). Meanings are encoded not merely through abstract roots, but through fine-grained morphological modifications that package event structure, intentionality, spatial vectoring, and agentive control directly into lexical forms.

### 1.1 Aktionsart (Способы действия / Modes of Action)
In Russian, aspect (Imperfective НСВ vs Perfective СВ) interacts with prefixation and suffixation to produce Aktionsarten—systematic semantic modifications of lexical aspect:

| Aktionsart | Semantic Characterization | Morphological Marker | Example | English Gloss |
| :--- | :--- | :--- | :--- | :--- |
| **Ingressive / Inchoative** | Inception of state/action | *за-* | *петь* → *запеть* | to begin singing |
| **Delimitative** | Action performed for a short, finite duration | *по-* | *читать* → *почитать* | to read for a little while |
| **Perdurative** | Action spanning an entire specified duration | *про-* | *спать* → *проспать (всю ночь)* | to sleep through (the entire night) |
| **Cumulative** | Accumulation of object/quantity | *на-* (+ Partitive Genitive) | *печь* → *напечь (блинов)* | to bake a quantity of pancakes |
| **Exhaustive / Totalizing** | Exhaustion of subject/agent energy | *у-* + *-ся*, *из-* + *-ся* | *бегать* → *убегаться* | to run oneself ragged / to exhaustion |
| **Distributive** | Action distributed across multiple objects/agents | *пере-* | *бить* → *перебить (все тарелки)* | to smash all the plates one by one |
| **Semelfactive** | Single, instantaneous, punctual occurrence | *-ну-* | *колоть* → *кольнуть* | to prick once / give a sharp sting |
| **Attenuative** | Reduced intensity of action | *при-* / *под-* | *открыть* → *приоткрыть* | to open slightly (ajar) |

### 1.2 Lexicalization of Direction & Intentionality: Prefixed Motion Verbs
Motion verbs in Russian lexicalize spatial orientation with topological precision:
- **Base Pairs**: *идти / ходить* (indeterminate vs determinate; unidirectional vs multidirectional).
- **Prefix Matrices**:
  - *в(о)-* (inward / penetration): *войти / входить* (enter).
  - *вы-* (outward / exit): *выйти / выходить* (exit).
  - *до-* (attainment of terminus): *дойти / доходить* (reach / arrive on foot).
  - *пере-* (transversal across surface): *перейти / переходить* (cross over).
  - *про-* (transit past or through): *пройти / проходить* (pass by / walk through).
  - *у-* (departure away from origin): *уйти / уходить* (leave / depart).
  - *под(о)-* (approach to proximity): *подойти / подходить* (+ *к* + Dat: approach).
  - *от(о)-* (recession to distance): *отойти / отходить* (+ *от* + Gen: step away).

### 1.3 Impersonal Semantic Frames & Involuntary Agency
Russian prominently features impersonal constructions where animate human participants are cast in the **Dative Case**, representing them not as volitional nominative agents, but as experiencers subjected to external, physical, or emotional states:
- *Мне хочется спать.* ("To me it is wanting to sleep" → I feel like sleeping).
- *Ему не спится.* ("To him it is not sleeping itself" → He cannot sleep).
- *Нам повезло.* ("To us it lucky-transited" → We got lucky).
- *Тебе следует знать.* ("To thee it is behooved to know" → You ought to know).

---

## 2. Idiomatic Inventory & Phrasal Semantics (Фразеологизмы)

Russian idiomaticity relies heavily on culturally grounded somatic metaphors, historical folklore, and expressive syntactic reduplications:

### 2.1 Somatic & Body-Part Idioms
1. **Бить баклуши** (*lit.* to beat wooden blocks for spoons)
   - *Meaning*: To idle, slack off, waste time.
   - *Semantic Category*: Labor / Idleness.
   - *Valency*: Intransitive.

2. **Водить за нос** (*lit.* to lead by the nose)
   - *Meaning*: To deceive, mislead, string someone along.
   - *Valency*: Transitive (+ Acc: *кого-либо*).

3. **Вешать нос** (*lit.* to hang one's nose)
   - *Meaning*: To despond, become dejected, lose heart.
   - *Usage*: Frequently in negative imperative (*Не вешай нос!* — Cheer up!).

4. **Зарубить на носу** (*lit.* to notch on one's tally-stick/nose)
   - *Meaning*: To remember firmly once and for all, take to heart.
   - *Valency*: + Clause or Acc (*Заруби себе на носу, что...*).

5. **Спустя рукава** (*lit.* having lowered one's sleeves)
   - *Meaning*: Carelessly, sloppily, half-heartedly.
   - *Adverbial Modifier*: *работать спустя рукава* (to work carelessly).
   - *Antonym*: *засучив рукава* (with rolled-up sleeves / diligently).

### 2.2 Relational & Evaluative Idioms
1. **Ни рыба ни мясо** (*lit.* neither fish nor meat)
   - *Meaning*: Wishy-washy, nonentity, neither here nor there.
   - *Syntactic Function*: Predicate complement or adjectival modifier.

2. **Семь пятниц на неделе** (*lit.* seven Fridays in a week)
   - *Meaning*: Fickle, perpetually changing one's mind/plans.
   - *Idiomatic Frame*: *У него семь пятниц на неделе.*

3. **Как снег на голову** (*lit.* like snow on the head)
   - *Meaning*: Completely unexpected, out of the blue.
   - *Semantic Category*: Suddenness / Surprise.

4. **Держать в ежовых рукавицах** (*lit.* to hold in hedgehog mittens)
   - *Meaning*: To rule with an iron fist, treat with strict discipline.
   - *Valency*: + Acc of patient.

---

## 3. Computational Semantic Graph & Case Role Mapping

```
[Agent / Source] --(Nominative/Genitive)--> [Event / Predicate] --(Accusative/Genitive)--> [Patient]
       |                                           |
(Dative: Experiencer/Recipient)             (Instrumental: Means/Manner)
       |                                           |
       v                                           v
[Psychological State / Involuntary Force]    [Tool / Agent of Passive / Trajectory]
```

- **Objective Genitive vs Partitive Genitive**: Verbs of seeking, expecting, or consuming (*искать, ждать, выпить*) trigger Accusative for concrete specific entities (*выпить эту воду*), but Genitive for abstract, negated, or indefinite quantities (*выпить воды*, *ждать поезда*, *не видеть смысла*).
- **Instrumental of Agency & Means**: *Писать ручкой* (means), *Книга написана автором* (passive agent), *Лес пахнет хвоей* (predicate complement of sensory verbs).
