# Arabic Engine — Layer 3: Phonological & Orthographic Rules (Text/Sound Layer)

## 1. Right-to-Left (RTL) Script Architecture & Glyphs

The Arabic writing system is a right-to-left cursive abjad comprising 28 primary consonants and 3 long vowels:
- 22 letters connect in 4 contextual glyph shapes: Isolated, Initial, Medial, and Final.
- 6 letters are non-connecting to the left: **أ (Alif), د (Dāl), ذ (Dhāl), ر (Rā'), ز (Zāy), و (Wāw)**.

---

## 2. Diacritics & Vocalic Phonation (الحَرَكَاتُ)

Full diacritization (Tashkīl) explicitly vocalizes the grammatical case and stem vowels:

| Diacritic | Arabic Name | Phonetic Value | Example |
|-----------|-------------|----------------|---------|
| ـَ | Fatḥa | Short vowel /a/ | كَتَبَ (*kataba*) |
| ـِ | Kasra | Short vowel /i/ | كِتَاب (*kitāb*) |
| ـُ | Ḍamma | Short vowel /u/ | كُتُب (*kutub*) |
| ـْ | Sukūn | Zero vowel / Coda | مَكْتَب (*mak-tab*) |
| ـّ | Shadda | Gemination / Doubled consonant | عَلَّمَ (*'allama*) |
| ـً | Tanwīn Fatḥ | Indefinite accusative /-an/ | كِتَاباً (*kitāban*) |
| ـٍ | Tanwīn Kasr | Indefinite genitive /-in/ | كِتَابٍ (*kitābin*) |
| ـٌ | Tanwīn Ḍamm | Indefinite nominative /-un/ | كِتَابٌ (*kitābun*) |

---

## 3. Sun and Moon Letters (الحُرُوفُ الشَّمْسِيَّةُ والقَمَرِيَّةُ)

When the prefixal definite article **الـ** (*al-*) is prefixed to a noun, the coronal lateral /l/ assimilates to coronal consonants:

### 3.1 Sun Letters (14 Coronal Consonants — الحروف الشمسية)
The letters **ت, ث, د, ذ, ر, ز, س, ش, ص, ض, ط, ظ, ل, ن**:
- The /l/ assimilates completely to the consonant, marked by a shadda (ـّ):
  - *al-shams* $\longrightarrow$ **ash-shams** (الشَّمْسُ)
  - *al-rajul* $\longrightarrow$ **ar-rajul** (الرَّجُلُ)
  - *al-nūr* $\longrightarrow$ **an-nūr** (النُّورُ)

### 3.2 Moon Letters (14 Non-Coronal Consonants — الحروف القمرية)
The letters **ء, ب, ج, ح, خ, ع, غ, ف, ق, ك, م, هـ, و, ي**:
- The /l/ remains fully articulated with a sukūn:
  - *al-qamar* $\longrightarrow$ **al-qamar** (القَمَرُ)
  - *al-kitāb* $\longrightarrow$ **al-kitāb** (الكِتَابُ)
  - *al-bāb* $\longrightarrow$ **al-bāb** (البَابُ)

---

## 4. Hamza Orthography Rules (قَوَاعِدُ رَسْمِ الهَمْزَةِ)

The glottal stop /ʔ/ (Hamza) is governed by positional and vocalic precedence:

### 4.1 Hamzat al-Waṣl vs. Hamzat al-Qaṭ'
- **Hamzat al-Waṣl (همزة الوصل)**: Silent in connected speech; occurs in the definite article (*al-*), Form VII, VIII, IX, X imperatives and perfects, and select nominals (*ism, ibn, ibna*).
- **Hamzat al-Qaṭ' (همزة القطع)**: Obligatorily articulated; written as **أ** or **إ**; occurs in Form IV verbs, broken plurals (*'aqlām*), and particles (*'in, 'an, 'ilā*).

### 4.2 Medial Hamza Seat Hierarchy
The chair/seat of medial hamza is dictated by relative vowel strength:
$$\text{Kasra (/i/)} > \text{Ḍamma (/u/)} > \text{Fatḥa (/a/)} > \text{Sukūn (/0/)}$$
- If either the hamza or preceding vowel is *kasra*, it sits on a Nabrah (ـئـ / ئ).
- Else if either is *ḍamma*, it sits on a Wāw (ؤ).
- Else if either is *fatḥa*, it sits on an Alif (أ).
- After long vowels, it sits on the line (ء).

---

## 5. Punctuation & Typography

Arabic utilizes standardized inverted glyphs matching script flow:
- Arabic Comma: `،` (U+060C)
- Arabic Semicolon: `؛` (U+061B)
- Arabic Question Mark: `؟` (U+061F)
- Tatweel (Kashida): `ـ` (U+0640) for typographic justification and legibility.
