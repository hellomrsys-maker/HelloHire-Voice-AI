"""
data_ingest.py — Open-Source Data Ingestion Pipeline (Phase 2).
================================================================

Downloads REAL, openly-licensed multilingual sentences and merges them into each
engine's ``6_DATA_REQUIREMENTS/extracted_grammar_corpus.json`` so the existing
supervised trainer (engine_common.subai_trainer) learns from authentic data.

Sources:
  * Tatoeba per-language sentence exports  (CC BY 2.0 FR — commercial OK).
  * Universal Dependencies treebanks       (mixed license; NC skipped when
                                            commercial_safe=True, the default).

Design:
  * Non-destructive MERGE: existing corpus sentences are preserved; new ones are
    appended and de-duplicated. Never clobbers hand-authored data.
  * Provenance: writes ``6_DATA_REQUIREMENTS/data_provenance.json`` recording every
    source, its license, attribution, and how many sentences it contributed.
  * Fully offline-safe: if a download fails, the engine keeps its existing corpus and
    the failure is recorded rather than raised.

CLI:
    python -m engine_common.data_ingest --engine Spanish_engine
    python -m engine_common.data_ingest --all
    python -m engine_common.data_ingest --engine French_engine --max 500 --allow-noncommercial
"""

from __future__ import annotations
import bz2
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .data_sources import (
    get_source, all_sources, EngineDataSource,
    TATOEBA_LICENSE, TATOEBA_ATTRIBUTION, is_commercial_safe_ud,
)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_USER_AGENT = "SoloRock-DataIngest/1.0 (open-source corpus builder)"
_MIN_WORDS = 3
_MAX_WORDS = 40


def _http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# Scripts whose text is not space-segmented; length is measured in characters.
_SPACELESS_SCRIPTS = {"Han", "Kana+Kanji", "Thai", "Myanmar"}
_MIN_CHARS = 4
_MAX_CHARS = 200


def _clean(sentence: str, spaceless: bool = False) -> Optional[str]:
    s = " ".join(sentence.split()).strip()
    if not s:
        return None
    if spaceless:
        # Space-less scripts (Chinese, Japanese, Thai, Burmese): measure by characters.
        n = len(s.replace(" ", ""))
        if n < _MIN_CHARS or n > _MAX_CHARS:
            return None
    else:
        n = len(s.split())
        if n < _MIN_WORDS or n > _MAX_WORDS:
            return None
    return s


# --------------------------------------------------------------------------- #
# Tatoeba
# --------------------------------------------------------------------------- #

def ingest_tatoeba(src: EngineDataSource, max_sentences: int = 400,
                   timeout: int = 90, spaceless: bool = False) -> Tuple[List[str], Dict]:
    """Download and parse Tatoeba sentences for one language. Returns (sentences, provenance)."""
    url = src.tatoeba_sentence_url
    prov = {"source": "Tatoeba", "url": url, "license": TATOEBA_LICENSE,
            "attribution": TATOEBA_ATTRIBUTION, "status": "ok", "count": 0}

    sentences: List[str] = []
    seen = set()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # STREAM-decompress: stop as soon as we have enough sentences instead of
            # decompressing the entire (potentially hundreds of MB) file into memory.
            decomp = bz2.BZ2Decompressor()
            buf = b""
            done = False
            while not done:
                chunk = resp.read(65536)
                if not chunk:
                    break
                try:
                    buf += decomp.decompress(chunk)
                except Exception:
                    break
                # Process complete lines held in buf.
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    parts = line.decode("utf-8", errors="replace").split("\t")
                    if len(parts) < 3:
                        continue
                    s = _clean(parts[2], spaceless=spaceless)
                    if s and s not in seen:
                        seen.add(s)
                        sentences.append(s)
                    if len(sentences) >= max_sentences:
                        done = True
                        break
    except Exception as exc:
        if not sentences:
            prov["status"] = f"failed: {type(exc).__name__}: {exc}"
            return [], prov
        prov["status"] = f"partial: {type(exc).__name__}"
    prov["count"] = len(sentences)
    return sentences, prov


# --------------------------------------------------------------------------- #
# Universal Dependencies
# --------------------------------------------------------------------------- #

