# Persian Phonology & Orthography Specifications (Text/Sound Layer)

## 1. Perso-Arabic Alphabet & Persian Specific Letters
Persian is written right-to-left (RTL) using an extended Arabic script containing 32 letters. The four letters added for Persian phonemes not present in Arabic are:
1. **پ** (*pe*) — /p/ (e.g., *pedar* پدر)
2. **چ** (*che*) — /tʃ/ (e.g., *cheshm* چشم)
3. **ژ** (*zhe*) — /ʒ/ (e.g., *zhende* ژنده, *muzh* مژه)
4. **گ** (*gāf*) — /ɡ/ (e.g., *garm* گرم)

## 2. Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله)
The Zero-Width Non-Joiner (Unicode `U+200C`, UTF-8 `\xE2\x80\x8C`) is a mandatory structural element of Persian digital orthography:
- It prevents unwanted character ligatures across morphological morpheme boundaries while keeping word tokens cohesive:
  - Prefix *mi-*: `می` + ZWNJ + `خورم` $\to$ `می‌خورم` (CORRECT) vs `میخورم` (disfavored) vs `می خورم` (incorrectly broken across space).
  - Plural *-hā*: `کتاب` + ZWNJ + `ها` $\to$ `کتاب‌ها` (CORRECT).
  - Compound nouns: `دست` + ZWNJ + `نویس` $\to$ `دست‌نویس` (manuscript).

## 3. Vowel Inventory
Contemporary Standard Tehrani Persian has 6 monophthong vowels and 2 diphthongs:
- **Short Vowels** (usually unwritten in standard orthography, optional diacritics):
  - /æ/ (*fathe* / زبر): *dar* (در)
  - /e/ (*kasre* / زیر): *del* (دل)
  - /o/ (*zamme* / پیش): *gol* (گل)
- **Long Vowels** (written with alif, ye, vāv):
  - /ɒː/ (آ / ا): *āb* (آب)
  - /iː/ (ی): *tir* (تیر)
  - /uː/ (و): *nur* (نور)
- **Diphthongs**: /ow/ (*now* نو), /ej/ (*pey* پی).

## 4. Stress Accent Patterns
1. **Nouns, Adjectives, Prepositions, Infinitives**: Stress is strictly on the **final syllable**:
   - *ketā́b*, *bozórg*, *dāneshgā́h*, *raftán*.
2. **Affixes**:
   - Plural suffixes *-hā*, *-ān* attract stress: *ketāb-hā́*.
   - Ezafe enclitic *-e* and direct object *rā* are **unstressed (atonic)**: *ketā́b-e bozorg*, *ketā́b rā*.
   - Personal endings are unstressed in present verbs: *mí-khor-am*.
3. **Verbal Prefixes**:
   - Durative *mí-* and subjunctive *bé-* strongly attract primary stress:
     - *mí-ravam* (I go), *bé-rav!* (Go!).
   - Negative prefix *ná-* / *né-* attracts primary sentence stress: *né-miravam* (I am not going).

## 5. Punctuation Rules
- Persian question mark: **؟** (`U+061F`)
- Persian comma: **،** (`U+060C`)
- Persian semicolon: **؛** (`U+061B`)
- Quotation marks: French guillemets **« ... »** (`U+00AB`, `U+00BB`).
