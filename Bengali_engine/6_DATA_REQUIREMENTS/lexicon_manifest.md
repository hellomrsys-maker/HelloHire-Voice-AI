# Layer 6: Data Requirements & Lexicon Manifest - Bengali Engine (বাংলা)

## 1. Corpus Foundations & Annotation Standards
The Bengali engine integrates treebanks, lexicons, and corpora aligned with the Universal Dependencies (UD) framework:
- **UD Bengali-BC / UD Bengali-BS Treebanks**: CoNLL-U format annotated for POS tags, morphological features, and dependency graphs.
- **ILCI Bengali Corpus**: Indian Languages Corpora Initiative (Health, Tourism, and General Domains).
- **BanglaNet (Bengali WordNet)**: Synset relations, hyponymy, hypernymy, and semantic classes.
- **BDLex / Ananda Bazar Patrika Corpus**: Standard lexical frequency and collocation distributions.

---

## 2. Core Lexicon Manifests

### 1. Simplex Verbs Inventory
The core engine database maintains root lemmas categorized into conjugation classes:
- *করা* (`kora` - to do), *দেওয়া* (`dewa` - to give), *নেওয়া* (`newa` - to take), *পড়া* (`poda` - to read/study), *লেখা* (`lekha` - to write), *বলা* (`bola` - to say), *দেখা* (`dekha` - to see), *খাওয়া* (`khawa` - to eat), *যাওয়া* (`jawa` - to go), *আসা* (`asha` - to come), *শোনা* (`shona` - to hear), *জানা* (`jana` - to know), *থাকা* (`thaka` - to stay), *হওয়া* (`howa` - to become).

### 2. Vector Verbs Inventory
The 8 canonical aspectual auxiliary vector verbs:
- *ফেলা* (`phela`), *রাখা* (`rakha`), *দেওয়া* (`dewa`), *নেওয়া* (`newa`), *ওঠা* (`othha`), *বসা* (`bosa`), *যাওয়া* (`jawa`), *আসা* (`asha`).

### 3. Postposition & Case Marker Inventory
- Inherent case suffixes: `-ke` (objective), `-er/-r` (genitive), `-e/-te/-y` (locative).
- Free postpositions governing Genitive: *জন্য* (`jonno`), *সাথে* (`sathe`), *সঙ্গে* (`shonge`), *কাছে* (`kache`), *সামনে* (`shamne`), *পিছনে* (`pichhone`), *ভিতরে* (`bhitore`), *বাইরে* (`baire`), *উপরে* (`upore`), *নিচে* (`niche`), *আগে* (`aage`), *পরে* (`pore`).
- Free postpositions governing Nominative / Direct: *দিয়ে* (`diye` - with/by), *থেকে* (`theke` - from), *হতে* (`hote` - from), *পর্যন্ত* (`porjonto` - until).

### 4. Classifier Enclitics (*Nirdeshok*)
- Singular definite: `-Ta` (general), `-Ti` (polite/small), `-khana` (flat), `-khani` (poetic flat).
- Plural definite: `-gulo` (general), `-guli` (polite/formal).
- Human numeral: `-jon`.

---

## 3. Lexical Distribution & Register Mapping
- **Tatsama (সংস্কৃত তৎসম)**: ~25% in modern spoken, ~55% in Sadhu Bhasha and formal technical prose.
- **Tadbhav (তদ্ভব - Middle Indo-Aryan derived)**: ~50% in standard colloquial prose.
- **Deshi (দেশি - Indigenous Austroasiatic/Dravidian substrate)**: ~10% everyday terms (*কুঁড়ে* `kũde`, *চিংড়ি* `chingdi`).
- **Bideshi (বিদেশি - Arabic, Persian, Portuguese, English loanwords)**: ~15% (*কলম* `kolom`, *আইন* `aain`, *টেবিল* `tebil`, *চাবি* `chabi`).
