# Layer 3: Phonological & Orthographic (Text-Sound Layer) — Italian Language Engine

## 1. Phoneme Inventory & Allophonic Rules
Italian standard phonology (based on Fiorentino colto) consists of 7 vowel phonemes and 23 consonant phonemes.

### 1.1 Heptavocalic Vowel System (Tonic Vowels)
Under primary lexical stress, Italian features a 7-vowel contrast:
- High: `/i/` (*vino*), `/u/` (*luna*)
- Higher-Mid (Closed): `/e/` (*pesca* = fishing), `/o/` (*botte* = barrel)
- Lower-Mid (Open): `/ɛ/` (*pèsca* = peach), `/ɔ/` (*bòtte* = blows/hits)
- Low: `/a/` (*pane*)
*(In unstressed syllables, the contrast between open and closed mid vowels is neutralized into /e/ and /o/).*

### 1.2 Palatal Affricates & Velar Alternations
- **Grapheme `c`**:
  - Before `a, o, u`: Velar stop `/k/` (*cane, collo, cura*).
  - Before `e, i`: Voiceless postalveolar affricate `/tʃ/` (*cena, cibo*).
  - Digraph `ch` before `e, i`: Preserves velar `/k/` (*chiave, amiche*).
  - Trigraph `ci` before `a, o, u`: Diacritic `i` indicating `/tʃ/` (*ciao, ciotola*).
- **Grapheme `g`**:
  - Before `a, o, u`: Voiced velar stop `/ɡ/` (*gatto, gola, gusto*).
  - Before `e, i`: Voiced postalveolar affricate `/dʒ/` (*gente, giro*).
  - Digraph `gh` before `e, i`: Preserves velar `/ɡ/` (*ghiro, streghe*).
  - Trigraph `gi` before `a, o, u`: Diacritic `i` indicating `/dʒ/` (*giorno, giallo*).

### 1.3 Intrinsic Geminates (Consonanti Intrinsecamente Doppie)
Five consonants are always pronounced geminate (long) intervocalically:
1. Palatal nasal `/ɲ/` (digraph `gn`: *bagno, sogno*).
2. Palatal lateral `/ʎ/` (trigraph `gli`: *figlio, aglio*).
3. Voiceless postalveolar fricative `/ʃ/` (digraph `sc` before *e, i*: *pesce, sci*).
4. Voiceless alveolar affricate `/ts/` (*piazza, stazione*).
5. Voiced alveolar affricate `/dz/` (*mezzo, zero*).

## 2. Syntactic Doubling (Raddoppiamento Fonosintattico - RF)
In standard Italian, the initial consonant of a word undergoes phonetic lengthening when preceded by:
- All stressed monosyllables (*è, ha, va, dà, fa, già, più, può, qui, tra, fra*).
- Strong polysyllables accented on the final syllable (*città, caffè, virtù, perché*).
- Specific unstressed function words (*a, da, e, ma, o, se, che*).
*Examples*: *a casa* $\to$ `[akˈkaːsa]`, *e poi* $\to$ `[epˈpɔi]`, *è vero* $\to$ `[ɛvˈveːro]`.

## 3. Elision (Elisione) & Truncation (Troncamento)
- **Elision**: Deletion of final unstressed vowel before a word starting with a vowel, marked with an apostrophe:
  - *lo amico* $\to$ *l'amico*, *la amica* $\to$ *l'amica*, *ci è* $\to$ *c'è*, *di accordo* $\to$ *d'accordo*, *una amica* $\to$ *un'amica*.
- **Truncation**: Deletion of a final unstressed vowel or syllable before consonant or vowel, without an apostrophe:
  - *bello ragazzo* $\to$ *bel ragazzo*, *buono giorno* $\to$ *buon giorno / buongiorno*, *dottore Rossi* $\to$ *dottor Rossi*, *uno amico* $\to$ *un amico* (masculine never takes apostrophe).
