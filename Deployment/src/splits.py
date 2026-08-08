"""Deterministic train/valid partition, persisted for reproducibility (SPEC §10 step 5).

The provided ``dev`` files are evaluation-only and are never touched here. The
``valid`` split is carved from ``train`` with a seeded shuffle over content
``uid``s (``config.SEED``), and the chosen valid uids are persisted so a re-run
reproduces the exact partition (plan §4).

Two guards enforce the project's dev-leak rule (STATUS, plan §0 #1):
- ``carve_valid`` asserts train ∩ valid = ∅ by construction.
- ``assert_no_dev_leak`` asserts no training uid appears in dev — a genuine
  *content* check (uid = task + db + input + gold), not a filename coincidence.
"""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path

from . import config
from .loader import Example

log = logging.getLogger(__name__)


def _valid_uids_path(name: str) -> Path:
    return config.SPLITS_DIR / f"{name}_valid_uids.json"


def carve_valid(
    examples: list[Example],
    name: str,
    valid_fraction: float | None = None,
    seed: int | None = None,
) -> tuple[list[Example], list[Example]]:
    """Split ``examples`` into (train, valid) deterministically and persist it.

    ``name`` labels the persisted file (e.g. ``"spider"``, ``"sql2nosql"``). If a
    persisted valid-uid set already exists it is reused verbatim; otherwise the
    partition is computed from a seeded shuffle and saved.
    """
    if valid_fraction is None:
        valid_fraction = config.CONFIG.split.valid_fraction
    if seed is None:
        seed = config.SEED

    config.ensure_dirs()
    path = _valid_uids_path(name)

    uids = [e.uid for e in examples]
    unique = set(uids)
    if len(unique) != len(uids):
        log.warning("%s: %d duplicate uids among %d examples", name, len(uids) - len(unique), len(uids))

    if path.exists():
        valid_uids = set(json.loads(path.read_text(encoding="utf-8")))
        log.info("%s: reusing persisted valid split (%d uids) from %s", name, len(valid_uids), path)
    else:
        ordered = sorted(unique)  # stable regardless of input order
        rng = random.Random(seed)
        rng.shuffle(ordered)
        n_valid = round(len(ordered) * valid_fraction)
        valid_uids = set(ordered[:n_valid])
        path.write_text(json.dumps(sorted(valid_uids)), encoding="utf-8")
        log.info(
            "%s: carved valid=%d / train=%d (fraction=%.2f, seed=%d) -> %s",
            name, len(valid_uids), len(unique) - len(valid_uids), valid_fraction, seed, path,
        )

    train = [e for e in examples if e.uid not in valid_uids]
    valid = [e for e in examples if e.uid in valid_uids]

    train_uids = {e.uid for e in train}
    valid_only = {e.uid for e in valid}
    assert train_uids.isdisjoint(valid_only), f"{name}: train/valid uid overlap"
    return train, valid


def assert_no_dev_leak(train_examples: list[Example], dev_examples: list[Example]) -> None:
    """Raise if any training uid also appears in dev (content-level leak check)."""
    train_uids = {e.uid for e in train_examples}
    dev_uids = {e.uid for e in dev_examples}
    overlap = train_uids & dev_uids
    if overlap:
        raise AssertionError(
            f"dev leak: {len(overlap)} example(s) appear in both train and dev "
            f"(e.g. {sorted(overlap)[:3]})"
        )
