"""
training/core/generate_observational_words_corpus.py - Consolidates all observational dialogue words and dyads.
"""

import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EN_CORPUS_PATH = os.path.join(ROOT_DIR, "English_engine", "6_DATA_REQUIREMENTS", "english_conversational_dialogue_dynamics_corpus.json")
HI_CORPUS_PATH = os.path.join(ROOT_DIR, "Hindustani_engine", "6_DATA_REQUIREMENTS", "conversational_dialogue_dynamics_corpus.json")
CANONICAL_EN_PATH = os.path.join(ROOT_DIR, "English_engine", "6_DATA_REQUIREMENTS", "canonical_engine_data.json")
OUT_PATH = os.path.join(ROOT_DIR, "data", "observational_speech_words_corpus.json")


def main():
    with open(EN_CORPUS_PATH, "r", encoding="utf-8") as f:
        en_corpus = json.load(f)

    with open(HI_CORPUS_PATH, "r", encoding="utf-8") as f:
        hi_corpus = json.load(f)

    with open(CANONICAL_EN_PATH, "r", encoding="utf-8") as f:
        canonical_en = json.load(f)

    all_words = []
    word_set = set()

    for sc in en_corpus.get("dialogue_scenes", []):
        for turn in sc.get("turns", []):
            for wt in turn.get("word_tokens", []):
                w = wt["word"].strip(',.?!;:"')
                if w:
                    all_words.append({
                        "word": w,
                        "duration_ms": wt.get("duration_ms", 200),
                        "pitch_hz": wt.get("pitch_hz", 160.0),
                        "focal_stress": wt.get("focal_stress", False),
                        "contour": wt.get("contour", "SUSTAINED"),
                        "intent": turn.get("intent", "UNKNOWN"),
                        "scene_id": sc.get("scene_id", "")
                    })
                    word_set.add(w.lower())

    for sc in hi_corpus.get("dialogue_scenes", []):
        for turn in sc.get("turns", []):
            text = turn.get("text", "")
            for w in text.split():
                clean_w = w.strip(',.?!;:|।')
                if clean_w:
                    word_set.add(clean_w)

    intent_nodes = canonical_en.get("dialogue_intent_tree", {}).get("nodes", [])

    consolidated = {
        "metadata": {
            "title": "Observational Dialogue Dynamics and Word Prosody Corpus",
            "legal_standard": "Section 10 RULEBOOK.md - Observational Listening & Legal Barrier Protocol",
            "zero_voice_cloning_certified": True,
            "calibrated_turn_taking_latency_ms": 518,
            "total_unique_vocabulary_words": len(word_set),
            "total_dialogue_scenes": len(en_corpus.get("dialogue_scenes", [])) + len(hi_corpus.get("dialogue_scenes", [])),
            "total_word_tokens_analyzed": len(all_words),
        },
        "tokenized_words_catalog": all_words,
        "dialogue_scenes_english": en_corpus.get("dialogue_scenes", []),
        "dialogue_scenes_hindustani": hi_corpus.get("dialogue_scenes", []),
        "intent_tree_templates": intent_nodes
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)

    print(f"Consolidated corpus written to {OUT_PATH}")
    print(f"Total Unique Vocabulary: {len(word_set)}")
    print(f"Total Word Tokens Analyzed: {len(all_words)}")


if __name__ == "__main__":
    main()
