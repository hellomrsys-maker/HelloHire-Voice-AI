# Layer 3: Phonological & Orthographic Layer - Bengali Engine (বাংলা)

## 1. Bengali Script (বাংলা লিপি - Bangla Lipi)
Bengali is written in the Eastern Nagari (Bangla-Assamese) abugida, derived from Brahmi script via the Siddham/Gaudi script.
- **Inherent Vowel**: Every consonant glyph represents a consonant plus the inherent vowel /ɔ/ (অ) unless modified by a vowel diacritic (*kar* / কার) or suppressed by a virama / hasanta (*্* / হসন্ত).
- **Vowel Shift of Inherent Vowel**: The inherent vowel /ɔ/ frequently shifts phonetically to rounded /o/ word-finally or before /i/ and /u/ (e.g., *মন* is pronounced [mon], *মত* [mɔto] or [mɔt]).

---

## 2. Vowel Inventory & Nasalization
Bengali features 7 oral vowels and 7 phonemically corresponding nasal vowels:

| Height / Backness | Front Oral | Front Nasal | Central Oral | Central Nasal | Back Oral | Back Nasal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **High** | /i/ (ই, ি) | /ĩ/ (ইঁ, িঁ) | — | — | /u/ (উ, ু) | /ũ/ (উঁ, ুঁ) |
| **High-Mid** | /e/ (এ, ে) | /ẽ/ (এঁ, েঁ) | — | — | /o/ (ও, ো) | /õ/ (ওঁ, োঁ) |
| **Low-Mid** | /æ/ (অ্যা, ্যা) | /æ̃/ (অ্যাঁ) | — | — | /ɔ/ (অ) | /ɔ̃/ (অঁ) |
| **Low** | — | — | /a/ (আ, া) | /ã/ (আঁ, াঁ) | — | — |

- **Chandrabindu (ঁ)**: Phonemic vowel nasalization marker (e.g., *চাঁদ* `chãd` - moon, *তাঁর* `tãr` - his/her honorific).
- **Anusvara (ং)**: Velar nasal consonant coda [ŋ] (e.g., *রং* `rong` - color, *বাংলা* `bangla`).
- **Visarga (ঃ)**: Gemination of subsequent consonant or word-final voiceless aspiration / glottalization (e.g., *দুঃখ* `dukkho` - sorrow).

---

## 3. Consonantal System & Retroflexion
Bengali stop consonants exhibit a 4-way contrast (Voiceless Unaspirated, Voiceless Aspirated, Voiced Unaspirated, Voiced Aspirated) across 5 places of articulation:

| Articulation | Unvoiced Unaspirated | Unvoiced Aspirated | Voiced Unaspirated | Voiced Aspirated | Nasal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Velar** | ক [k] | খ [kʰ] | গ [ɡ] | ঘ [ɡʱ] | ঙ [ŋ] |
| **Palatal / Palato-alveolar** | চ [tɕ] | ছ [tɕʰ] | জ [dʑ] | ঝ [dʑʱ] | ঞ [ɲ] |
| **Retroflex** | ট [ʈ] | ঠ [ʈʰ] | ড [ɖ] | ঢ [ɖʱ] | ণ [n] |
| **Dental** | ত [t̪] | থ [t̪ʰ] | দ [d̪] | ধ [d̪ʱ] | ন [n] |
| **Labial** | প [p] | ফ [pʰ/ɸ] | ব [b] | ভ [bʱ/β] | ম [m] |

- **Flaps**: ড় [ɽ] (retroflex flap) and ঢ় [ɽʱ] (aspirated retroflex flap).
- **Sibilant Neutralization**: In standard Bengali, all three historical sibilants (*শ* palatal, *ষ* retroflex, *স* dental) have largely merged into the voiceless postalveolar sibilant [ʃ], except when followed by dental coronals (/t/, /t̪ʰ/, /n/, /l/, /r/) where they revert to dental [s].

---

## 4. Conjunct Consonants (*যুক্তাক্ষর* - Juktakkhor)
When two or more consonants appear without an intervening vowel, they form complex conjunct ligatures:
- **ক্ষ** = ক্ + ষ (`k + ṣ = kkʰo` in standard Bengali: *পরীক্ষা* `porikkha`).
- **জ্ঞ** = জ্ + ঞ (`j + ñ = ggõ` in standard Bengali: *জ্ঞান* `ggãn`).
- **ঞ্চ** = ঞ্ + চ (`ñ + c = ñc`: *পঞ্চ* `poncho`).
- **ন্ত** = ন্ + ত (`n + t = nt`: *শান্ত* `shanto`).
- **ত্র** = ত্ + র (`t + r = tr`: *ছাত্র* `chatro`).

---

## 5. Punctuation & Boundary Markings
- **Bengali Dā̃ṛi / Dāri (।)**: Unicode `U+0964` serves as the primary declarative terminal full stop.
- **Double Dā̃ṛi (॥)**: Unicode `U+0965` marks paragraph or poetic stanza termination.
- **Western Punctuation Marks**: Comma (`,`), semicolon (`;`), quotation marks (`"..."`), and question mark (`?`) are standard in modern text.
