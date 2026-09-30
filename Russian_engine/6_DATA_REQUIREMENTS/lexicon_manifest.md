# Layer 6: Data Requirements & Lexicon Manifest (Russian Language Engine)

## 1. Corpus Foundations & Treebank Specifications

The Russian Computational Cognitive Engine integrates gold-standard linguistic corpora and formal grammatical dictionaries:

### 1.1 Corpora Sources
1. **Universal Dependencies (UD) Russian SynTagRus**:
   - The primary gold standard for syntactic dependency structures, morphological features, and surface syntax in contemporary Russian.
   - Tagset: Universal POS (UPOS) + Universal Features (Feats) with language-specific extensions (`Animacy[gram]=Anim|Inan`, `Variant=Short`).
2. **OpenCorpora Russian Morphological Dictionary**:
   - Over 5 million word forms with full morphological paradigm expansions, frequency indices, and lemma mappings.
3. **Zaliznyak's Grammatical Dictionary (Грамматический словарь русского языка А. А. Зализняка)**:
   - Indexical paradigm coding (e.g., noun types 1a, 2*b, verb types 1a/b, 4a/c) ensuring deterministic inflectional and accentological generation.

---

## 2. Core Lexicon Inventories

### 2.1 Verbal Aspect Pair Matrix (Видовые пары)
Aspectual pairs are stored with explicit derivation types:
- **Suffixal imperfectivization** (*-ыва- / -ива- / -ва-*): *переписать / переписывать*, *открыть / открывать*.
- **Prefixal perfectivization** (*по-, с-, про-, на-, за-*): *делать / сделать*, *писать / написать*, *читать / прочитать*.
- **Suppletive pairs**:
  - *говорить / сказать* (to speak / say)
  - *брать / взять* (to take)
  - *класть / положить* (to put / lay horizontally)
  - *ловить / поймать* (to catch)
  - *искать / найти* (to search / find)

### 2.2 Unprefixed Motion Verb Inventory (14 Core Pairs)

| Determinate (Unidirectional) | Indeterminate (Multidirectional) | English Gloss |
| :--- | :--- | :--- |
| **идти** | **ходить** | go on foot / walk |
| **ехать** | **ездить** | go by vehicle / drive / ride |
| **бежать** | **бегать** | run |
| **лететь** | **летать** | fly |
| **плыть** | **плавать** | swim / sail |
| **нести** | **носить** | carry (in hands) |
| **вести** | **водить** | lead / conduct / steer |
| **везти** | **возить** | transport (by vehicle) |
| **ползти** | **ползать** | crawl |
| **лезть** | **лазить / лазать** | climb |
| **брести** | **бродить** | stroll / wander |
| **катить** | **катать** | roll |
| **тащить** | **таскать** | drag / pull |
| **гнать** | **гонять** | chase / drive animals |

### 2.3 Prepositional & Verbal Case Government Valency

| Governor Type | Word / Governor | Obligatory Case Trigger | Example |
| :--- | :--- | :--- | :--- |
| **Preposition** | *без, для, до, из, от, у, около, после* | **Genitive** | *без сомнения*, *до дома* |
| **Compound Prep** | *в течение, в продолжение, ввиду* | **Genitive** | *в течение года*, *ввиду шторма* |
| **Preposition** | *к, по, благодаря, вопреки, согласно* | **Dative** | *к директору*, *благодаря помощи* |
| **Preposition** | *в, на, за, под* (Directional motion) | **Accusative** | *в комнату*, *на стол* |
| **Preposition** | *с, со* (Association / Comitative) | **Instrumental** | *с другом*, *с молоком* |
| **Preposition** | *над, под, перед, за* (Spatial static) | **Instrumental** | *над городом*, *перед входом* |
| **Preposition** | *о / об / обо, при* | **Prepositional** | *о книге*, *при встрече* |
| **Verb** | *бояться, избегать, лишать(ся), ждать* | **Genitive** | *бояться темноты* |
| **Verb** | *помогать, советовать, радоваться* | **Dative** | *помогать коллеге* |
| **Verb** | *управлять, руководить, владеть* | **Instrumental** | *управлять проектом* |
| **Verb** | *интересоваться, гордиться, заниматься* | **Instrumental** | *гордиться успехом* |

---

## 3. Computational Storage & JSON Schema

The Russian engine structures rule databases in `Russian_engine/brain/rules/`:
1. `verb_aspect_db.json`: Aspectual mapping, suppletion, Aktionsart derivation prefixes.
2. `case_declension_matrix.json`: 3 noun declensions, adjective endings, animacy splits, preposition government.
3. `motion_verbs_matrix.json`: Determinate/indeterminate pairs, directional prefixes.
4. `pragmatic_patronymic_matrix.json`: T-V address triggers, patronymic generation rules, epistolary formulas.
