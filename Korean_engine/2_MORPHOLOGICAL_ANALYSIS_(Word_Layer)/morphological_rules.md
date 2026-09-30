# Korean Engine — Layer 2: Morphological Analysis (Word Layer)

## 1. Postpositional Particles (조사 / Josa)

Korean nominals are marked for syntactic case and semantic nuances via postpositive enclitics (*조사*). Crucially, the phonological form of many particles is conditioned by the presence or absence of a syllable-final consonant (**받침 / Batchim**):

### 1.1 Case Particles (격조사) & Allomorphy Matrix
| Case Function | After Consonant (받침 O) | After Vowel (받침 X) | Example (Consonant / Vowel) |
| :--- | :--- | :--- | :--- |
| **Topic / Contrast (*화제*)** | `-은` | `-는` | *책은* (as for book) / *사과는* (as for apple) |
| **Subject (*주격*)** | `-이` | `-가` | *선생님이* (teacher-NOM) / *친구가* (friend-NOM) |
| **Subject Honorific (*주체존칭*)** | `-께서` | `-께서` | *부모님께서* (parents-HON.NOM) |
| **Object (*목적격*)** | `-을` | `-를` | *밥을* (rice-ACC) / *커피를* (coffee-ACC) |
| **Genitive (*관형격*)** | `-의` [e/i] | `-의` [e/i] | *한국의* (Korea's) |
| **Dative / Locative (Inanimate)** | `-에` | `-에` | *학교에* (to/at school) |
| **Dynamic Locative / Source** | `-에서` | `-에서` | *집에서* (at home, from home) |
| **Dative / Goal (Animate)** | `-에게 / -한테` | `-에게 / -한테` | *친구에게* (to friend) / *형한테* (to brother) |
| **Dative Honorific (*존칭여격*)** | `-께` | `-께` | *선생님께* (to teacher) |
| **Instrumental / Directional** | `-으로` (after C except `ㄹ`) | `-로` (after V or `ㄹ`) | *책으로* (with book) / *서울로* (to Seoul) / *칼로* (with knife) |
| **Comitative / Coordinate** | `-과` | `-와` | *물과* (water and) / *차와* (tea and) |
| **Comparative** | `-보다` | `-보다` | *어제보다* (than yesterday) |

---

## 2. Predicate Inflection Architecture (용언의 활용 구조)

Korean verbs (*동사*) and adjectives (*형용사*) inflect identically through agglutinative suffix chains:

```
[ 어간 (Root/Stem) ] 
       + 
[ 선어말어미 (Pre-Final Endings) ]
   ├── 주체높임 (Subject Honorific): -(으)시-
   ├── 시제/상 (Tense/Aspect): -았/었/였- (Past), -더- (Retrospective)
   └── 양태/의지 (Modality/Intention): -겠- (Future/Conjecture/Will)
       + 
[ 어말어미 (Final Endings) ]
   ├── 종결어미 (Sentence Terminal): -다, -습니다, -어요, -니, -자, -십시오
   ├── 연결어미 (Conjunctive/Clause Chaining): -고, -며, -지만, -어서/아서, -면
   └── 전성어미 (Transforming: Nominal/Adnominal): -기, -ㅁ/음, -는, -(으)ㄴ, -(으)ㄹ
```

---

## 3. The Seven Irregular Conjugation Paradigms (7대 불규칙 활용)

When a verb/adjective stem meets a suffix beginning with a vowel (`-아/어`, `-(으)ㄴ`, `-(으)ㄹ`), stem alternations occur:

### 3.1 ㄷ-Irregular (ㄷ-불규칙)
Final `ㄷ` of the stem shifts to `ㄹ` before a vowel:
- *듣다* (to listen) $\to$ *들어요* (listen-POL), *들은* (listened), *들을* (will listen).
- *걷다* (to walk) $\to$ *걸어요*, *걸었다*.
- *Regular Contrasts*: *닫다* $\to$ *닫아요*, *받다* $\to$ *받아요*, *믿다* $\to$ *믿어요*.

### 3.2 ㅂ-Irregular (ㅂ-불규칙)
Final `ㅂ` drops and surfaces as `우` (or `오` after `ㅗ` in *돕다, 곱다*):
- *춥다* (to be cold) $\to$ *추워요* (`춥 + 어요` $\to$ `추 + 우 + 어요` $\to$ *추워요*).
- *어렵다* (to be difficult) $\to$ *어려워요*.
- *돕다* (to help) $\to$ *도와요* (`돕 + 아요` $\to$ `도 + 오 + 아요` $\to$ *도와요*).
- *Regular Contrasts*: *잡다* $\to$ *잡아요*, *뽑다* $\to$ *뽑아요*, *입다* $\to$ *입어요*.

### 3.3 ㅅ-Irregular (ㅅ-불규칙)
Final `ㅅ` drops before a vowel without diphthong coalescence:
- *짓다* (to build) $\to$ *지어요* (`짓 + 어요` $\to$ `지 + 어요`), *지은*, *지을*.
- *낫다* (to recover/better) $\to$ *나아요*.
- *Regular Contrasts*: *씻다* $\to$ *씻어요*, *벗다* $\to$ *벗어요*, *웃다* $\to$ *웃어요*.

### 3.4 르-Irregular (르-불규칙)
Vowel `으` drops and an additional `ㄹ` doubles into the preceding syllable's batchim:
- *빠르다* (to be fast) $\to$ *빨라요* (`빨` + `라요`).
- *부르다* (to call/sing) $\to$ *불러요* (`불` + `러요`).
- *모르다* (not know) $\to$ *몰라요*.

### 3.5 으-Drop (으-탈락)
Stem-final `으` unconditionally drops before `-아/어`:
- *크다* (to be big) $\to$ *커요*.
- *쓰다* (to write/use) $\to$ *써요*.
- *바쁘다* (to be busy) $\to$ *바빠요* (vowel harmony with preceding `ㅏ`).

### 3.6 ㅎ-Irregular (ㅎ-불규칙)
Color and demonstrative adjectives in `ㅎ` drop `ㅎ` and fuse with `-아/어` to form `ㅐ/ㅒ`:
- *그렇다* (to be so) $\to$ *그래요*.
- *파랗다* (to be blue) $\to$ *파래요*.
- *하얗다* (to be white) $\to$ *하얘요*.
- *Regular Contrasts*: *좋다* $\to$ *좋아요*, *놓다* $\to$ *놓아요*.

### 3.7 여-Irregular (여-불규칙)
The auxiliary verb *하다* takes `-여` instead of `-아/어`, contracting to `해`:
- *하다* $\to$ *하여* $\to$ *해요*, *공부하다* $\to$ *공부해요*.
