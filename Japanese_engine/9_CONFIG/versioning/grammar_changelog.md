# Japanese Engine Linguistic Specification & Grammar Changelog

## [Version 2.0.0] - 2026-09-18

### Added
- Complete 9-layer Japanese linguistic engine architecture (`Japanese_engine/`).
- 14 Dedicated computational skills in `Japanese_engine/brain/skills/`:
  - `tokenization.py`: MeCab-class morphological segmentation with script classification.
  - `pos_tagging.py`: UniDic and MeCab-IPA hierarchical Hinshi categorization.
  - `parsing.py`: Bunsetsu chunking and head-final Kakariuke dependency parsing.
  - `lemmatization.py`: Katsuyou inversion across Godan, Ichidan, Kuru, and Suru verbs.
  - `reading_generation.py`: Kanji to Furigana and HTML5 `<ruby>` generation.
  - `ner.py`: Named Entity Recognition without capitalization cues using suffix heuristics.
  - `coreference.py`: Zero-pronoun (pro-drop) resolution via topic-chain tracking.
  - `srl.py`: Semantic Role Labeling anchored to particle case frames.
  - `sentiment.py`: Negation scope handling after the predicate and epistemic certainty scoring.
  - `kana_kanji_conversion.py`: IME candidate conversion and homophone scoring.
  - `g2p.py`: Grapheme-to-phoneme conversion and Tokyo standard pitch accent contours.
  - `stt_decoder.py`: Mora-timed acoustic decoding and Kana-to-Kanji Henkan.
  - `keigo_engine.py`: Honorific transformation across Sonkeigo, Kenjougo, and Teineigo.
  - `generation.py`: Agglutinative verbal generation with politeness constraints.
- 11 Rules specifications in `Japanese_engine/brain/rules/` including `particle_grammar.fst` and `verb_conjugation.fst`.
- 9 Analysis modules in `Japanese_engine/brain/Analysis/` including `ha_ga_resolver.py` and `zero_pronoun_resolver.py`.
- 10 Task pipelines in `Japanese_engine/brain/task/` including `ocr_postprocess.py` and `furigana_annotator.py`.
- 4 Sub-AIs in `Japanese_engine/brain/sub_ais/` with 0-nanosecond physical memory writes to AMSV.
- Six-Language Matrix in `Japanese_engine/six_language_matrix/` integrating Rust, C++20, CUDA, Java 21, Julia, and Python.
- 0-nanosecond synchronous memory synchronization under the Zero-Bridge Synchronous Memory Rule.
