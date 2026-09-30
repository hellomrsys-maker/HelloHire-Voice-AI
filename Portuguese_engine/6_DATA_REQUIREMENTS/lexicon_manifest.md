# Layer 6: Data Requirements & Lexicon Manifest - Portuguese Engine (Português)

## 1. Corpus Resources & Annotation Standards
The Portuguese engine integrates verified open-source treebanks and lexicons:
- **UD Portuguese-Bosque / UD Portuguese-GSD**: Universal Dependencies annotated for POS tags, morphological features (mood, tense, person, clitics), and dependency syntax.
- **Dicionário Aberto / Priberam API Schema**: Comprehensive base lemmas and etymological roots.
- **CETENFolha & CETEMPúblico**: Large-scale newspaper corpora for Brazilian and European Portuguese frequency modeling.
- **WordNet.Br / OpenWordnet-PT**: Ontological synsets and semantic relation networks.

---

## 2. Core Lexicon Inventories

### 1. Irregular Verbs Manifest
- *ser, estar, ter, haver, ir, vir, fazer, dizer, poder, pôr, saber, querer, trazer, ver, dar*.

### 2. Prepositional Contractions Table
- *de + [o, a, os, as, este, esta, estes, estas, esse, essa, esses, essas, aquele, aquela, aqueles, aquelas, ele, ela, eles, elas, isto, isso, aquilo]*
- *em + [o, a, os, as, um, uma, uns, umas, este, esta, estes, estas, esse, essa, esses, essas, aquele, aquela, aqueles, aquelas, isto, isso, aquilo]*
- *a + [o, a, os, as, aquele, aquela, aqueles, aquelas, aquilo]* (triggering crase: *à, às, àquele, àquela, àqueles, àquelas, àquilo*)
- *por + [o, a, os, as]* (*pelo, pela, pelos, pelas*)

### 3. Clitic Pronoun Manifest
- Direct Object: *me, te, o, a, nos, vos, os, as*
- Indirect Object: *me, te, lhe, nos, vos, lhes*
- Reflexive: *me, te, se, nos, vos, se*
- Allomorphs: *-lo, -la, -los, -las* (after -r, -s, -z), *-no, -na, -nos, -nas* (after nasal dipthongs).

---

## 3. AO90 Compliance Lexicon
Lists standardized spellings under the 1990 Orthographic Agreement:
- Removed consonants: *ação* (not *acção*), *direção* (not *direcção*), *fato* (pt-BR) / *facto* (pt-PT where pronounced).
- Unaccented paroxytones: *ideia, assembleia, heroico, jiboia*.
- Des-trema: *cinquenta, tranquilo, frequência*.
