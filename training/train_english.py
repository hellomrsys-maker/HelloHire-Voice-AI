"""
train_english.py - Direct entrypoint to English_engine/train.py.

Executes the dedicated, self-contained single-file English engine trainer.
"""

from __future__ import annotations
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from English_engine.train import main

if __name__ == "__main__":
    main()
