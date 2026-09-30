# Layer 2: Morphological Analysis (Word Layer) — Spanish Engine

## 1. Verbal Inflection System (14 Conjugated Tenses)
Spanish verbs inflect fusively across Person (1, 2, 3), Number (Singular, Plural), Tense (Present, Past, Future), Aspect (Imperfective, Perfective), and Mood (Indicative, Subjunctive, Imperative).

### 1.1 The Three Conjugation Classes
- **1st Conjugation (`-ar`)**: *Cantar*, *hablar*, *estudiar* (Theme vowel `/a/`).
- **2nd Conjugation (`-er`)**: *Comer*, *beber*, *temer* (Theme vowel `/e/`).
- **3rd Conjugation (`-ir`)**: *Vivir*, *partir*, *abrir* (Theme vowel `/i/`).

### 1.2 Full Tense Inventory (14 Tenses)
| Mood | Simple Tense | Compound Tense (*Haber* + Participio) |
| :--- | :--- | :--- |
| **Indicativo** | **Presente**: *hablo* | **Pret. Perfecto Compuesto**: *he hablado* |
| | **Pret. Imperfecto**: *hablaba* | **Pret. Pluscuamperfecto**: *había hablado* |
| | **Pret. Indefinido (Perfecto Simple)**: *hablé* | **Pret. Anterior**: *hube hablado* |
| | **Futuro Simple**: *hablaré* | **Futuro Compuesto**: *habré hablado* |
| | **Condicional Simple**: *hablaría* | **Condicional Compuesto**: *habría hablado* |
| **Subjuntivo** | **Presente**: *hable* | **Pret. Perfecto**: *haya hablado* |
| | **Pret. Imperfecto**: *hablara / hablase* | **Pret. Pluscuamperfecto**: *hubiera / hubiese hablado* |
| **Imperativo** | **Afirmativo**: *habla tú, hable usted* | *(Negativo uses Presente Subjuntivo)* |

### 1.3 Stem Alternations & Irregular Paradigms
- **Diphthongization**:
  - `e` $\to$ `ie`: *pensar* $\to$ *pienso*, *entender* $\to$ *entiendo*.
  - `o` $\to$ `ue`: *dormir* $\to$ *duermo*, *volver* $\to$ *vuelvo*.
- **Vowel Raising**:
  - `e` $\to$ `i`: *pedir* $\to$ *pido*, *servir* $\to$ *sirvo*.
- **Velar Insertions (*G-Verbs*)**:
  - *poner* $\to$ *pongo*, *salir* $\to$ *salgo*, *tener* $\to$ *tengo*, *venir* $\to$ *vengo*.
- **Suppletive & Radical Irregulars**:
  - *ser*: *soy, eres, es, somos, sois, son* (Pret: *fui, fuiste, fue*).
  - *estar*: *estoy, estás, está* (Pret: *estuve*).
  - *ir*: *voy, vas, va* (Pret: *fui, fuiste, fue*).
  - *haber*: Auxiliary base (*he, has, ha/hay, hemos, habéis, han*).

---

## 2. Nominal & Adjectival Concordance
- **Gender Agreement**: Masculine and feminine inflection:
  - Canonical: `-o` (masc), `-a` (fem): *chico alto* vs *chica alta*.
  - Invariant in `-e` or consonant: *inteligente*, *azul*, *feliz*.
  - Heterogeneous nouns: *el día* (masc), *la mano* (fem), *el problema* (masc from Greek), *el mapa* (masc).
  - Tonic feminine *a-* requiring masculine singular article: *el agua clara*, *el águila real*.
- **Number Agreement**:
  - Vowel-ending: adds `-s` (*casas*, *perros*).
  - Consonant-ending: adds `-es` (*ciudades*, *árboles*).
  - Words ending in `-z`: orthographic mutation to `-ces` (*pez* $\to$ *peces*, *feliz* $\to$ *felices*).
- **Mandatory Prepositional Contractions**:
  - `a + el` $\longrightarrow$ **al** (*Voy al mercado*).
  - `de + el` $\longrightarrow$ **del** (*El libro del estudiante*).
