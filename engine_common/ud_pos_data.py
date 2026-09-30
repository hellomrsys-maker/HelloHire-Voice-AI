"""
ud_pos_data.py — Universal Dependencies POS-Tagging Dataset Builder.
====================================================================

Turns the raw CoNLL-U treebanks in the local UD 2.18 release into REAL
part-of-speech supervision: sequences of (word, UPOS) pairs. This uses the
genuine linguistic annotation in UD (column 4 = UPOS) rather than just the
sentence text, so we can train an actual POS tagger per language.

CoNLL-U columns (tab-separated):
    0 ID  1 FORM  2 LEMMA  3 UPOS  4 XPOS  5 FEATS  6 HEAD  7 DEPREL  8 DEPS  9 MISC

The 17 Universal POS tags (plus a PAD slot at index 0) are the label space.
"""

from __future__ import annotations
import os
import tarfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# The 17 universal POS tags (UD v2). Index 0 is reserved for PAD.
UPOS_TAGS = [
    "<PAD>",
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
    "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X",
]
UPOS2ID: Dict[str, int] = {t: i for i, t in enumerate(UPOS_TAGS)}
NUM_UPOS = len(UPOS_TAGS)


@dataclass
class PosSentence:
    words: List[str]
    tags: List[int]        # UPOS ids aligned to words


@dataclass
class PosDataset:
    engine_dir: str
    treebank: str
    train: List[PosSentence] = field(default_factory=list)
    val: List[PosSentence] = field(default_factory=list)
    license: str = "unknown"
    status: str = "ok"


def _find_local_ud_archive() -> Optional[str]:
    # Reuse the ingest module's locator to avoid duplication.
    try:
        from .data_ingest import find_local_ud_archive
        return find_local_ud_archive()
    except Exception:
        cand = r"C:\Users\sysyo\Downloads\Universal Dependencies 2.18\ud-treebanks-v2.18.tgz"
        return cand if os.path.exists(cand) else None


def parse_conllu_pos(conllu: str, max_sentences: int, max_len: int = 40) -> List[PosSentence]:
    """Parse (word, UPOS) sequences from CoNLL-U text."""
    sentences: List[PosSentence] = []
    words: List[str] = []
    tags: List[int] = []
    for line in conllu.splitlines():
        if not line.strip():
            # sentence boundary
            if 1 <= len(words) <= max_len:
                sentences.append(PosSentence(words=words, tags=tags))
            words, tags = [], []
            if len(sentences) >= max_sentences:
                break
            continue
        if line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 4:
            continue
        idx = cols[0]
        # Skip multi-word token ranges (e.g. "3-4") and empty nodes ("3.1").
        if not idx.isdigit():
            continue
        form = cols[1].strip()
        upos = cols[3].strip()
        if not form:
            continue
        words.append(form)
        tags.append(UPOS2ID.get(upos, UPOS2ID["X"]))
    if words and 1 <= len(words) <= max_len and len(sentences) < max_sentences:
        sentences.append(PosSentence(words=words, tags=tags))
    return sentences


