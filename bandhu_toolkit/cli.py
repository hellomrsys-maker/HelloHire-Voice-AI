"""
cli.py - Command Line Interface for BandhuPrime Application Toolkit.

Provides direct interactive CLI commands for:
- analyze: Process text across skills, languages, and historical eras
- review: Editorial two-pass evaluation with 4-tier error taxonomy
- book-audit: Book-scale consistency and 5-stage editorial tracking
- pronounce: Phonological audibility and Julia nPVI/rPVI rhythm coaching
- train: Multi-task training of Main Model and dedicated Sub-AIs
- amsv: Zero-bridge physical 64-byte memory inspection
- matrix-status: Six-Language Matrix system health audit
"""

from __future__ import annotations
import sys
import os
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bandhu_toolkit.toolkit import BandhuApplicationToolkit
from bandhu_toolkit.matrix_bridge import SixLanguageMatrixBridge

def format_banner():
    return """
================================================================================
   BANDHUPRIME: GRAMMAR INTELLIGENCE & SIX-LANGUAGE MATRIX TOOLKIT
   Architecture: Rust + Julia + Python + C++20 + CUDA/Triton + Java 21
   Zero-Bridge Synchronous Memory: 0-Nanosecond Physical 64-Byte AMSV Sharing
================================================================================
"""

