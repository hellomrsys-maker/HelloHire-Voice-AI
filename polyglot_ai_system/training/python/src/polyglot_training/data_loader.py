# =============================================================================
# training/python/src/polyglot_training/data_loader.py
#
# Training data loader.
#
# Architecture rule (enforced here):
#   The training layer MUST NOT read canonical engine YAML files directly.
#   All access to canonical knowledge-layer files goes exclusively through
#   EngineTrainingAPI (the designated bridge).  This loader therefore accepts
#   either:
#     (a) An instantiated EngineTrainingAPI object (preferred, live bridge), or
#     (b) A list of canonical YAML paths — in which case it instantiates its own
#         EngineTrainingAPI per file and calls api.load() as the single
#         permitted entry point.  No raw open()/yaml.safe_load() calls appear
#         in this file.
#
# Processing pipeline applied to every loaded sample:
#   1. Load approved training_data items via EngineTrainingAPI
#   2. Normalize slot values (whitespace, casing)
#   3. Tokenize via character-level mapping (production: Rust FFI tokenizer)
#   4. Batch with padding and truncation
# =============================================================================

from __future__ import annotations

import random
import logging
from dataclasses import dataclass
from typing import Iterator, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DataBatch:
    """A single training batch."""
    input_ids:      List[List[int]]
    target_ids:     List[List[int]]
    attention_mask: List[List[int]]
    faculty_label:  str   # Which cognitive faculty this batch trains
    batch_size:     int
    seq_len:        int


@dataclass
class TrainingDataset:
    """A dataset produced from one canonical engine training file."""
    name:          str
    samples:       List[dict]
    faculty_label: str
    language:      str = "en"

    def __len__(self) -> int:
        return len(self.samples)


