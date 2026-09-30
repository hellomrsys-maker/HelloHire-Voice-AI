# Hindustani Lexical Requirements & Corpus Manifests (Data Layer)

## 1. Core Lexicon Architecture
The Hindustani engine coordinates structured lexical resources for:
1. **Verbal Roots & Stems**:
   - 2,500+ simplex verbs with transitivity classifications (intransitive vs transitive vs ditransitive for ergative *ne* triggering).
   - Light verb matrices for conjunct verb constructions (*karna, hona, aana, dena, lena, lagna*).
   - Vector auxiliary matrices (*lena, dena, jaana, daalna, baithna, uthna, padna*).
2. **Postpositional Inventory**:
   - Primary case postpositions: *ne* (ergative), *ko* (dative/accusative), *se* (instrumental/ablative), *ka/ke/ki* (genitive), *mein* (locative in), *par* (locative on), *tak* (terminative up to).
   - Compound postpositions: *ke paas, ke saath, ke liye, ke baad, ke pehle, ke bina*.
3. **Dual-Script & Romanization Transliteration Tables**:
   - Character mapping between Devanagari Unicode block (U+0900 to U+097F), Arabic Nastaliq block (U+0600 to U+06FF), and standardized ITRANS/IAST romanization.

## 2. Benchmark Evaluation Datasets
- **Universal Dependencies Hindi-HDTB & Urdu-UDTB**: Over 16,000 dependency trees annotated with UD POS, morphosyntactic features, and relation arcs.
- **IIT Bombay Hindi-English Parallel Corpus**: For bilingual alignment and cross-lingual validation.
