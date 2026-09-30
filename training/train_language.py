"""
train_language.py - Single Total Master Language Training Entrypoint.

Trains ANY of the 45 languages or all languages sequentially in one total file.
Ingests canonical_engine_data.json and trains curriculum, Sub-AIs, intent trees,
vocal cord bio-acoustics, and zero-bridge AMSV synchronization.

Usage:
    py training/train_language.py --language English
    py training/train_language.py --language Hindustani
    py training/train_language.py --language Spanish
    py training/train_language.py --all
"""

from __future__ import annotations
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from training.train_language_engine import UniversalLanguageTrainer, main

if __name__ == "__main__":
    main()
