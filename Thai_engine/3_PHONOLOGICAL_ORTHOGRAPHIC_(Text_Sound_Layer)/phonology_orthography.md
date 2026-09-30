# Phonological & Orthographic Specification for Thai (Sound & Text Layer)
## Sovereign Engine: `Thai_engine` | 5-Tone Scriptio Continua

### 1. The 5 Phonemic Tones
Thai distinguishes five contrastive pitch contours:

| Tone Name | Thai Name | Tone Contour | Pitch Value | IPA | Example | Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mid** | สามัญ (*Sǎamǎan*) | Level | [33] | /˧/ | *กา* (*kaa*) | "crow" |
| **Low** | เอก (*Èek*) | Low falling | [21] | /˨˩/ | *ก่า* (*kàa*) | "species of lizard" |
| **Falling** | โท (*Thoo*) | High falling | [51] | /˥˩/ | *ก้า* (*kâa*) | "brave" |
| **High** | ตรี (*Trii*) | High rising/level | [45] | /˦˥/ | *ก๊า* (*káa*) | "(onomatopoeia)" |
| **Rising** | จัตวา (*Càttawaa*) | Dipping rising | [24] | /˩˦/ | *ก๋า* (*kǎa*) | "smart / bold" |

---

### 2. The 3 Consonant Classes (44 Letters)
Consonants dictate tone generation when combined with vowels and tone marks:

#### A. Middle Class (อักษรกลาง - 9 letters)
*ก, จ, ด, ต, ฎ, ฏ, บ, ป, อ*
- Capable of carrying all 4 tone marks and producing all 5 tones.

#### B. High Class (อักษรสูง - 11 letters)
*ข, ฃ, ฉ, ฐ, ถ, ผ, ฝ, ศ, ษ, ส, ห*
- Inherent tone is **Rising** (in live syllables without tone mark).

#### C. Low Class (อักษรต่ำ - 24 letters)
1. **Paired Low Consonants (อักษรต่ำคู่ - 14 letters)**:
   *ค, ฅ, ฆ, ช, ซ, ฌ, ฑ, ฒ, ท, ธ, พ, ฟ, ภ, ฮ* (Aspirated / fricatives pairing with high class).
2. **Single / Sonorant Low Consonants (อักษรต่ำเดี่ยว - 10 letters)**:
   *ง, ญ, ณ, น, ม, ย, ร, ล, ว, ฬ* (Nasals, liquids, glides). Inherent tone is **Mid**.

---

### 3. Tone Calculation Matrix (The 5-Tone Rule Engine)

| Consonant Class | Syllable Type | No Tone Mark | ไม้เอก ( ่ ) | ไม้โท ( ้ ) | ไม้ตรี ( ๊ ) | ไม้จัตวา ( ๋ ) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Middle** | Live (คำเป็น) | **Mid** | **Low** | **Falling** | **High** | **Rising** |
| **Middle** | Dead (คำตาย) | **Low** | — | **Falling** | — | — |
| **High** | Live (คำเป็น) | **Rising** | **Low** | **Falling** | — | — |
| **High** | Dead (คำตาย) | **Low** | — | — | — | — |
| **Low** | Live (คำเป็น) | **Mid** | **Falling** | **High** | — | — |
| **Low** | Dead (Short Vowel) | **High** | — | **Falling** | — | — |
| **Low** | Dead (Long Vowel) | **Falling** | — | — | — | — |

*Live Syllables (คำเป็น)*: End with a long vowel or sonorant coda (-m, -n, -ng, -y, -w).
*Dead Syllables (คำตาย)*: End with a short vowel without coda, or stop codas (-p, -t, -k).

---

### 4. Orthographic Non-Linearity & Scriptio Continua
Thai is written in continuous *scriptio continua* without word spaces. Vowels surround consonants in 4 quadrants:
1. **Preposed (หน้า)**: เ, แ, โ, ใ, ไ (written *before* the consonant pronounced first, e.g. *ไป* *pay*).
2. **Postposed (หลัง)**: ะ, า, ๅ.
3. **Superscript (บน)**: ิ, ี, ึ, ื, ั, ็, ์ (silent letter marker *Thanthakhat*), and tone marks.
4. **Subscript (ล่าง)**: ุ, ู.