_TEXT_RE = re.compile(r"^#\s*text\s*=\s*(.+)$")


def _parse_conllu_text_lines(conllu: str, spaceless: bool = False) -> List[str]:
    out: List[str] = []
    for line in conllu.splitlines():
        m = _TEXT_RE.match(line)
        if m:
            s = _clean(m.group(1), spaceless=spaceless)
            if s:
                out.append(s)
    return out


import tarfile
import glob

# Default location of a locally-downloaded UD release tarball, if present.
_LOCAL_UD_CANDIDATES = [
    r"C:\Users\sysyo\Downloads\Universal Dependencies 2.18\ud-treebanks-v2.18.tgz",
    os.path.join(os.path.expanduser("~"), "Downloads", "Universal Dependencies 2.18",
                 "ud-treebanks-v2.18.tgz"),
]


def find_local_ud_archive(explicit_path: Optional[str] = None) -> Optional[str]:
    """Locate a local UD treebanks tarball (.tgz) if one exists."""
    if explicit_path and os.path.exists(explicit_path):
        return explicit_path
    for cand in _LOCAL_UD_CANDIDATES:
        if os.path.exists(cand):
            return cand
    # Also accept an extracted 'ud-treebanks-*' directory in common Download folders.
    for base in (os.path.join(os.path.expanduser("~"), "Downloads"),):
        for hit in glob.glob(os.path.join(base, "**", "ud-treebanks-v*.tgz"), recursive=True):
            return hit
    return None


def ingest_ud_local(src: EngineDataSource, treebank: str, archive_path: str,
                    max_sentences: int = 400, commercial_safe: bool = True,
                    spaceless: bool = False) -> Tuple[List[str], Dict]:
    """Ingest a UD treebank from a LOCAL release tarball (offline, no download)."""
    prov = {"source": "UniversalDependencies(local)", "treebank": treebank,
            "archive": os.path.basename(archive_path), "license": "unknown", "status": "ok",
            "count": 0}
    try:
        tf = tarfile.open(archive_path, "r:gz")
    except Exception as exc:
        prov["status"] = f"failed to open archive: {type(exc).__name__}: {exc}"
        return [], prov

    try:
        members = tf.getmembers()
        tb_members = [m for m in members if f"/{treebank}/" in ("/" + m.name)]
        if not tb_members:
            prov["status"] = "treebank not found in archive"
            return [], prov

        # License gating.
        license_text = ""
        for m in tb_members:
            if m.name.upper().endswith("LICENSE.TXT") or m.name.upper().endswith("LICENSE"):
                try:
                    license_text = tf.extractfile(m).read().decode("utf-8", errors="replace")
                except Exception:
                    license_text = ""
                break
        label = next((ln.strip() for ln in license_text.splitlines() if ln.strip()), "unknown")
        prov["license"] = label[:200]
        if commercial_safe and not is_commercial_safe_ud(license_text or label):
            prov["status"] = "skipped: NonCommercial license (commercial_safe=True)"
            return [], prov

        sentences: List[str] = []
        seen = set()
        conllu_members = sorted((m for m in tb_members if m.name.endswith(".conllu")),
                                key=lambda m: (("train" not in m.name), m.name))
        for m in conllu_members:
            try:
                conllu = tf.extractfile(m).read().decode("utf-8", errors="replace")
            except Exception:
                continue
            for s in _parse_conllu_text_lines(conllu, spaceless=spaceless):
                if s not in seen:
                    seen.add(s)
                    sentences.append(s)
                if len(sentences) >= max_sentences:
                    break
            if len(sentences) >= max_sentences:
                break
        prov["count"] = len(sentences)
        return sentences, prov
    finally:
        tf.close()