class TrainingDataLoader:
    """
    Loads training data exclusively through the EngineTrainingAPI bridge.

    Enforces the architecture rule:
      - No direct file I/O to canonical YAML knowledge-layer files.
      - Raw dialogue is never used as training data.
      - Every training item must carry review_status: approved (enforced by
        EngineTrainingAPI._load_training_records).

    Construction modes
    ------------------
    Mode A — supply a pre-loaded EngineTrainingAPI instance:
        loader = TrainingDataLoader(api=my_api)

    Mode B — supply file paths; loader creates one API per file:
        loader = TrainingDataLoader(training_file_paths=["path/to/engine.yaml"])

    Both modes produce the same internal sample list.
    """

    def __init__(
        self,
        training_file_paths: Optional[List[str]] = None,
        api: Optional[object] = None,          # EngineTrainingAPI | None
        batch_size: int = 32,
        max_seq_length: int = 512,
        shuffle: bool = True,
        seed: int = 42,
    ):
        self._batch_size     = batch_size
        self._max_seq_length = max_seq_length
        self._shuffle        = shuffle
        self._rng            = random.Random(seed)

        self._datasets: List[TrainingDataset] = []
        self._all_samples: List[dict]         = []

        if api is not None:
            # Mode A: consume records from a pre-loaded bridge
            self._load_from_api(api, source_name="<pre-loaded api>")
        elif training_file_paths:
            # Mode B: create one EngineTrainingAPI per path, load via bridge
            self._load_from_paths(training_file_paths)
        else:
            logger.warning(
                "TrainingDataLoader constructed with neither api nor "
                "training_file_paths — no data will be available."
            )

        logger.info("Total training samples loaded: %d", len(self._all_samples))

    # ------------------------------------------------------------------
    # Internal loading — both routes go through EngineTrainingAPI
    # ------------------------------------------------------------------

    def _load_from_paths(self, paths: List[str]) -> None:
        """
        For each path create an EngineTrainingAPI, call api.load(), then
        delegate to _load_from_api.  This is the ONLY place where a YAML
        path is handed to the bridge; no open() or yaml.safe_load() here.
        """
        # Import here to avoid circular imports at module level
        from polyglot_engine.training_api import EngineTrainingAPI

        for path_str in paths:
            api = EngineTrainingAPI(training_yaml_path=path_str)
            api.load()  # bridge's single permitted file-read entry point
            if not api.is_loaded():
                logger.warning("EngineTrainingAPI failed to load: %s", path_str)
                continue
            # Derive a human-readable source name from the stem of the path
            import pathlib
            source_name = pathlib.Path(path_str).stem
            self._load_from_api(api, source_name=source_name)

    def _load_from_api(self, api: object, source_name: str) -> None:
        """
        Pull approved TrainingRecord objects from a loaded EngineTrainingAPI,
        convert them to the plain-dict sample format used by the batching
        pipeline, and register a TrainingDataset.
        """
        from polyglot_engine.training_api import EngineTrainingAPI

        if not isinstance(api, EngineTrainingAPI):
            logger.error(
                "_load_from_api received non-EngineTrainingAPI object: %s",
                type(api),
            )
            return

        records = api.get_training_records(approved_only=True)
        if not records:
            logger.warning("No approved training records from: %s", source_name)
            return

        # Convert TrainingRecord dataclass instances to plain dicts so that the
        # rest of the batching pipeline stays type-agnostic.
        samples: List[dict] = [r.to_dict() for r in records]

        # Derive language from the first record (all records in one file share
        # the same language by construction).
        language = records[0].language if records else "en"

        dataset = TrainingDataset(
            name=source_name,
            samples=samples,
            faculty_label="general",
            language=language,
        )
        self._datasets.append(dataset)
        self._all_samples.extend(samples)

        logger.info(
            "Loaded %d approved training records from %s (lang=%s)",
            len(samples), source_name, language,
        )

    def _sample_to_token_ids(self, sample: dict) -> tuple[list[int], list[int]]:
        """
        Converts a training sample (TrainingRecord.to_dict() output) to
        input_ids and target_ids.

        Samples loaded via EngineTrainingAPI carry these canonical fields
        (set by TrainingRecord.to_dict()):
            assembled_output  — the fully assembled sentence/utterance
            slot_values       — dict of slot_name → slot_value strings
            component_family  — primary family name (string)
            record_id         — unique identifier

        The input sequence is built from slot_values joined in order.
        The target sequence is the assembled_output.

        Production replacement: swap character-level ord() mapping here
        with a call to the Rust-backed EngineTokenizer via FFI.
        """

        def _pad(ids: list[int], max_len: int) -> tuple[list[int], list[int]]:
            """Pad/truncate ids to max_len; return (ids, attention_mask)."""
            mask = [1] * min(len(ids), max_len) + [0] * max(max_len - len(ids), 0)
            padded = (ids + [0] * max(max_len - len(ids), 0))[:max_len]
            return padded, mask[:max_len]

        # Input: slot values joined in insertion order (Python 3.7+ dict order)
        slot_values: dict = sample.get("slot_values", {})
        input_text = " ".join(str(v) for v in slot_values.values()) if slot_values else sample.get("record_id", "")

        # Target: the fully assembled output string
        target_text: str = sample.get("assembled_output", input_text)

        # Character-level tokenization (production: replace with Rust FFI call)
        raw_input_ids  = [ord(c) % 30000 for c in input_text]
        raw_target_ids = [ord(c) % 30000 for c in target_text]

        input_ids, _input_mask  = _pad(raw_input_ids,  self._max_seq_length)
        target_ids, _target_mask = _pad(raw_target_ids, self._max_seq_length)

        return input_ids, target_ids

    def batches(self, num_batches: Optional[int] = None) -> Iterator[DataBatch]:
        """
        Yields training batches.

        Args:
            num_batches: If set, stops after this many batches.
                         If None, iterates indefinitely (for training loops).

        Yields:
            DataBatch objects.
        """
        if not self._all_samples:
            logger.warning("No training samples available — check training file loading")
            return

        samples = list(self._all_samples)
        batch_count = 0

        while True:
            if self._shuffle:
                self._rng.shuffle(samples)

            for i in range(0, len(samples), self._batch_size):
                batch_samples = samples[i:i + self._batch_size]
                if len(batch_samples) < self._batch_size:
                    # Pad batch with random samples from the same pool
                    extra = self._rng.choices(samples,
                                               k=self._batch_size - len(batch_samples))
                    batch_samples = batch_samples + extra

                # Convert samples to token IDs
                inputs, targets = [], []
                for s in batch_samples:
                    inp, tgt = self._sample_to_token_ids(s)
                    inputs.append(inp)
                    targets.append(tgt)

                masks = [[1 if tok != 0 else 0 for tok in row] for row in inputs]

                yield DataBatch(
                    input_ids=inputs,
                    target_ids=targets,
                    attention_mask=masks,
                    faculty_label="general",
                    batch_size=len(batch_samples),
                    seq_len=self._max_seq_length,
                )

                batch_count += 1
                if num_batches is not None and batch_count >= num_batches:
                    return

    def sample_count(self) -> int:
        return len(self._all_samples)

    def dataset_count(self) -> int:
        return len(self._datasets)
