# Telugu Linguistic Layer 6: Data Requirements
## తెలుగు డేటా మరియు కార్పస్ ప్రమాణాలు (Data Requirements)

Layer 6 formalizes the data contracts, lexical inventories, and conversational pathways required for the **Telugu Linguistic Engine (తెలుగు ఇంజిన్)**.

---

### 1. Canonical Engine Dataset (`canonical_engine_data.json`)
The canonical dataset serves as the single source of truth for the Telugu training engine:
- **Typology**: `SOV_AGGLUTINATIVE_HEAD_FINAL` (కర్త - కర్మ - క్రియ క్రమం).
- **Latency Prosody Calibration**:
  - Calibrated Turn-Taking Gap: **518 ms**
  - Baseline $F_0$: **218.0 Hz**
  - Syllable Speech Tempo: **3.7 sps** (Ajanta vowel-ending musical flow)
  - Vocal Roughness: **0.72**
- **Hierarchical Dialogue Intent Tree**:
  - 6 Production Intent Nodes (`STATUS_INQUIRY`, `ATTENTION_FOCUS_CHECK`, `SYSTEM_INQUIRY`, `AUTHORIZATION_INQUIRY`, `REASSURANCE_EMPATHY`, `CLOSURE_DEPARTURE`).
  - Total Generative Capacity: **432+ sentences** generated from slot-equivalence templates with $O(1)$ traversal.

---

### 2. Curriculum Sentence Corpora
- 20 canonical curriculum sentences encompassing Telugu syntax, morphology, the 8 Vibhaktulu case paradigms, Sandhi phonology, and pragmatic honorific registers (`మీరు` vs `నువ్వు`).
