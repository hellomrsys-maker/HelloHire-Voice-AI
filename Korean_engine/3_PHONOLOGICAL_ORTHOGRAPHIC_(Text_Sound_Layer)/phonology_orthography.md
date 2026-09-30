# Korean Engine — Layer 3: Phonological & Orthographic Layer

## 1. Hangul (한글) Syllabic Composition & Unicode Architecture

Hangul is a featural phonemic alphabet organized into 2- or 3-dimensional syllabic blocks (*음절*):
`[ Initial Consonant (초성) ] + [ Medial Vowel (중성) ] + [ Final Consonant (종성/받침) - optional ]`

### 1.1 The Unicode Syllable Arithmetic
Korean syllables in Unicode range from `U+AC00` (*가*) to `U+D7A3` (*힣*), spanning exactly 11,172 precomposed syllabic blocks:
$$\text{CodePoint} = \text{0xAC00} + ((\text{Initial} \times 21) + \text{Medial}) \times 28 + \text{Final}$$

- **19 Initial Consonants (초성)**:
  `ㄱ (0), ㄲ (1), ㄴ (2), ㄷ (3), ㄸ (4), ㄹ (5), ㅁ (6), ㅂ (7), ㅃ (8), ㅅ (9), ㅆ (10), ㅇ (11), ㅈ (12), ㅉ (13), ㅊ (14), ㅋ (15), ㅌ (16), ㅍ (17), ㅎ (18)`
- **21 Medial Vowels (중성)**:
  `ㅏ (0), ㅐ (1), ㅑ (2), ㅒ (3), ㅓ (4), ㅔ (5), ㅕ (6), ㅖ (7), ㅗ (8), ㅘ (9), ㅙ (10), ㅚ (11), ㅛ (12), ㅜ (13), ㅝ (14), ㅞ (15), ㅟ (16), ㅠ (17), ㅡ (18), ㅢ (19), ㅣ (20)`
- **28 Final Consonants (종성 / 받침)**:
  `None (0), ㄱ (1), ㄲ (2), ㄳ (3), ㄴ (4), ㄵ (5), ㄶ (6), ㄷ (7), ㄹ (8), ㄺ (9), ㄻ (10), ㄼ (11), ㄽ (12), ㄾ (13), ㄿ (14), ㅀ (15), ㅁ (16), ㅂ (17), ㅄ (18), ㅅ (19), ㅆ (20), ㅇ (21), ㅈ (22), ㅊ (23), ㅋ (24), ㅌ (25), ㅍ (26), ㅎ (27)`

---

## 2. Syllable Coda Neutralization (음절 끝소리 규칙 / 7종성법)

In word-final position or preceding an onset consonant, all 27 graphic final consonants collapse into exactly **7 phonetic stop realizations**:

| Neutralized Sound | Orthographic Codas that Neutralize | Example Orthography | Phonetic Realization |
| :--- | :--- | :--- | :--- |
| **[ㄱ]** | `ㄱ, ㄲ, ㅋ, ㄳ, ㄺ` | *박, 밖, 부엌, 몫, 닭* | `[박, 박, 부억, 목, 닥]` |
| **[ㄴ]** | `ㄴ, ㄵ, ㄶ` | *눈, 앉다, 많다* | `[눈, 안-, 만-]` |
| **[ㄷ]** | `ㄷ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ` | *곧, 옷, 있-, 낮, 꽃, 밭, 히읗* | `[곧, 옫, 읻-, 낟, 꼳, 받, 히읃]` |
| **[ㄹ]** | `ㄹ, ㄼ, ㄽ, ㄾ, ㅀ` | *달, 여덟, 외곬, 핥다, 잃다* | `[달, 여덜, 외골, 할-, 일-]` |
| **[ㅁ]** | `ㅁ, ㄻ` | *밤, 삶* | `[밤, 삼]` |
| **[ㅂ]** | `ㅂ, ㅍ, ㄿ, ㅄ` | *입, 잎, 읊다, 값* | `[입, 입, 을-, 갑]` |
| **[ㅇ]** | `ㅇ` | *강, 방* | `[강, 방]` |

---

## 3. Major Phonological Processes (음운 변동)

### 3.1 Nasalization (비음화)
When an unreleased stop coda `[ㄱ, ㄷ, ㅂ]` is immediately followed by a nasal onset `[ㄴ, ㅁ]`, the stop assimilates into its homorganic nasal:
- `[ㄱ] + [ㄴ, ㅁ] -> [ㅇ]`: *국물* $\to$ `[궁물]`, *백만* $\to$ `[뱅만]`
- `[ㄷ] + [ㄴ, ㅁ] -> [ㄴ]`: *닫는* $\to$ `[단는]`, *끝물* $\to$ `[끈물]`
- `[ㅂ] + [ㄴ, ㅁ] -> [ㅁ]`: *밥물* $\to$ `[밤물]`, *입니다* $\to$ `[임니다]`

### 3.2 Tensification / Post-Obstruent Glottalization (된소리되기)
Lax stops and affricates `[ㄱ, ㄷ, ㅂ, ㅅ, ㅈ]` become tense `[ㄲ, ㄸ, ㅃ, ㅆ, ㅉ]` after an unreleased obstruent coda:
- *학교* $\to$ `[학꾜]`, *식당* $\to$ `[식땅]`, *국밥* $\to$ `[국빱]`, *옷고름* $\to$ `[옫꼬름]`

### 3.3 Liquidization / Lateral Assimilation (유음화)
When alveolar nasal `[ㄴ]` meets alveolar liquid `[ㄹ]`, they regressively or progressively assimilate to double lateral `[ㄹㄹ]`:
- `ㄴ + ㄹ -> [ㄹㄹ]`: *신라* $\to$ `[실라]`, *난로* $\to$ `[날로]`
- `ㄹ + ㄴ -> [ㄹㄹ]`: *칼날* $\to$ `[칼랄]`, *달나라* $\to$ `[달라라]`

### 3.4 Palatalization (구개음화)
Coronal stops `[ㄷ, ㅌ]` immediately preceding the high front vowel `[이]` or semivowel `[j]` palatalize to postalveolar affricates `[ㅈ, ㅊ]`:
- *굳이* $\to$ `[구지]`
- *같이* $\to$ `[가치]`
- *해돋이* $\to$ `[해도지]`

### 3.5 Aspiration (격음화)
When lax stops `[ㄱ, ㄷ, ㅂ, ㅈ]` encounter the glottal fricative `[ㅎ]` (either preceding or following), they merge into aspirated stops:
- *축하* $\to$ `[추카]`, *좋다* $\to$ `[조타]`, *입학* $\to$ `[이팍]`, *맞히다* $\to$ `[마치다]`