def _ud_cache_dir() -> Optional[str]:
    """Return the extract-once UD cache directory if it exists."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache = os.path.join(root, "scratch", "_ud_cache")
    return cache if os.path.isdir(cache) else None


def _split_sents(sents, val_fraction, ds, tb, license_text):
    ds.treebank = tb
    ds.license = license_text
    n_val = max(1, int(len(sents) * val_fraction)) if len(sents) > 5 else 0
    ds.val = sents[:n_val]
    ds.train = sents[n_val:] or sents
    return ds


def _build_from_cache(engine_dir, treebanks, max_sentences, val_fraction, ds) -> Optional[PosDataset]:
    """Read POS data from the on-disk extracted UD cache (instant). Returns None if
    the cache or the wanted treebanks are absent (caller falls back to the tarball)."""
    cache = _ud_cache_dir()
    if not cache:
        return None
    for tb in treebanks:
        tb_dir = None
        for top in os.listdir(cache):
            cand = os.path.join(cache, top, tb)
            if os.path.isdir(cand):
                tb_dir = cand
                break
        if not tb_dir:
            continue
        files = os.listdir(tb_dir)
        license_text = "unknown"
        for fn in files:
            if fn.upper().startswith("LICENSE"):
                try:
                    txt = open(os.path.join(tb_dir, fn), encoding="utf-8", errors="replace").read()
                    license_text = next((l.strip() for l in txt.splitlines() if l.strip()), "unknown")[:200]
                except Exception:
                    pass
                break
        conllu_files = sorted((f for f in files if f.endswith(".conllu")),
                              key=lambda f: (("train" not in f), f))
        sents: List[PosSentence] = []
        for fn in conllu_files:
            try:
                conllu = open(os.path.join(tb_dir, fn), encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            remaining = max_sentences - len(sents)
            if remaining <= 0:
                break
            sents.extend(parse_conllu_pos(conllu, max_sentences=remaining))
        if sents:
            return _split_sents(sents, val_fraction, ds, tb, license_text)
    return None  # wanted treebanks not in cache -> fall back to tarball


def build_pos_dataset(
    engine_dir: str,
    treebanks: List[str],
    max_sentences: int = 600,
    val_fraction: float = 0.2,
    archive_path: Optional[str] = None,
) -> PosDataset:
    """
    Build a POS train/val dataset for one engine from the first available UD treebank
    in ``treebanks`` (read from the local UD tarball, single streaming pass).
    """
    ds = PosDataset(engine_dir=engine_dir, treebank="")

    # FAST PATH: read from an already-extracted UD cache on disk if present.
    cache_hit = _build_from_cache(engine_dir, treebanks, max_sentences, val_fraction, ds)
    if cache_hit is not None:
        return cache_hit
    # If a cache exists but did not contain these treebanks, do NOT fall back to the
    # slow full-tarball scan (which streams ~500MB) — report missing quickly instead.
    if _ud_cache_dir() is not None:
        ds.status = "treebank not in UD cache"
        return ds

    archive_path = archive_path or _find_local_ud_archive()
    if not archive_path:
        ds.status = "no local UD archive"
        return ds

    wanted = set(treebanks)
    collected: Dict[str, List[PosSentence]] = {}
    licenses: Dict[str, str] = {}
    try:
        with tarfile.open(archive_path, "r|gz") as tf:
            for m in tf:
                parts = m.name.split("/")
                if len(parts) < 2 or parts[1] not in wanted or not m.isreg():
                    continue
                if m.name.upper().endswith("LICENSE.TXT") or m.name.upper().endswith("LICENSE"):
                    try:
                        txt = tf.extractfile(m).read().decode("utf-8", errors="replace")
                        licenses[parts[1]] = next(
                            (l.strip() for l in txt.splitlines() if l.strip()), "unknown")[:200]
                    except Exception:
                        pass
                    continue
                if m.name.endswith(".conllu"):
                    try:
                        conllu = tf.extractfile(m).read().decode("utf-8", errors="replace")
                    except Exception:
                        continue
                    sents = parse_conllu_pos(conllu, max_sentences=max_sentences)
                    collected.setdefault(parts[1], [])
                    # Prefer train files; concatenate but cap.
                    remaining = max_sentences - len(collected[parts[1]])
                    if remaining > 0:
                        collected[parts[1]].extend(sents[:remaining])
    except Exception as exc:
        ds.status = f"failed: {type(exc).__name__}: {exc}"
        return ds

    # Pick the treebank (in preference order) that yielded the most sentences.
    best_tb = None
    for tb in treebanks:
        if collected.get(tb):
            best_tb = tb
            break
    if not best_tb:
        ds.status = "no POS sentences found"
        return ds

    ds.treebank = best_tb
    ds.license = licenses.get(best_tb, "unknown")
    sents = collected[best_tb]
    n_val = max(1, int(len(sents) * val_fraction)) if len(sents) > 5 else 0
    ds.val = sents[:n_val]
    ds.train = sents[n_val:] or sents
    return ds
