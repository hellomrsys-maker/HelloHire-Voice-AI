# Morphological Analysis & Grammar Rules for Tamil (Word Layer)
## Sovereign Engine: `Tamil_engine` | Agglutinative Core

### 1. The Classical Dravidian Agglutination Paradigm
Tamil is an exclusively **suffixing agglutinative** language. Words are formed by stringing transparent, discrete grammatical morphemes to an invariant or morphophonemically regularized root:

$$\text{Noun Word} = \text{Root} + (\text{Plural Suffix}) + (\text{Oblique Stem Formative}) + (\text{Case Suffix}) + (\text{Clitic})$$
$$\text{Verb Word} = \text{Root} + (\text{Causative Suffix}) + (\text{Tense/Aspect Marker}) + (\text{PNG Agreement Suffix})$$

---

### 2. The 8 Grammatical Cases (*Vēṟṟumai* வேற்றுமை)

| Case Number | Traditional Name | Suffix Form | Function & Meaning | Example (Root: *maram* மரம் "tree" / *avan* அவன் "he") |
| :--- | :--- | :--- | :--- | :--- |
| **1st** | *Mutal* (Nominative) | $-\emptyset$ (Zero) | Subject of clause | *மரம்* (*maram*), *அவன்* (*avaṉ*) |
| **2nd** | *Iraṇṭām* (Accusative) | *-ai* (-ஐ) | Direct Object (definite) | *மரத்தை* (*marattai*), *அவனை* (*avaṉai*) |
| **3rd** | *Mūṉṟām* (Instrumental/Sociative) | *-āl* (-ஆல்) / *-uṭaṉ* (-உடன்) | Instrument ("by/with") / Companion ("along with") | *மரத்தால்* (*marattāl*), *அவனுடன்* (*avaṉuṭaṉ*) |
| **4th** | *Nāṉkām* (Dative) | *-ku* (-க்கு) / *-ukku* (-உக்கு) | Recipient, Direction ("to/for"), Experiencer | *மரத்துக்கு* (*marattukku*), *அவனுக்கு* (*avaṉukku*) |
| **5th** | *Aintām* (Ablative) | *-iliruntu* (-இலிருந்து) | Motion away from ("from") | *மரத்திலிருந்து* (*marattiliruntu*), *அவனிடமிருந்து* (*avaṉiṭamiruntu*) |
| **6th** | *Āṟām* (Genitive/Possessive) | *-iṉ* (-இன்) / *-uṭaiya* (-உடைய) | Possession, attribution ("of") | *மரத்தின்* (*marattiṉ*), *அவனுடைய* (*avaṉuṭaiya*) |
| **7th** | *Ēḻām* (Locative) | *-il* (-இல்) / *-iṭam* (-இடம்) | Location ("in/at/on") (*-iṭam* for animates) | *மரத்தில்* (*marattil*), *அவனிடம்* (*avaṉiṭam*) |
| **8th** | *Eṭṭām* (Vocative) | *-ē* (-ஏ) / elongation | Address / invocation ("O ... !") | *மரமே!* (*maramē!*), *மாணவா!* (*māṇavā!*) |

---

### 3. Verb Morphology: Tense Stems & PNG Concord
Tamil finite verbs obligatorily encode Person-Number-Gender (PNG) agreement concordant with the subject:

#### A. Three Primary Tenses
1. **Past (*Iṟantakālam*)**: Markers *-t-*, *-tt-*, *-nt-*, *-iṉ-*
   - Weak: *செய் + த் + ஏன்* $\to$ *செய்தேன்* (*ceytēṉ* - "I did")
   - Strong: *படி + த் + த் + ஏன்* $\to$ *படித்தேன்* (*paṭittēṉ* - "I studied")
2. **Present (*Nikaḻkālam*)**: Markers *-kiṟ-*, *-kkiṟ-*, *-kiṉṟ-*
   - Weak: *செய் + கிற் + ஏன்* $\to$ *செய்கிறேன்* (*ceykiṟēṉ* - "I do")
   - Strong: *படி + க்கிற் + ஏன்* $\to$ *படிக்கிறேன்* (*paṭikkiṟēṉ* - "I study")
3. **Future (*Etirkālam*)**: Markers *-v-*, *-pp-*, *-p-*
   - Weak: *செய் + வ் + ஏன்* $\to$ *செய்வேன்* (*ceyvēṉ* - "I will do")
   - Strong: *படி + ப்ப் + ஏன்* $\to$ *படிப்பேன்* (*paṭippēṉ* - "I will study")

#### B. Person-Number-Gender (PNG) Agreement Suffixes

| Person | Number | Gender / Deference | Suffix | Example (*paṭi* "study", Past) | Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1st** | Singular | Common | *-ēṉ* (-ஏன்) | *படித்தேன்* (*paṭittēṉ*) | "I studied" |
| **1st** | Plural | Exclusive/Common | *-ōm* (-ஓம்) | *படித்தோம்* (*paṭittōm*) | "We studied" |
| **2nd** | Singular | Informal | *-āy* (-ஆய்) | *படித்தாய்* (*paṭittāy*) | "You studied" |
| **2nd** | Plural / Hon | Polite Honorific | *-īrkaḷ* (-ீர்கள்) | *படித்தீர்கள்* (*paṭittīrkaḷ*) | "You (hon/pl) studied" |
| **3rd** | Singular | Masculine (*Āṇpāl*) | *-āṉ* (-ஆன்) | *படித்தான்* (*paṭittāṉ*) | "He studied" |
| **3rd** | Singular | Feminine (*Peṇpāl*) | *-āḷ* (-ஆள்) | *படித்தாள்* (*paṭittāḷ*) | "She studied" |
| **3rd** | Plural / Hon | Epicene / Honorific (*Palarpāl*) | *-ārkaḷ* (-ார்கள்) / *-ār* (-ார்) | *படித்தார்கள்* (*paṭittārkaḷ*) | "They / He/She (hon) studied" |
| **3rd** | Singular | Neuter (*Oṉṟaṉpāl*) | *-atu* (-அது) | *படித்தது* (*paṭittatu*) | "It studied / read" |
| **3rd** | Plural | Neuter Plural (*Palaviṉpāl*) | *-aṉa* (-அன) | *படித்தன* (*paṭittaṉa*) | "They (inanimate) studied" |

---

### 4. Sandhi (*Puṇarcci* புணர்ச்சி) Morphophonemics
When two morphemes or words join:
1. **Doubling of Plosives (Valikattal வலிமிகல்)**:
   After accusative *-ai*, dative *-ku*, and certain adverbs (*ini, aṅkē*), subsequent plosives (*k, c, t, p*) double:
   - *புத்தகத்தை + படி* $\to$ *புத்தகத்தைப் படி* (*puttakattaip paṭi*)
   - *வீட்டுக்கு + போ* $\to$ *வீட்டுக்குப் போ* (*vīṭṭukkup pō*)
2. **Intervocalic Glides (*Uṭampaṭumey* உடம்படுமெய்)**:
   - Front vowels (*i, ī, e, ē, ai*) insert *-y-* (-ய்-): *கிளி + ஐ* $\to$ *கிளியை* (*kiḷiyai*).
   - Back/neutral vowels (*a, ā, u, ū, o, ō*) insert *-v-* (-வ்-): *பசு + ஐ* $\to$ *பசுவை* (*pasuvai*).