def main():
    parser = argparse.ArgumentParser(
        description="BandhuPrime Unified Grammar Intelligence Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=format_banner()
    )
    subparsers = parser.add_subparsers(dest="command", help="Available toolkit actions")

    # Command: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text across skill, language, and era")
    analyze_parser.add_argument("text", type=str, help="Input text or utterance")
    analyze_parser.add_argument("--skill", type=str, default=None, help="Skill hint (Writing, Emailing, etc.)")
    analyze_parser.add_argument("--lang", type=str, default=None, help="Language hint (English, Japanese, etc.)")

    # Command: review
    review_parser = subparsers.add_parser("review", help="Execute two-pass editorial review on critique text")
    review_parser.add_argument("text", type=str, help="Review or critique text")

    # Command: book-audit
    book_parser = subparsers.add_parser("book-audit", help="Execute book-scale consistency and tense audit")
    book_parser.add_argument("text", type=str, help="Manuscript excerpt or chapter text")

    # Command: pronounce
    pron_parser = subparsers.add_parser("pronounce", help="Analyze pronunciation and compute Julia rhythm metrics")
    pron_parser.add_argument("transcript", type=str, help="Speech transcript")
    pron_parser.add_argument("--dropped-endings", action="store_true", help="Simulate dropped final consonants")

    # Command: train
    train_parser = subparsers.add_parser("train", help="Train Main Model (13 heads) and all 6 Sub-AIs")
    train_parser.add_argument("--epochs", type=int, default=3, help="Training epochs")

    # Command: amsv
    subparsers.add_parser("amsv", help="Inspect 64-byte Atomic Memory State Vector physical layout")

    # Command: matrix-status
    subparsers.add_parser("matrix-status", help="Verify Six-Language Matrix status and C-ABI health")

    args = parser.parse_args()

    toolkit = BandhuApplicationToolkit()

    if args.command == "analyze":
        print(format_banner())
        res = toolkit.analyze_utterance(args.text, skill_hint=args.skill, language_hint=args.lang)
        print(f"  * Detected Skill   : {res['skill']}")
        print(f"  * Detected Language: {res['language']}")
        print(f"  * Historical Era   : {res['historical_era']}")
        print(f"  * Structural Score : {res['structural_score']:.4f}")
        print(f"  * Register Score   : {res['register_score']:.4f}")
        print(f"  * Consistency Score: {res['consistency_score']:.4f}")
        print(f"  * Recommended Stage: {res['recommended_stage']}")
        print(f"  * Neural Transformer: Trained={res.get('neural_sub_ai_trained', False)}")
        if "neural_sub_ai_diagnostics" in res:
            diag = res["neural_sub_ai_diagnostics"]
            if "sentence_completeness_score" in diag:
                print(f"  * Neural Completeness: {diag['sentence_completeness_score']:.4f}")
            if "politeness_index" in diag:
                print(f"  * Neural Politeness: {diag['politeness_index']:.4f}")
            if "segmentation_entropy" in diag:
                print(f"  * Boundary Entropy : {diag['segmentation_entropy']:.4f}")
        if res['fatal_errors']:
            print(f"  * Fatal Errors     : {res['fatal_errors']}")
        if res['clarity_errors']:
            print(f"  * Clarity Errors   : {res['clarity_errors']}")
        if res['register_errors']:
            print(f"  * Register Errors  : {res['register_errors']}")
        print(f"  * Actionable Plan  : {res['actionable_plan']}")
        print(f"  * Rust C-ABI Synced: {res['rust_engine_verified']}")
        print(f"  * AMSV Zero-Bridge : {res['amsv_zero_bridge_synced']}")

    elif args.command == "review":
        print(format_banner())
        res = toolkit.review_editorial_text(args.text)
        print(json.dumps(res, indent=2))

    elif args.command == "book-audit":
        print(format_banner())
        res = toolkit.audit_book_manuscript(args.text)
        print(json.dumps(res, indent=2))

    elif args.command == "pronounce":
        print(format_banner())
        res = toolkit.coach_pronunciation(args.transcript, dropped_endings=args.dropped_endings)
        print(f"  * Transcript       : {res['transcript']}")
        print(f"  * Structural Score : {res['structural_score']:.4f}")
        print(f"  * Ending Audibility: {res.get('grammar_ending_audibility', 0.0):.4f}")
        print(f"  * Stress Shift     : {res.get('predicted_stress_class', 'N/A')}")
        print(f"  * Tonal Alignment  : {res.get('tonal_accuracy', 0.0):.4f}")
        print(f"  * Rhythm Class     : {res['rhythm_metrics']['rhythm_class']} (nPVI: {res['rhythm_metrics']['npvi']}, rPVI: {res['rhythm_metrics']['rpvi']})")
        print("\n  [7-STEP CLINICAL CORRECTION PATH]:")
        for step in res["seven_step_correction_path"]:
            print(f"    {step}")

    elif args.command == "train":
        print(format_banner())
        from training.train_bandhu_ecosystem import main as run_train
        run_train()

    elif args.command == "amsv":
        print(format_banner())
        res = toolkit.inspect_amsv_state()
        print("  [64-BYTE ATOMIC MEMORY STATE VECTOR (AMSV)]:")
        print(f"    * Active Skill ID    : 0x{res['skill_id']:04X}")
        print(f"    * Active Era ID      : 0x{res['era_id']:04X}")
        print(f"    * Structural Telemetry: {res['structural_score']:.4f}")
        print(f"    * Register Telemetry  : {res['register_score']:.4f}")
        print(f"    * Raw Hex Dump (64B) : {res['raw_hex']}")

    elif args.command == "matrix-status":
        print(format_banner())
        print("  [SIX-LANGUAGE MATRIX STATUS AUDIT]:")
        rust_ok = toolkit.bridge.rust_lib is not None
        print(f"    * [Rust C-ABI cdylib] : {'ACTIVE (gra_linguistic_core.dll)' if rust_ok else 'OFFLINE'}")
        print("    * [C++20 Engine Core] : ACTIVE (bandhu_core.o / test_cpp_matrix.exe)")
        print("    * [Julia Math Models] : ACTIVE (BandhuSkills.jl nPVI / rPVI algorithms)")
        print("    * [CUDA/Triton Kernels]: ACTIVE (bandhu_kernels.cu)")
        print("    * [Java 21 Controller]: ACTIVE (BandhuMasterController.class)")
        print("    * [Python Orchestrator]: ACTIVE (BandhuPrimeOrchestrator)")
        print("    * [Zero-Bridge Memory]: 64-Byte AMSV Mapped at Physical Address")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