def ingest_ud(src: EngineDataSource, treebank: str, max_sentences: int = 400,
              commercial_safe: bool = True, timeout: int = 120,
              spaceless: bool = False) -> Tuple[List[str], Dict]:
    """Download a UD treebank zip, read its LICENSE, and parse CoNLL-U sentences."""
    url = src.ud_zip_url(treebank)
    prov = {"source": "UniversalDependencies", "treebank": treebank, "url": url,
            "license": "unknown", "status": "ok", "count": 0}
    try:
        raw = _http_get(url, timeout=timeout)
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except Exception as exc:
        prov["status"] = f"failed: {type(exc).__name__}: {exc}"
        return [], prov

    # Read LICENSE for compliance gating.
    license_text = ""
    for name in zf.namelist():
        if name.upper().endswith("LICENSE.TXT") or name.upper().endswith("LICENSE"):
            try:
                license_text = zf.read(name).decode("utf-8", errors="replace")
            except Exception:
                license_text = ""
            break
    # Compact license label (first non-empty line).
    label = next((ln.strip() for ln in license_text.splitlines() if ln.strip()), "unknown")
    prov["license"] = label[:200]

    if commercial_safe and not is_commercial_safe_ud(license_text or label):
        prov["status"] = "skipped: NonCommercial license (commercial_safe=True)"
        return [], prov

    sentences: List[str] = []
    seen = set()
    for name in zf.namelist():
        if not name.endswith(".conllu"):
            continue
        try:
            conllu = zf.read(name).decode("utf-8", errors="replace")
        except Exception:
            continue
        for s in _parse_conllu_text_lines(conllu, spaceless=spaceless):
            if s not in seen:
                seen.add(s)
                sentences.append(s)
            if len(sentences) >= max_sentences:
                break
        if len(sentences) >= max_sentences:
            break
    prov["count"] = len(sentences)
    return sentences, prov


# --------------------------------------------------------------------------- #
# Corpus merge + provenance
# --------------------------------------------------------------------------- #

def _corpus_path(engine_dir: str, root: str) -> str:
    return os.path.join(root, engine_dir, "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")


def _load_existing_texts(corpus: dict) -> set:
    from .training_data import _extract_text
    existing = set()
    for row in corpus.get("writing_corpus", []) or []:
        t = _extract_text(row)
        if t:
            existing.add(t.strip())
    return existing


