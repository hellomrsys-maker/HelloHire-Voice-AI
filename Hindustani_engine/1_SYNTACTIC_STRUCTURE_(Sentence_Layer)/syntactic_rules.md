# Hindustani Syntactic Structure & Grammar Invariants (Sentence Layer)

## 1. Typological Overview
- **Family**: Indo-European -> Indo-Iranian -> Indo-Aryan.
- **Constituent Order**: Strictly **SOV (Subject-Object-Verb)** canonical. Verbs and auxiliaries occupy the clause-final position.
- **Head Directionality**: Head-final. Prepositions do not exist; grammatical relations are marked exclusively by **postpositions** (*ghar mein* = in the house, *mez par* = on the table).
- **Alignment Typology**: **Split-Ergativity**:
  - Non-perfective aspects (present, habitual, continuous, future): **Nominative-Accusative**. Subject has no marker, verb agrees with subject.
  - Perfective aspect with transitive verbs: **Ergative-Absolutive**. The subject takes the overt ergative postposition **ने (ne)**. The verb agrees in gender and number with the direct object (if unmarked). If the direct object is marked with the accusative/dative postposition **को (ko)**, the verb adopts the default neutral masculine singular form.

## 2. Universal Dependencies (UD) POS Mapping
- `NOUN`: Common nouns (*ladka, kitaab, ghar, shehar*)
- `PROPN`: Proper nouns (*Bharat, Dilli, Sita, Ram*)
- `VERB`: Lexical verbs (*karna, jaana, dekhna, bolna, aana*)
- `AUX`: Auxiliary verbs (*hona: hai, hain, tha, the, thi, thin, hoga, honge; sakna, chukna*)
- `ADJ`: Qualitative adjectives (Marked: *accha/acchi/acche*; Unmarked: *sundar, saaf*)
- `PRON`: Personal/demonstrative pronouns (*main, tu, tum, aap, yeh, woh, hum, kaun, koi*)
- `ADP`: Postpositions (*ne, ko, se, ka, ke, ki, mein, par, tak*)
- `ADV`: Adverbs (*jaldi, dheere, hamesha, kabhi, wahan, yahan*)
- `CCONJ`: Coordinating conjunctions (*aur, lekin, parantu, magar, ya*)
- `SCONJ`: Subordinating conjunctions (*ki, kyonki, agar, yadi, jab, jaise*)
- `PART`: Emphatic and negative particles (*bhi, hi, to, na, nahin, mat*)
- `PUNCT`: Punctuation (*|, ., ,, ?, !*)

## 3. Postpositional Alignment & Oblique Case Transformation
Any noun or pronoun followed by an overt postposition automatically undergoes inflection into the **Oblique Case**:
- Masculine singular marked nouns (*-a* ending) inflect to *-e*:
  - *ladka* (boy, direct) -> *ladke ne* (by the boy), *ladke ko* (to the boy), *ladke ka* (of the boy).
- Masculine/Feminine plural nouns inflect to *-on*:
  - *ladke* (boys, direct plural) -> *ladkon ne* (by the boys), *kitabein* (books) -> *kitabon mein* (in the books).
- Pronoun oblique transformations:
  - *main* + *ne* -> *maine*
  - *tu* + *ne* -> *tune*
  - *hum* + *ne* -> *humne*
  - *aap* + *ne* -> *aapne*
  - *yeh* + *ne* -> *isne* / *inhonne*
  - *woh* + *ne* -> *usne* / *unhonne*

## 4. Complex Predicates & Compound Verbs
Hindustani heavily utilizes two types of multi-word verbal structures:
1. **Conjunct Verbs (Noun/Adjective + Light Verb)**:
   - *madad karna* (to help), *shuru karna* (to start), *saaf karna* (to clean), *yaad aana* (to remember).
2. **Compound Verbs (Polar V1 stem + Vector V2 auxiliary)**:
   - *lena* (action for self): *khaa lena* (eat up for oneself).
   - *dena* (action directed towards other): *bata dena* (tell someone).
   - *jaana* (completion/change of state): *kho jaana* (get lost), *mar jaana* (die).
   - *daalna* (violent/forceful completion): *maar daalna* (kill decisively).
   - *baithna* (reckless/inadvertent action): *lad baithna* (quarrel foolishly).

## 5. Three-Tier Politeness Register
- **आप (aap)**: Level 3 Deferential. Highest respect; used with elders, guests, superiors, strangers. Requires plural honorific verb agreement (*aap aate hain*).
- **तुम (tum)**: Level 2 Familiar. Neutral casual; used with close peers, friends, younger siblings, coworkers. Requires 2nd person plural agreement (*tum aate ho*).
- **तू (tu)**: Level 1 Intimate. Used for deities (*Bhagwan tu daya kar*), young children, intimate lovers, or in extreme anger/disrespect (*tu kahan jaata hai*).
