"""
restructure_to_canonical_intent_trees.py

Restructures language engine data into the Single Canonical File Standard:
  <Language>_engine/6_DATA_REQUIREMENTS/canonical_engine_data.json

This file combines:
1. Engine Profile (Language, ISO, word order, script)
2. Latency & Prosody Calibration (518ms gap, baseline F0, tempo, roughness)
3. Hierarchical Dialogue Intent Tree (Slot-Equivalence Tree Graph)
4. Clean Syntactic & Pragmatic Sentences (Zero author or media footprints)

Dramatically shrinks storage footprints and provides O(1) intent traversal.
"""

from __future__ import annotations
import os
import sys
import glob
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from training.conversational_intent_tree import (
    build_default_english_intent_tree,
    build_default_hindustani_intent_tree,
    IntentTreeNode,
    ConversationalIntentTree
)

def build_canonical_data_for_engine(engine_dir: str):
    req_dir = os.path.join(engine_dir, "6_DATA_REQUIREMENTS")
    os.makedirs(req_dir, exist_ok=True)
    canonical_file = os.path.join(req_dir, "canonical_engine_data.json")

    # Read grammar corpus if available
    corpus_file = os.path.join(req_dir, "extracted_grammar_corpus.json")
    meta = {}
    sample_sentences = []
    if os.path.exists(corpus_file):
        with open(corpus_file, "r", encoding="utf-8") as f:
            corpus_data = json.load(f)
        meta = corpus_data.get("metadata", {})
        for item in corpus_data.get("writing_corpus", []):
            if isinstance(item, dict):
                s = (item.get("sentence") or item.get("text") or "").strip()
            elif isinstance(item, str):
                s = item.strip()
            elif isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str):
                s = item[0].strip()
            else:
                s = ""

            if s and not any(tag in s for tag in ["#", "(rigorously", "(methodically", "(in production"]):
                sample_sentences.append(s)
                if len(sample_sentences) >= 20:
                    break

    lang_name = meta.get("language", engine_dir.replace("_engine", ""))
    iso_codes = meta.get("iso_codes", [lang_name[:3].lower()])
    primary_iso = iso_codes[0]

    # Build or assign the Intent Tree
    if "English" in engine_dir:
        intent_tree = build_default_english_intent_tree()
    elif "Hindustani" in engine_dir:
        intent_tree = build_default_hindustani_intent_tree()
    else:
        # Generic multilingual intent tree
        intent_tree = ConversationalIntentTree(language=lang_name, default_gap_ms=518)
        intent_tree.add_node(IntentTreeNode(
            node_id=f"{primary_iso}_tree_status_inquiry",
            intent="STATUS_INQUIRY",
            calibrated_gap_ms=518,
            amsv_intent_byte=0x21,
            inbound_stems=[
                f"Status check ({lang_name})",
                f"How are operations ({lang_name})?"
            ],
            template="{subject} {valence}.",
            slots={
                "subject": ["Status", "Operations", "System"],
                "valence": ["nominal", "optimal", "ready", "stable"]
            },
            acoustic_profile={"mean_f0_hz": 220.0, "speech_rate_sps": 3.6, "vocal_roughness": 0.65}
        ))
        intent_tree.add_node(IntentTreeNode(
            node_id=f"{primary_iso}_tree_directive_confirm",
            intent="DIRECTIVE_CONFIRMATION",
            calibrated_gap_ms=518,
            amsv_intent_byte=0x24,
            inbound_stems=[
                f"Confirm execution ({lang_name})",
                f"Report readiness ({lang_name})"
            ],
            template="{action} {status}.",
            slots={
                "action": ["Execution", "Module", "Pipeline"],
                "status": ["confirmed", "active", "synchronized"]
            },
            acoustic_profile={"mean_f0_hz": 230.0, "speech_rate_sps": 3.8, "vocal_roughness": 0.70}
        ))

    canonical_data = {
        "engine_profile": {
            "language": lang_name,
            "engine": engine_dir,
            "iso_codes": iso_codes,
            "scripts": meta.get("scripts", ["Default"])
        },
        "latency_prosody_calibration": {
            "calibrated_gap_ms": 518,
            "turn_taking_range_ms": [300, 650],
            "baseline_f0_hz": 230.0,
            "speech_tempo_sps": 3.6,
            "vocal_roughness": 0.75
        },
        "dialogue_intent_tree": intent_tree.to_dict(),
        "curriculum_sentences": sample_sentences
    }

    with open(canonical_file, "w", encoding="utf-8") as f:
        json.dump(canonical_data, f, ensure_ascii=False, indent=2)

    print(f"  [OK] Canonical dataset created: {canonical_file} (Capacity: {intent_tree.total_generative_capacity()} sentences)")

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine_dirs = sorted(glob.glob(os.path.join(root, "*_engine")))
    print("=" * 80)
    print(f"  [CANONICAL INTENT TREE RESTRUCTURING] Processing {len(engine_dirs)} engines")
    print("=" * 80)

    for edir in engine_dirs:
        build_canonical_data_for_engine(edir)

    print("=" * 80)
    print("  Canonical Intent Tree datasets successfully generated across all engines!")
    print("=" * 80)

if __name__ == "__main__":
    main()
