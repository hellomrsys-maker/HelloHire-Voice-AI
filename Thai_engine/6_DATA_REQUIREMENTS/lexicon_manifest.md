# Data Requirements & Lexicon Manifest for Thai (Corpus Layer)
## Sovereign Engine: `Thai_engine` | Lexical Resources

### 1. Benchmark Corpora & Lexicons

1. **Royal Institute Dictionary (RID / พจนานุกรม ฉบับราชบัณฑิตยสถาน)**:
   - Gold standard lexicon defining orthography, syllable boundaries, word classes, and royal terminology for over 43,000 official lemmas.
2. **Universal Dependencies (UD) Thai-PUD**:
   - Syntactic dependency treebank validating isolating SVO structures, serial verb chains, and classifier dependencies.
3. **LST20 / BEST Corpus (NECTEC)**:
   - Multi-million word segmented Thai benchmark providing statistical transition matrices for scriptio continua tokenization and named entity recognition.
4. **PyThaiNLP / TCC (Thai Character Clusters)**:
   - Inseparable grapheme cluster database ensuring zero split of superscript/subscript vowels and tone marks from base consonants.

---

### 2. Unicode Specification for Thai
- **Unicode Block**: `U+0E00` – `U+0E7F`
  - Consonants: `U+0E01` (ก) – `U+0E2E` (ฮ)
  - Vowel Signs: `U+0E30` (ะ), `U+0E31` (ั), `U+0E32` (า), `U+0E34` – `U+0E39`, `U+0E40` (เ) – `U+0E44` (ไ)
  - Tone Marks: `U+0E48` ( ่ ), `U+0E49` ( ้ ), `U+0E4A` ( ๊ ), `U+0E4B` ( ๋ )
  - Diacritics: `U+0E4C` (Thanthakhat / Karan ์), `U+0E47` (Maitaikhu ็)
  - Symbols: `U+0E46` (Maiyamok ๆ), `U+0E50` – `U+0E59` (Thai Numerals ๐–๙)
