"""
training package root.

Exposes core training infrastructure and sub-packages:
- core
- bubbles
- cognitive
- legacy
"""

import os
import sys
import importlib

_DIR = os.path.dirname(os.path.abspath(__file__))

# Extend package search path to subdirectories so `from training.<module> import ...` works
__path__ = [
    _DIR,
    os.path.join(_DIR, "core"),
    os.path.join(_DIR, "bubbles"),
    os.path.join(_DIR, "cognitive"),
    os.path.join(_DIR, "legacy"),
]

# Ensure sub-directories are in sys.path for direct module discovery
for sub in ["core", "bubbles", "cognitive", "legacy"]:
    p = os.path.join(_DIR, sub)
    if p not in sys.path:
        sys.path.insert(0, p)


def __getattr__(name: str):
    """Fallback dynamic attribute resolver for sub-module compatibility."""
    for sub in ["core", "bubbles", "cognitive", "legacy"]:
        candidate = os.path.join(_DIR, sub, f"{name}.py")
        if os.path.exists(candidate):
            try:
                mod = importlib.import_module(f"training.{sub}.{name}")
            except Exception:
                mod = importlib.import_module(name)
            sys.modules[f"training.{name}"] = mod
            return mod
    raise AttributeError(f"module 'training' has no attribute '{name}'")
