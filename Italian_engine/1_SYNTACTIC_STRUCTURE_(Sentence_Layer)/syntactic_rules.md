# Layer 1: Syntactic Structure (Sentence Layer) — Italian Language Engine

## 1. Canonical Constituent Architecture & Word Order
Italian exhibits a canonical **SVO** (Subject-Verb-Object) word order with extensive pragmatic fluidity governed by information structure (Topic-Focus articulation):
$$\text{Clause} = (\text{Topic}) + \text{Subject} + (\text{Clitic Chain}) + \text{Verb} + \text{Direct Object} + (\text{Indirect Object}) + (\text{Adjuncts})$$

### 1.1 Pro-Drop (Null-Subject Parameter)
Italian is a prototypical null-subject language. Subject personal pronouns (*io, tu, lui/lei, noi, voi, loro*) are overtly realized strictly for contrast, focus, or disambiguation:
- Standard: *Andiamo al cinema.* (Null subject `[noi]`).
- Contrastive: *Io vado al cinema, ma tu rimani a casa.*

### 1.2 Auxiliary Selection Invariants (Essere vs Avere)
In compound tenses (e.g. *passato prossimo*), auxiliary verb selection is strictly governed by verb valency and lexical aspect:
1. **Avere**: Selected by prototypical transitive verbs and unergative intransitive verbs (*ha mangiato la mela*, *ha dormito a lungo*).
2. **Essere**: Obligatorily selected by:
   - Unaccusative verbs of motion and change of state (*è andato, è arrivata, sono caduti, è nata*).
   - Reflexive and reciprocal verbs (*si è lavato, si sono parlati*).
   - Passive voice constructions (*la lettera è stata scritta*).
   - Impersonal *si* constructions (*si è deciso di partire*).
3. **Past Participle Concord Rule**:
   - With *essere*: The past participle **must agree in gender and number** with the subject (*Marco è arrivato*, *Chiara è arrivata*, *I ragazzi sono arrivati*, *Le ragazze sono arrivate*).
   - With *avere*: The past participle remains invariant masculine singular (*-o*), **unless** preceded by a 3rd-person direct object clitic (*lo, la, li, le*), in which case concord with the clitic is mandatory (*L'ho vista* [fem. sg.], *Li abbiamo comprati* [masc. pl.]).

### 1.3 Clitic Placement (Collocazione dei Clitici)
- **Proclisis**: Clitics obligatorily precede finite verbs (*Mi ha visto*, *Non glielo dire*).
- **Enclisis**: Clitics obligatorily attach to non-finite forms (infinitive, gerund) and affirmative imperatives:
  - Infinitive: *vederlo* (dropping infinitive final *-e*).
  - Gerund: *vedendolo*.
  - Affirmative Imperative: *dimmi* (with consonant doubling from *di'* + *mi*), *guardalo*.
- **Clitic Clusters**: When indirect (*mi, ti, ci, vi, si*) meets direct (*lo, la, li, le*) or partitive (*ne*), the indirect clitic vowel *-i* shifts to *-e*:
  $$\text{mi} + \text{lo} \to \text{me lo}, \quad \text{ti} + \text{ne} \to \text{te ne}, \quad \text{gli/le} + \text{lo} \to \text{glielo}$$

### 1.4 Subjunctive Mood Concord (Concordanza del Congiuntivo)
Subordinate clauses introduced by *che* obligatorily take the subjunctive mood under:
- Verbs of volition, emotion, belief, and doubt (*voglio che, spero che, credo che, dubito che*).
- Impersonal conjunctions (*benché, affinché, prima che, a meno che*).
- Hypothetical periods (Periodo Ipotetico della Possibilità / Irrealtà: *Se potessi, verrei*).
