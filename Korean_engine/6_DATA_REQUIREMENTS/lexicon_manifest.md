# Korean Engine — Layer 6: Data Requirements & Lexicon Manifest

## 1. Primary Linguistic Corpora & Treebanks

The Korean Engine integrates standardized linguistic datasets and treebanks:

1. **Universal Dependencies (UD) Korean Treebanks**:
   - **UD Korean-Kaist**: 27,363 sentences annotated with UPOS and dependency relations based on the KAIST Treebank.
   - **UD Korean-GSD**: 6,329 sentences derived from Google Korean Universal Dependency Treebank, annotated with syntactic heads, lemmas, and features.
2. **The 21st Century Sejong Corpus (21세기 세종계획 말뭉치)**:
   - Over 200 million words of contemporary Korean text, tagged with the standard Sejong POS tagset (NNG, NNP, VV, VA, VX, VCP, VCN, JKS, JKC, JKG, JKO, JKB, JKV, JKQ, JX, JC, EP, EF, EC, ETN, ETM).
   - Provides canonical frequency counts for morphemes and predicate-argument co-occurrences.
3. **National Institute of Korean Language (국립국어원) Resources**:
   - **Standard Korean Language Dictionary (*표준국어대사전*)**: Over 500,000 headwords with canonical definitions, phonological pronunciations, and syntactic valency patterns.
   - **Korean Basic Dictionary (*한국어기초사전*)**: 50,000 high-frequency headwords mapped to CEFR/TOPIK proficiency levels (Levels 1–6).

---

## 2. Morpheme & Lexical Valency Databases

### 2.1 Postpositional Case Particle Lexicon (조사 사전)
Full inventory of case, auxiliary, and conjunctive particles with batchim conditioning flags:
- `JKS` (주격조사): *이/가, 께서*
- `JKO` (목적격조사): *을/를*
- `JKG` (관형격조사): *의*
- `JKB` (부사격조사): *에, 에서, 에게, 한테, 께, 으로/로, 와/과, 보다, 처럼*
- `JX` (보조사): *은/는, 도, 만, 까지, 부터, 마다, 조차*

### 2.2 Predicate Argument Structures (용언 격틀 사전)
Specifies obligatory argument frames for core verbs:
- *주다 / 드리다*: `[주어:가/께서] + [여격:에게/께] + [목적어:을/를] + [서술어]` (Trivalent)
- *좋아하다*: `[주어:이/가] + [목적어:을/를] + [서술어]` (Bivalent Transitive)
- *좋다*: `[주어:이/가] + [서술어]` (Monovalent Adjective)
- *만나다 / 뵙다*: `[주어:이/가] + [목적어:을/를] + [서술어]` / `[공동격:와/과] + [서술어]`

---

## 3. Conjugational Irregularity Tables (용언 불규칙 활용표)

The engine stores explicit stem-mapping tables for all 7 irregular paradigms:
1. **ㄷ-Irregular**: 18 core verbs (*듣다, 걷다, 묻다, 싣다, 긷다, 깨닫다, etc.*).
2. **ㅂ-Irregular**: ~400 verbs and adjectives (*춥다, 덥다, 돕다, 곱다, 맵다, 가볍다, 무겁다, etc.*).
3. **ㅅ-Irregular**: 12 core verbs (*짓다, 낫다, 붓다, 잇다, 젓다, etc.*).
4. **르-Irregular**: ~80 verbs (*빠르다, 부르다, 고르다, 오르다, 모르다, 흐르다, etc.*).
5. **으-Drop**: Universal rule for all `으`-final stems (*크다, 뜨다, 끄다, 쓰다, 담그다, etc.*).
6. **ㅎ-Irregular**: Color/demonstrative adjectives (*그렇다, 이렇다, 저렇다, 어떻다, 빨갛다, 파랗다, etc.*).
7. **여-Irregular**: *하다* and all composite `-하다` derived verbs (*공부하다, 운동하다, 사랑하다, etc.*).

---

## 4. Orthographic & Spelling Norms (한글 맞춤법)
- **Standard Korean Orthography (한글 맞춤법, 1988/2017 개정)**:
  - Article 1: "Standard Korean shall be written according to its pronunciation, while conforming to its morphemic identity (어법에 맞도록)."
  - Article 5: Consonant clustering and batchim pronunciation.
  - Spacing rules (띄어쓰기): Nominals and their following particles are attached without space (*조사는 그 앞말에 붙여 쓴다*: *학생이, 책을, 서울에서*).
