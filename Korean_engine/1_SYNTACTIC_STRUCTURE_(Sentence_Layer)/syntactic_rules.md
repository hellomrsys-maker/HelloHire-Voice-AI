# Korean Engine — Layer 1: Syntactic Structure (Sentence Layer)

## 1. Clausal Typology: Head-Final SOV & Agglutinative Scrambling

Korean (*한국어 / Hangugeo*) is a strictly head-final, dependent-marking, agglutinative language:

### 1.1 Canonical Word Order (SOV)
The finite verbal or adjectival predicate strictly anchors the clause-final position:
```
[Subject - 주어]    [Indirect/Direct Object - 목적어]    [Verb/Adjective - 서술어]
   학생이                  책을                             읽는다.
  (Student-NOM)          (book-ACC)                         (reads)
```

### 1.2 Scrambling & Topic-Focus Architecture
Because grammatical relations are marked overtly by postpositional case particles (*조사 / Josa*), pre-verbal constituents enjoy considerable scrambling freedom:
- Canonical: `[주어] + [시간] + [장소] + [목적어] + [서술어]` (*민수가 오늘 도서관에서 책을 읽었다.*)
- Topicalized: `[시간] + [주어] + [목적어] + [장소] + [서술어]` (*오늘 민수가 책을 도서관에서 읽었다.*)
- Object Focus: `[목적어] + [주어] + [서술어]` (*그 책을 민수가 읽었다.*)

> **Invariable Constraint**: Regardless of pre-verbal permutation, the finite predicate MUST remain clausal-final.

---

## 2. Topic vs. Subject Distinction: 은/는 vs. 이/가

Korean distinguishes information-structural **Topic/Contrast** (*화제/대조*) from grammatical **Subject/Focus** (*주어/초점*):

| Feature | Topic Particle (*은/는*) | Subject Particle (*이/가*) |
| :--- | :--- | :--- |
| **Phonological Conditioning** | `-은` after C, `-는` after V | `-이` after C, `-가` after V |
| **Information Status** | Old/Shared Information (Theme) | New Information (Rheme / Focus) |
| **Pragmatic Force** | "As for X..." / Contrast ("X, unlike Y") | Exhaustive listing ("It is X that...") |
| **Example** | *저는 학생입니다.* ("As for me, I am a student.") | *제가 학생입니다.* ("I [and not someone else] am the student.") |

---

## 3. Pre-Nominal Head-Final Relative Clauses (관형사절)

Unlike English post-nominal relative clauses (*the book that I read*), Korean relative clauses strictly precede their head nouns using adnominal participial endings (*관형사형 전성어미*):

| Tense / Aspect | Suffix after Vowel | Suffix after Consonant | Example with *읽다* (to read) | Resulting NP |
| :--- | :--- | :--- | :--- | :--- |
| **Present (*현재*)** | `-는` | `-는` | *읽는* | *내가 읽는 책* ("the book I read") |
| **Past (*과거*)** | `-ㄴ` | `-은` | *읽은* | *내가 읽은 책* ("the book I read [yesterday]") |
| **Future / Prospective (*미래/추측*)** | `-ㄹ` | `-을` | *읽을* | *내가 읽을 책* ("the book I will read") |
| **Retrospective (*회상*)** | `-던` | `-던` | *읽던* | *내가 읽던 책* ("the book I used to read") |

---

## 4. Pro-Drop (Ellipsis of Known Arguments)

Korean is an extreme **radical pro-drop language**:
- Any argument (subject, direct object, indirect object, topic) that is recoverable from context or situational discourse is routinely omitted.
- Imperatives and polite requests typically lack an overt subject:
  - *밥 먹었어요?* ("Did [you] eat rice/meal?") — Both subject (*당신은*) and object (*밥을*) can be optionally dropped: *먹었어요?*
- The syntax engine must handle bare predicates as complete, well-formed grammatical clauses.

---

## 5. Clausal Nominalization & Complementation

Subordinate clauses are nominalized to act as clausal arguments:
1. **Fact / Event Nominalization with `-는 것`**:
   - *한국어를 배우는 것은 재미있습니다.* ("Learning Korean is fun.")
2. **Abstract / Concept Nominalization with `-기`**:
   - *읽기* (reading), *쓰기* (writing), *한국어 배우기를 시작했다* ("Started learning Korean").
3. **Quotation / Indirect Discourse with `-고`**:
   - Declarative: `...다고 하다 / 말했다` (*그는 온다고 말했다* - "He said he would come.")
   - Interrogative: `...냐고 묻다` (*언제 오냐고 물었다* - "Asked when [he] would come.")