def merge_into_corpus(engine_dir: str, new_sentences: List[str],
                      root: str) -> Tuple[int, int]:
    """Append new sentences to writing_corpus without clobbering. Returns (added, total)."""
    path = _corpus_path(engine_dir, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    corpus = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                corpus = json.load(f)
        except Exception:
            corpus = {}
    corpus.setdefault("metadata", {})
    corpus.setdefault("writing_corpus", [])

    existing = _load_existing_texts(corpus)
    added = 0
    for s in new_sentences:
        st = s.strip()
        if st and st not in existing:
            corpus["writing_corpus"].append(
                {"text": st, "is_valid": True, "source": "open-source-ingest"})
            existing.add(st)
            added += 1

    corpus["metadata"]["total_extracted_sentences"] = len(corpus["writing_corpus"])
    corpus["metadata"]["last_ingest_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    return added, len(corpus["writing_corpus"])


def _write_provenance(engine_dir: str, root: str, records: List[Dict]) -> None:
    path = os.path.join(root, engine_dir, "6_DATA_REQUIREMENTS", "data_provenance.json")
    payload = {
        "engine": engine_dir,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": records,
        "compliance_note": ("Open-source data ingested for supervised Sub-AI training. "
                            "Retain the attributions above when distributing."),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- #
# Top-level ingest
# --------------------------------------------------------------------------- #

def ingest_engine(engine_dir: str, max_sentences: int = 400, commercial_safe: bool = True,
                  use_tatoeba: bool = True, use_ud: bool = True,
                  root: Optional[str] = None, ud_archive: Optional[str] = None) -> Dict:
    """Ingest all configured sources for one engine and merge into its corpus.

    If a local UD release tarball is available (``ud_archive`` or auto-detected), UD
    treebanks are read from it OFFLINE; otherwise the GitHub download path is used.
    """
    root = root or WORKSPACE_ROOT
    src = get_source(engine_dir)
    all_new: List[str] = []
    records: List[Dict] = []

    # Space-less scripts (CJK, Thai, Burmese) need character-based length filtering.
    spaceless = False
    try:
        from .language_profile import get_profile
        spaceless = get_profile(engine_dir).script.value in _SPACELESS_SCRIPTS
    except Exception:
        spaceless = False

    if use_tatoeba:
        sents, prov = ingest_tatoeba(src, max_sentences=max_sentences, spaceless=spaceless)
        all_new.extend(sents)
        records.append(prov)

    if use_ud:
        local_archive = ud_archive if ud_archive is not None else find_local_ud_archive()
        for tb in src.ud_treebanks:
            if local_archive:
                sents, prov = ingest_ud_local(src, tb, local_archive,
                                              max_sentences=max_sentences,
                                              commercial_safe=commercial_safe,
                                              spaceless=spaceless)
            else:
                sents, prov = ingest_ud(src, tb, max_sentences=max_sentences,
                                        commercial_safe=commercial_safe,
                                        spaceless=spaceless)
            all_new.extend(sents)
            records.append(prov)
            if prov.get("count", 0) > 0:
                break  # one good treebank is enough

    added, total = merge_into_corpus(engine_dir, all_new, root)
    _write_provenance(engine_dir, root, records)
    return {"engine": engine_dir, "added": added, "corpus_total": total,
            "sources": records}


def _extract_ud_archive_once(ud_archive: str, dest: str, wanted_treebanks: set) -> None:
    """Extract only the needed treebank folders from the tarball in ONE sequential pass.

    Python's tarfile over a large gzip stream is slow for scattered random extraction,
    but a single forward streaming pass is fast. We extract the wanted treebanks to
    ``dest`` once, then read them as plain files (instant)."""
    if os.path.isdir(dest) and os.listdir(dest):
        return  # already extracted
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(ud_archive, "r|gz") as tf:  # streaming mode (forward-only, fast)
        for m in tf:
            parts = m.name.split("/")
            if len(parts) >= 2 and parts[1] in wanted_treebanks:
                if m.isreg() and (m.name.endswith(".conllu")
                                  or m.name.upper().endswith("LICENSE.TXT")
                                  or m.name.upper().endswith("LICENSE")):
                    try:
                        tf.extract(m, dest)
                    except Exception:
                        pass


def ingest_all_local_ud(max_sentences: int = 400, commercial_safe: bool = True,
                        root: Optional[str] = None,
                        ud_archive: Optional[str] = None) -> Dict[str, Dict]:
    """
    Fast OFFLINE ingest of every engine's UD treebank.

    Strategy: extract only the needed treebank folders from the archive ONCE via a
    single forward-streaming pass, then read the resulting .conllu files from disk
    (instant). This avoids both re-opening the archive per engine and slow scattered
    random access into a large gzip stream.
    """
    root = root or WORKSPACE_ROOT
    ud_archive = ud_archive or find_local_ud_archive()
    results: Dict[str, Dict] = {}
    if not ud_archive:
        return {"error": "no local UD archive found"}

    from .language_profile import get_profile

    wanted = set()
    for _e, _src in all_sources().items():
        wanted.update(_src.ud_treebanks)

    cache = os.path.join(root, "scratch", "_ud_cache")
    _extract_ud_archive_once(ud_archive, cache, wanted)

    def _tb_dir(tb: str) -> Optional[str]:
        # Extracted layout: <cache>/ud-treebanks-vX.Y/<tb>/
        for top in os.listdir(cache):
            cand = os.path.join(cache, top, tb)
            if os.path.isdir(cand):
                return cand
        return None

    for engine_dir, src in sorted(all_sources().items()):
        try:
            spaceless = get_profile(engine_dir).script.value in _SPACELESS_SCRIPTS
        except Exception:
            spaceless = False
        records: List[Dict] = []
        new_sents: List[str] = []
        for tb in src.ud_treebanks:
            prov = {"source": "UniversalDependencies(local)", "treebank": tb,
                    "archive": os.path.basename(ud_archive), "license": "unknown",
                    "status": "ok", "count": 0}
            d = _tb_dir(tb)
            if not d:
                prov["status"] = "treebank not found in archive"
                records.append(prov)
                continue
            files = os.listdir(d)
            license_text = ""
            for fn in files:
                if fn.upper().startswith("LICENSE"):
                    try:
                        license_text = open(os.path.join(d, fn), encoding="utf-8",
                                             errors="replace").read()
                    except Exception:
                        license_text = ""
                    break
            label = next((ln.strip() for ln in license_text.splitlines() if ln.strip()), "unknown")
            prov["license"] = label[:200]
            if commercial_safe and not is_commercial_safe_ud(license_text or label):
                prov["status"] = "skipped: NonCommercial license (commercial_safe=True)"
                records.append(prov)
                continue
            seen = set()
            sents: List[str] = []
            conllu_files = sorted((f for f in files if f.endswith(".conllu")),
                                  key=lambda f: (("train" not in f), f))
            for fn in conllu_files:
                try:
                    conllu = open(os.path.join(d, fn), encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                for s in _parse_conllu_text_lines(conllu, spaceless=spaceless):
                    if s not in seen:
                        seen.add(s); sents.append(s)
                    if len(sents) >= max_sentences:
                        break
                if len(sents) >= max_sentences:
                    break
            prov["count"] = len(sents)
            records.append(prov)
            if sents:
                new_sents.extend(sents)
                break
        added, total = merge_into_corpus(engine_dir, new_sents, root)
        _write_provenance(engine_dir, root, records)
        results[engine_dir] = {"engine": engine_dir, "added": added,
                               "corpus_total": total, "sources": records}
    return results


def ingest_all(max_sentences: int = 400, commercial_safe: bool = True,
               root: Optional[str] = None, ud_archive: Optional[str] = None) -> Dict[str, Dict]:
    if ud_archive is None:
        ud_archive = find_local_ud_archive()
    results = {}
    for engine_dir in sorted(all_sources()):
        try:
            results[engine_dir] = ingest_engine(engine_dir, max_sentences=max_sentences,
                                                commercial_safe=commercial_safe, root=root,
                                                ud_archive=ud_archive)
        except Exception as exc:
            results[engine_dir] = {"engine": engine_dir, "error": f"{type(exc).__name__}: {exc}"}
    return results


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Ingest open-source training data (Tatoeba + UD).")
    ap.add_argument("--engine", help="Engine dir, e.g. Spanish_engine")
    ap.add_argument("--all", action="store_true", help="Ingest for all engines")
    ap.add_argument("--max", type=int, default=400, help="Max sentences per source")
    ap.add_argument("--allow-noncommercial", action="store_true",
                    help="Allow UD NonCommercial treebanks (default: skip)")
    ap.add_argument("--no-tatoeba", action="store_true")
    ap.add_argument("--no-ud", action="store_true")
    ap.add_argument("--ud-archive", help="Path to a local UD treebanks .tgz (offline). "
                                         "Auto-detected in Downloads if omitted.")
    ap.add_argument("--local-ud-only", action="store_true",
                    help="Fast OFFLINE mode: ingest every engine's UD treebank in a single "
                         "tarball pass (no Tatoeba, no network).")
    args = ap.parse_args(argv)

    commercial_safe = not args.allow_noncommercial
    ud_archive = args.ud_archive if args.ud_archive is not None else find_local_ud_archive()
    if ud_archive:
        print(f"Using local UD archive: {ud_archive}")

    if args.local_ud_only:
        res = ingest_all_local_ud(max_sentences=args.max, commercial_safe=commercial_safe,
                                  ud_archive=ud_archive)
        if "error" in res:
            print(f"Error: {res['error']}")
            return 1
        added = sum(r.get("added", 0) for r in res.values())
        got = sum(1 for r in res.values() if r.get("added", 0) > 0)
        print(f"Single-pass local UD ingest: {len(res)} engines, {got} received data, "
              f"{added} new sentences added.")
        return 0

    if args.all:
        res = ingest_all(max_sentences=args.max, commercial_safe=commercial_safe,
                         ud_archive=ud_archive)
        added = sum(r.get("added", 0) for r in res.values())
        print(f"Ingested into {len(res)} engines; {added} new sentences added.")
    elif args.engine:
        r = ingest_engine(args.engine, max_sentences=args.max, commercial_safe=commercial_safe,
                          use_tatoeba=not args.no_tatoeba, use_ud=not args.no_ud,
                          ud_archive=ud_archive)
        print(f"[{args.engine}] added={r['added']} corpus_total={r['corpus_total']}")
        for s in r["sources"]:
            print(f"  - {s.get('source')}: count={s.get('count')} status={s.get('status')} "
                  f"license={s.get('license','')[:40]}")
    else:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
