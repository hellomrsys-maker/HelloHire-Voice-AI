# Layer 3: Phonology, Orthography & Substantive Capitalization (German Language Engine)

## 1. Orthographic Invariants: The 30-Letter Standard & Substantiv-Großschreibung

Standard German (*Hochdeutsch*) orthography features several unique systemic requirements that directly impact computational tokenization and parsing:

### 1.1 The 30-Letter Alphabet
German supplements the standard 26 Latin letters with four distinct characters:
- **Umlauts**: `ä / Ä` [ɛː/ɛ], `ö / Ö` [øː/œ], `ü / Ü` [yː/ʏ]
- **Eszett (Scharfes S)**: `ß / ẞ` [s]
  - Used after long vowels and diphthongs (*Straße, weiß, fließen, groß*).
  - Contrasted with `ss` which strictly follows short vowels (*Schloss, Fluss, dass, müssen*).
  - *Swiss German Rule*: In Switzerland and Liechtenstein, `ß` is abolished and replaced systematically with `ss` (*Strasse, weiss*).

### 1.2 Mandatory Noun Capitalization (Substantiv-Großschreibung)
German is the only major world language where **all nouns** (common, abstract, collective, and proper) are capitalized:
- *der Mann* (man), *die Freiheit* (freedom), *das Haus* (house).
- **Nominalizations**: Any part of speech converted into a noun takes obligatory capitalization and neuter gender:
  - Verbs: *das Lernen* (learning), *das Essen* (eating/food), *beim Schwimmen* (while swimming).
  - Adjectives: *das Gute* (the good), *etwas Neues* (something new), *im Allgemeinen* (in general).

---

## 2. Phonological Alternations & Allophonic Rules

### 2.1 Auslautverhärtung (Final Obstruent Devoicing)
In German syllable codas, underlying voiced stops and fricatives (/b, d, g, v, z/) obligatorily neutralize into their voiceless counterparts [p, t, k, f, s]:

| Underlying Phoneme | Syllable-Final Realization | Example Form (Coda) | Inflected Form (Onset - Voiced) |
| :--- | :--- | :--- | :--- |
| **/d/** | **[t]** | *Hund* [hʊnt] | *Hunde* [ˈhʊndə] |
| **/b/** | **[p]** | *gelb* [ɡɛlp] | *gelbe* [ˈɡɛlbə] |
| **/g/** | **[k]** | *Tag* [taːk] | *Tage* [ˈtaːɡə] |
| **/v/** | **[f]** | *aktiv* [akˈtiːf] | *aktive* [akˈtiːvə] |
| **/z/** | **[s]** | *Gras* [ɡʁaːs] | *Gräser* [ˈɡʁɛːzɐ] |

### 2.2 The Fricative Allophony: Ich-Laut [ç] vs Ach-Laut [x]
The grapheme `<ch>` surfaces as two complementary allophones determined strictly by the phonological environment:
1. **Ach-Laut [x] (Velar Fricative)**:
   - Follows back vowels (/a, o, u, aʊ/): *Bach* [bax], *Loch* [lɔx], *Buch* [buːx], *Bauch* [baʊx].
2. **Ich-Laut [ç] (Palatal Fricative)**:
   - Follows front vowels (/e, i, ä, ö, ü, aɪ, ɔɪ/): *ich* [ʔɪç], *echt* [ʔɛçt], *Bücher* [ˈbyːçɐ], *leicht* [laɪçt].
   - Follows sonorants (/l, n, r/): *Milch* [mɪlç], *Mönch* [mœnç], *durch* [dʊʁç].
   - Diminutive suffix *-chen*: *Mädchen* [ˈmɛːtçn̩], *Frauchen* [ˈfʁaʊçn̩] (even after back vowels).

### 2.3 The Glottal Stop (Knacklaut [ʔ])
In standard German, every stressed word-initial or morpheme-initial vowel is preceded by an unwritten glottal stop [ʔ], preventing resyllabification and liaison:
- *beachten* $\longrightarrow$ [bəˈʔaxtn̩] (not \*[bəˈnaxtn̩])
- *der Apfel* $\longrightarrow$ [deːɐ̯ ˈʔapfl̩] (not \*[deːˈʁapfl̩])
