# French Syntactic Structure & Grammar Invariants (Sentence Layer)

## 1. Typological Overview
- **Family**: Indo-European -> Romance -> Italo-Western -> Gallo-Romance.
- **Constituent Order**: SVO (Subject-Verb-Object) canonical in affirmative main clauses.
- **Subject Prominence**: **Strictly Non-Pro-Drop** (unlike Spanish or Italian). Overt subject pronouns (*je, tu, il, elle, on, nous, vous, ils, elles*) or nominal subjects are strictly obligatory, including dummy/expletive pronouns (*il pleut*, *il faut*).
- **Negation Typology**: Bipartite discontinuous negation (*ne ... pas*, *ne ... jamais*, *ne ... rien*, *ne ... plus*, *ne ... personne*). In colloquial spoken registers, *ne* is frequently dropped, but in formal written registers, bipartite closure is strictly mandatory.

## 2. Universal Dependencies (UD) POS Mapping
French tokens map to the 17 Universal Dependencies morphosyntactic categories:
- `NOUN`: Common nouns (*homme, livre, maison, développement*)
- `PROPN`: Proper nouns (*France, Paris, Marie, Victor*)
- `VERB`: Lexical verbs (*parler, finir, comprendre, vouloir*)
- `AUX`: Auxiliaries & copulas (*avoir, être, faire* in causative)
- `ADJ`: Qualitative & relational adjectives (*grand, petit, français, difficile*)
- `DET`: Determiners (Definite: *le, la, les*; Indefinite: *un, une, des*; Partitive: *du, de la, des*; Possessive: *mon, ma, mes*, etc.)
- `PRON`: Pronouns (Subject: *je, il*; Tonic: *moi, lui*; Clitic object: *le, lui, y, en*)
- `ADP`: Prepositions (*à, de, dans, pour, avec, sans, sur, sous*)
- `ADV`: Adverbs (*bien, mal, toujours, très, lentement*)
- `CCONJ`: Coordinating conjunctions (*et, ou, mais, donc, car, ni*)
- `SCONJ`: Subordinating conjunctions (*que, quand, si, parce que, bien que*)
- `PUNCT`: Punctuation marks (*., ,, ?, !, «, »*)

## 3. Clitic Pronoun Sequencing & Clitic Climbing
French clitic pronouns precede finite verbs in declarative statements and follow strict relative ordering:

```
[Subject] + [ne] + (me / te / se / nous / vous)
                 + (le / la / les)
                 + (lui / leur)
                 + (y)
                 + (en) + [VERB/AUX] + [pas]
```

### Examples:
- *Il me le donne.* (me [1st/2nd] before le [3rd direct])
- *Elle le lui explique.* (le [3rd direct] before lui [3rd indirect])
- *Nous y en avons trouvé.* (y before en)

In affirmative imperatives, pronouns are postposed with hyphens and tonic substitutions:
- *Donne-le-moi !* (*me* becomes *moi*)
- *Vas-y !* (euphonic -s added before *y*)

## 4. Subjunctive Mood Trigger Categories (WEIRDOS Matrix)
The subjunctive (*subjonctif*) is triggered in subordinate clauses introduced by *que* when the main clause conveys:
1. **Volition / Desire**: *vouloir que, désirer que, souhaiter que*.
2. **Necessity / Obligation**: *il faut que, il est nécessaire que*.
3. **Emotion / Sentiment**: *avoir peur que, être content que, regretter que*.
4. **Doubt / Disbelief / Denial**: *douter que, ne pas croire que, nier que*.
5. **Conjunctive Operators**: *bien que, quoique, pour que, avant que, afin que*.

## 5. Relative Pronoun Invariants
- `qui`: Subject relative pronoun (*L'homme qui parle*).
- `que` / `qu'`: Direct object relative pronoun (*Le livre qu'il lit*).
- `dont`: Genitive / prepositional phrase with *de* (*Le film dont je parle*).
- `où`: Locative / temporal relative pronoun (*La ville où j'habite*, *Le jour où tu es né*).
