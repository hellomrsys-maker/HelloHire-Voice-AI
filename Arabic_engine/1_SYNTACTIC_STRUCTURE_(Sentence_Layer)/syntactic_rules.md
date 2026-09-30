# Arabic Engine — Layer 1: Syntactic Structure (Sentence Layer)

## 1. Classical & Modern Standard Arabic Clausal Syntax

Arabic possesses two primary clausal configurations with distinct agreement dynamics:
1. **Verbal Sentence (الجُمْلَةُ الفِعْلِيَّةُ - al-Jumla al-Fi'liyya)**: Canonical Head-Initial **VSO** order.
2. **Nominal Sentence (الجُمْلَةُ الاِسْمِيَّةُ - al-Jumla al-Ismiyya)**: Topic-Comment **SVO** order or Copula-less Equational order (Mubtada' and Khabar).

```
   Verbal Clause (VSO)                   Nominal Clause (SVO)
          VP                                      IP
        ┌─┴─┐                                   ┌─┴─┐
        V   NP(Subj)                            NP  VP
        │     │                                  │   │
     qara'a al-awlādu (Singular V)            al-awlādu qara'ū (Plural V)
```

---

## 2. The Asymmetry of Subject-Verb Concord

The syntactic positioning of the subject relative to the verb determines number concord:

### 2.1 Pre-verbal Subject (SVO): Full Concord
When the subject precedes the verb (Nominal Sentence), the verb **must agree in both gender and number**:
- *Al-mu'allimu kataba* (المُعَلِّمُ كَتَبَ) — Masc. Sg.
- *Al-mu'allimāni katabā* (المُعَلِّمَانِ كَتَبَا) — Masc. Dual.
- *Al-mu'allimūna katabū* (المُعَلِّمُونَ كَتَبُوا) — Masc. Plural.
- *Al-mu'allimātun katabna* (المُعَلِّمَاتُ كَتَبْنَ) — Fem. Plural.

### 2.2 Post-verbal Subject (VSO): Gender-Only Partial Concord
When the verb precedes the overt nominal subject (Verbal Sentence), the verb **must remain grammatically singular**, agreeing **only in gender**:
- *Kataba al-mu'allimu* (كَتَبَ المُعَلِّمُ) — Sg. verb + Sg. subject.
- *Kataba al-mu'allimāni* (كَتَبَ المُعَلِّمَانِ) — Sg. verb + Dual subject.
- *Kataba al-mu'allimūna* (كَتَبَ المُعَلِّمُونَ) — Sg. verb + Plural subject (*\katabū al-mu'allimūna is ungrammatical in Classical MSA).
- *Katabat al-mu'allimātu* (كَتَبَتِ المُعَلِّمَاتُ) — Fem. Sg. verb + Fem. Plural subject.

---

## 3. Deflected Agreement (جَمْعُ غَيْرِ العَاقِلِ)

A universal structural rule of Arabic syntax dictates that **all non-human plurals are treated as Feminine Singular** (كُلُّ جَمْعٍ غَيْرِ عَاقِلٍ مُؤَنَّثٌ مَفْرَدٌ):
- Noun: *al-kutub* (الكُتُبُ - books, non-human plural).
- Demonstrative: *hādhihi al-kutub* (هَذِهِ الكُتُبُ - "this [fem sg] books").
- Adjective: *al-kutubu al-jadīdatu* (الكُتُبُ الجَدِيدَةُ - "the books the-new [fem sg]").
- Relative Pronoun: *al-kutubu allatī...* (الكُتُبُ الَّتِي - "the books which [fem sg]").
- Verb: *al-kutubu tufīdu an-nāsa* (الكُتُبُ تُفِيدُ النَّاسَ - "the books benefits [fem sg] the people").

---

## 4. The Idafa (Genitive Construct - الإِضَافَةُ)

The Idafa expresses possession, attribution, or categorization through juxtaposition of nouns:
$$\text{Idafa} = [\text{Term 1: Mudāf}] + [\text{Term 2: Mudāf Ilayh}]$$

### 4.1 Structural Constraints on Term 1 (المُضَافُ - al-Mudāf):
1. **Forbidden Definite Article**: Must never take *al-* (الـ).
2. **Forbidden Nunation**: Must never take tanwīn (ـٌ / ـٍ / ـً).
3. **Loss of Dual and Plural Nūn**: Dual suffix *-āni/-ayni* drops to *-ā/-ay*; Sound masculine plural *-ūna/-īna* drops to *-ū/-ī* (e.g. *kitābā ar-rajuli*, *mu'allimū al-madrasati*).

### 4.2 Structural Constraints on Term 2 (المُضَافُ إِلَيْهِ - al-Mudāf Ilayh):
1. **Obligatory Genitive Case (مَجْرُورٌ - Majrūr)**: Marked by kasra (ـِ) or suffix *-i/-in* / *-īna*.
2. Determines the definiteness of the entire construct: if Term 2 is definite, Term 1 becomes definite; if Term 2 is indefinite, Term 1 is indefinite.
