# Layer 1: Syntactic Structure & Topological Fields (German Language Engine)

## 1. The Topological Field Model (Topologisches Feldermodell & Satzklammer)

German syntax is governed by the structural principle of the **Sentence Bracket (Satzklammer)**, which divides every clause into five distinct topological fields:

```
+-----------+-----------------------+------------+-----------------------+-----------+
| Vorfeld   | Linke Satzklammer     | Mittelfeld | Rechte Satzklammer    | Nachfeld  |
| (Pre-field)| (Left Bracket - V2/C) | (Mid-field)| (Right Bracket - Verb)|(Post-field)|
+-----------+-----------------------+------------+-----------------------+-----------+
```

### 1.1 Clause Types & Verb Placement

| Clause Type | Left Bracket (LSK) | Right Bracket (RSK) | Word Order Typology | Example |
| :--- | :--- | :--- | :--- | :--- |
| **Main Declarative (V2)** | Finite Verb | Infinite Verb / Prefix | Verb-Second (V2) | *Der Student [liest] das Buch [vor].* |
| **Subordinate Clause (VE)**| Subordinating Conj (*dass, weil*)| Complete Verbal Complex| Verb-End (V-Ende / SOV) | *...weil der Student das Buch [gelesen hat].* |
| **Yes/No Question / Imperative (V1)**| Finite Verb | Infinite Verb / Prefix | Verb-First (V1) | *[Liest] der Student das Buch [vor]?* |

### 1.2 The Vorfeld (Pre-Field)
- In V2 main clauses, **exactly one** constituent may occupy the Vorfeld.
- It can be the Subject (*Der Lehrer gibt dem Schüler das Buch*), an Adverbial (*Gestern hat der Lehrer...*), or an Object (*Das Buch hat der Lehrer...*).
- **V2 Inversion**: Whenever any non-subject constituent occupies the Vorfeld, subject-verb inversion obligatorily occurs: the finite verb stays in the Left Bracket (position 2), and the subject is displaced into the Mittelfeld immediately following the verb.

---

## 2. The Mittelfeld Ordering Principles: TeKaMoLo & Pronoun Constraints

The Mittelfeld is bounded by the Left Bracket (finite verb or complementizer) and the Right Bracket (verb complex). Its internal constituents follow well-defined information-structural hierarchies:

### 2.1 TeKaMoLo Adverbial Sequence
Adverbial adjuncts in the Mittelfeld default to the canonical order:
1. **Temporal (Te)**: When? (*gestern, um 10 Uhr, immer*)
2. **Kausal (Ka)**: Why? (*wegen des Regens, aus Freude*)
3. **Modal (Mo)**: How? (*schnell, mit großem Fleiß, gerne*)
4. **Lokal (Lo)**: Where/Whither? (*nach Hause, in der Bibliothek*)

Example:
- *Wir sind [gestern] (Te) [wegen des Wetters] (Ka) [schnell] (Mo) [nach Hause] (Lo) gefahren.*

### 2.2 Pronominal vs Nominal Case Ordering
1. **Pronominal Arguments**: Clitic-like personal pronouns precede all nominal NPs:
   - Pronoun order: **Nominative $\to$ Accusative $\to$ Dative** (*Er hat [es] [ihm] gegeben*).
2. **Nominal Arguments**: When both arguments are full nouns, Dative precedes Accusative:
   - Noun order: **Dative (Recipient) $\to$ Accusative (Patient)** (*Er hat [dem Studenten] [das Buch] gegeben*).

---

## 3. Separable Verb Syntax (Trennbare Verben)

German prefixes split depending on the clausal clause type:
- **Separable Prefixes** (*ab-, an-, auf-, aus-, ein-, mit-, vor-, zu-, zurück-*):
  - In V2 main clauses: the finite stem raises to the Left Bracket; the separable prefix is stranded in the Right Bracket at the end of the clause (*Er [steht] jeden Morgen um sechs Uhr [auf]*).
  - In subordinate clauses: the prefix remains bound to the infinitive/participle in the Right Bracket (*...dass er jeden Morgen um sechs Uhr [aufsteht]*).
- **Inseparable Prefixes** (*be-, emp-, ent-, er-, ge-, miss-, ver-, zer-*):
  - Never separate under any syntactic configuration (*Er [versteht] die Frage*; *...weil er die Frage [versteht]*).

---

## 4. Subordination & Complementizers

Subordinate clauses introduce the Left Bracket with a complementizer, forcing all verbs to cluster in the Right Bracket:
- **Causal**: *weil, da* (+ V-End)
- **Conditional**: *wenn, falls* (+ V-End)
- **Concessive**: *obwohl, obgleich* (+ V-End)
- **Temporal**: *als* (single past event), *wenn* (repeated/present), *während, bevor, nachdem*
- **Complement**: *dass, ob* (+ V-End)
- **Relative Clauses**: Relative pronouns agree with antecedent in gender/number, but take case from their role in the relative clause:
  - *Der Mann, [den] ich gestern gesehen habe, ist mein Professor.*
