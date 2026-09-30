# Layer 3: Phonological & Orthographic (Text-Sound Layer) — Indonesian Language Engine

## 1. Phonemic Inventory
Standard Indonesian phonology features 6 vowels, 3 diphthongs, and 22 consonants.

### 1.1 Vowel System
- High: `/i/` (*pilih*), `/u/` (*tutup*)
- Mid: `/e/` (front mid tense /e/ vs lax /ɛ/: *bebek*), `/ə/` (schwa *pepet*: *empat, besar*)
- Mid Back: `/o/` (*toko, kota*)
- Low: `/a/` (*mata, bawa*)
*(Orthographic note: In standard Indonesian orthography, both /e/ and /ə/ are written with the single grapheme `e`, though dictionaries distinguish them with `é` for /e/).*

### 1.2 Consonant System & Grapheme Correspondences
- Bilabial: `/p, b, m, w/`
- Alveolar: `/t, d, s, z, n, l, r/` (alveolar trill `/r/` is strongly rolled)
- Postalveolar / Palatal:
  - Voiceless affricate `/tʃ/` (written `c`: *cantik, cium*).
  - Voiced affricate `/dʒ/` (written `j`: *jalan, jajan*).
  - Palatal nasal `/ɲ/` (written `ny`: *nyanyi, banyak*).
  - Palatal approximant `/j/` (written `y`: *saya, yakin*).
  - Postalveolar fricative `/ʃ/` (written `sy`: *syarat, masyarakat*).
- Velar: `/k, ɡ, ŋ/` (`ng`: *dengan, angin*), `/x/` (written `kh`: *khusus, akhir*).
- Glottal: `/h/` (*hari*), `/ʔ/` (word-final `k` pronounced as glottal stop: *bapak* `[ba.paʔ]`, *tidak* `[ti.daʔ]`).

## 2. Syllable Structure & Stress
- Canonical syllable structure: `(C)V(C)`: *a-nak, ban-tu, sang-at*.
- Penultimate stress: Lexical stress falls regularly on the **penultimate syllable** (*ru-MAH*, *be-SAR*), unless the penult vowel is a schwa `/ə/`, in which case stress shifts to the **ultimate syllable** (*be-SAR* `[bə'sar]`, *te-PANG* `[tə'paŋ]`).

## 3. Orthographic Conventions (Ejaan Bahasa Indonesia yang Disempurnakan - EYD)
- Historical spelling reforms:
  - 1901 Van Ophuijsen (`oe` for `/u/`, `dj` for `/dʒ/`, `tj` for `/tʃ/`).
  - 1947 Soewandi (`u` replaced `oe`).
  - 1972 Ejaan yang Disempurnakan / EYD (`c` replaced `tj`, `j` replaced `dj`, `y` replaced `j`, `ny` replaced `nj`, `sy` replaced `sj`, `kh` replaced `ch`).
- Hyphenation rule: Reduplicated words are **strictly written with hyphens** (*buku-buku, anak-anak, bersama-sama*), never numerals (*buku2* is informal/slang).
