# Layer 3: Phonology, Orthography & Harmonic Systems (Turkish Language Engine)

## 1. The Turkish Orthographic Standard (Harf İnkılabı, 1928)

Modern Turkish employs a 29-letter Latin-based phonetic alphabet with nearly 1:1 grapheme-to-phoneme correspondence:

```
A, B, C, Ç, D, E, F, G, Ğ, H, I, İ, J, K, L, M, N, O, Ö, P, R, S, Ş, T, U, Ü, V, Y, Z
```

### 1.1 The Dotted and Dotless I Distinction
A critical orthographic and computational requirement is the strict distinction between dotted and dotless I in both upper and lower case:
- **Dotted Front High Unrounded**: `i` (lowercase) $\longleftrightarrow$ `İ` (uppercase) [i]
- **Dotless Back High Unrounded**: `ı` (lowercase) $\longleftrightarrow$ `I` (uppercase) [ɯ]
- *Systemic Hazard*: Standard ASCII case folding (`"i".upper() -> "I"`) introduces catastrophic orthographic errors in Turkish (e.g. *diyar* vs *dıyâr*). All string operations must be locale-aware.

### 1.2 The Soft G (Yumuşak G: Ğ, ğ)
- Never appears in word-initial position.
- In modern standard Istanbul Turkish, it is non-plosive:
  - After back vowels (*a, ı, o, u*): lengthens the preceding vowel (*dağ* $\to$ [daː], *ağaç* $\to$ [aːtʃ]).
  - After front vowels (*e, i, ö, ü*): realized as a subtle palatal glide [j] or vowel lengthening (*değil* $\to$ [dejiɫ] / [diːl]).

---

## 2. Vowel Harmony (Ünlü Uyumu)

Turkish vowel phonology is governed by two interlocking tiers of vocalic assimilation:

```
                    FRONT (İnce)                BACK (Kalın)
              Unrounded       Rounded     Unrounded       Rounded
HIGH (Dar)       i              ü            ı              u
LOW  (Geniş)     e              ö            a              o
```

### 2.1 Two-Fold Vowel Harmony (A-Tipi / 2-Way)
Governs suffixes containing low/broad vowels:
- If last stem vowel is **Front** (*e, i, ö, ü*) $\longrightarrow$ suffix takes **-e-**
- If last stem vowel is **Back** (*a, ı, o, u*) $\longrightarrow$ suffix takes **-a-**

*Major Morphemes Governed*:
- Plural: *-ler / -lar* (*ev-ler*, *kitap-lar*)
- Dative: *-e / -a* (*ev-e*, *okul-a*)
- Locative: *-de / -da / -te / -ta* (*ev-de*, *okul-da*)
- Ablative: *-den / -dan / -ten / -tan* (*ev-den*, *okul-dan*)

### 2.2 Four-Fold Vowel Harmony (I-Tipi / 4-Way)
Governs suffixes containing high/narrow vowels, assimilating both backness and lip-rounding:

| Last Stem Vowel | Harmonic Suffix Vowel | Example Morpheme (Accusative *-i*) | Example Morpheme (Past *-di*) |
| :--- | :--- | :--- | :--- |
| **e, i** (Front Unrounded) | **-i-** | *ev-i* (house), *dil-i* (tongue) | *gel-di* (came) |
| **a, ı** (Back Unrounded)  | **-ı-** | *kız-ı* (girl), *kapı-y-ı* (door) | *bak-tı* (looked) |
| **ö, ü** (Front Rounded)   | **-ü-** | *göz-ü* (eye), *gül-ü* (rose)     | *gör-dü* (saw) |
| **o, u** (Back Rounded)    | **-u-** | *yol-u* (road), *kol-u* (arm)     | *bul-du* (found) |

*Major Morphemes Governed*:
- Accusative: *-i / -ı / -ü / -u*
- Genitive: *-(n)in / -(n)ın / -(n)ün / -(n)un*
- Past Tense: *-di / -dı / -dü / -du*
- Evidential: *-miş / -mış / -müş / -muş*
- 1st & 2nd Person Possessives: *-im / -in / -imiz / -iniz*

---

## 3. Consonant Alternations (Ünsüz Değişimleri)

### 3.1 Consonant Assimilation (Ünsüz Benzeşmesi / Sertleşme)
When a suffix beginning with a voiced dental/alveolar plosive or affricate (*d, c*) attaches to a stem ending in a voiceless consonant (`f, s, t, k, ç, ş, h, p` - mnemonic *Fıstıkçı Şahap*), the suffix consonant obligatorily devoices:
- $d \longrightarrow t$: *kitap* + *-da* $\longrightarrow$ *kitapta* (not \**kitapda*)
- $d \longrightarrow t$: *sınıf* + *-dan* $\longrightarrow$ *sınıftan* (not \**sınıfdan*)
- $c \longrightarrow ç$: *Türk* + *-ce* $\longrightarrow$ *Türkçe* (not \**Türkce*)

### 3.2 Consonant Softening / Lenition (Ünsüz Yumuşaması)
When a vowel-initial suffix attaches to a polysyllabic stem ending in voiceless stops `p, ç, t, k`, the final stop undergoes intervocalic voicing and lenition:
- $p \longrightarrow b$: *kitap* + *-ı* $\longrightarrow$ *kitabı*
- $ç \longrightarrow c$: *ağaç* + *-a* $\longrightarrow$ *ağaca*
- $t \longrightarrow d$: *kanat* + *-ı* $\longrightarrow$ *kanadı*
- $k \longrightarrow ğ$: *çocuk* + *-u* $\longrightarrow$ *çocuğu*; *renk* + *-i* $\longrightarrow$ *rengi* (nasal assimilation to $g$)
