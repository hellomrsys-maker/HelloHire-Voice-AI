# German Engine — Layer 6: Data Requirements & Lexicon Manifest

## 1. Corpus Sources & Treebanks

The German Engine utilizes standardized linguistic corpora and dependency treebanks:

1. **Universal Dependencies German Treebanks**:
   - **UD German-GSD**: 15,815 sentences (292,000 tokens) sourced from news, Wikipedia, and consumer reviews. Annotated with UPOS, XPOS (STTS - Stuttgart-Tübingen-TagSet), and morphological features.
   - **UD German-HDT (Hamburg Dependency Treebank)**: ~200,000 sentences (3.6 million tokens), the largest manually annotated German dependency treebank, providing rich hierarchical syntax.
   - **UD German-LIT**: Specialized literary texts for complex literary and historical syntax.
2. **Tiger & TüBa-D/Z Treebanks**:
   - **Tiger Corpus**: 50,474 newspaper sentences from *Frankfurter Rundschau*, using Topological Field (Satzklammer) annotations (Vorfeld, C-Feld, Mittelfeld, V-End, Nachfeld).
   - **TüBa-D/Z**: 95,000 sentences from *die tageszeitung (taz)* annotated with topological fields, constituent structure, and coreference.

---

## 2. Morphological Lexicons & Stemmers

1. **Morphy Lexicon (Wolfgang Lezius)**:
   - Comprehensive dictionary of ~320,000 inflected German word forms mapping to canonical stems, POS tags, and morphological features (Case, Number, Gender, Tense, Mood, Person).
2. **SMOR (Stuttgart Morphological Model)**:
   - Finite-state morphology engine covering German productive compounding, prefixation, suffixation, and Fugenlaute.
3. **CELEX German Morphological Database**:
   - 51,728 lemmas and 365,530 inflected word forms with syllabification, phonemic transcriptions (SAMPA), and morphological constituency.

---

## 3. Verb Valency Lexicons (Valenzlexika)

German verbs govern strict argument structures including grammatical cases and prepositional complements:

### 3.1 E-VALBU (Elektronisches Valenzwörterbuch deutscher Verben, IDS Mannheim)
Provides quantitative and qualitative valency frames for >3,000 core verbs:

| Verb Lemma | Valency Frame | Required Complements | Example |
|------------|---------------|----------------------|---------|
| *geben*    | Subj(Nom) + Obj(Dat) + Obj(Akk) | Trivalent | *Er gibt dem Kind einen Apfel.* |
| *helfen*   | Subj(Nom) + Obj(Dat) | Bivalent (Dative) | *Die Ärztin hilft dem Patienten.* |
| *warten*   | Subj(Nom) + PrepObj(*auf* + Akk) | Prepositional | *Wir warten auf den Zug.* |
| *denken*   | Subj(Nom) + PrepObj(*an* + Akk) | Prepositional | *Ich denke an die Reise.* |
| *gehören*  | Subj(Nom) + Obj(Dat) / PrepObj(*zu* + Dat) | Dative / Prepositional | *Das Buch gehört mir.* / *Das gehört zur Pflicht.* |
| *gedenken* | Subj(Nom) + Obj(Gen) | Bivalent (Genitive) | *Wir gedenken der Opfer.* |

---

## 4. Morphological Rules & Tables

### 4.1 Strong Verb Ablaut Series (Stammformen)
Standard German strong verbs fall into 7 traditional Ablaut classes:
1. **Class 1 (ei — i/ie — i/ie)**: *bleiben — blieb — geblieben*; *reiten — ritt — geritten*
2. **Class 2 (ie/eu/au — o — o)**: *fliegen — flog — geflogen*; *ziehen — zog — gezogen*
3. **Class 3 (i — a — u/o)**:
   - 3a (i + nasal + consonant): *singen — sang — gesungen*; *finden — fand — gefunden*
   - 3b (i + liquid + consonant): *helfen — half — geholfen*; *sterben — starb — gestorben*
4. **Class 4 (e — a — o)**: *nehmen — nahm — genommen*; *brechen — brach — gebrochen*
5. **Class 5 (e — a — e)**: *geben — gab — gegeben*; *sehen — sah — gesehen*
6. **Class 6 (a — u — a)**: *fahren — fuhr — gefahren*; *schlagen — schlug — geschlagen*
7. **Class 7 (reduplicating: a/o/u/ei/au — ie — a/o/u/ei/au)**: *fallen — fiel — gefallen*; *halten — hielt — gehalten*; *laufen — lief — gelaufen*

### 4.2 Compound Infixes (Fugenlaute)
- **-s- / -es-**: *Arbeit-s-zimmer, Wirtschaft-s-krise, Jahr-es-zeit*
- **-en- / -n-**: *Ketten-reaktion, Straße-n-bahn, Student-en-wohnheim*
- **-er-**: *Bilder-rahmen, Kinder-garten*
- **Zero-Fuge**: *Haustür, Autoreifen, Schreibtisch*

---

## 5. Orthographic & Spelling Norms
- **Amtliche Rechtschreibung 2006 / 2024 (Rat für deutsche Rechtschreibung)**:
  - Strict capitalization of substantive nouns (*das Buch, die Freiheit, das Gute*).
  - Distinction between *ss* (short vowel: *dass, Schloss, Fluss*) and *ß* (long vowel / diphthong: *Straße, groß, weiß*).
  - Capitalized formal address (*Sie, Ihnen, Ihr*).
  - Swiss German variant: universal replacement of *ß* by *ss*.
