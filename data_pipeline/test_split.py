"""
test_split.py - automatic checks that the train / validation / test split is fair.

The most important rule of the project: a person whose recordings are used for training
must never appear in validation or test data. These tests fail loudly if that ever breaks.

Run from the repository folder:
    python -m pytest data_pipeline/test_split.py
(The last test needs the built data in data/derived/; it is skipped if it is missing.)
"""

import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPLIT_FILE = ROOT / "data_pipeline" / "split.json"
DERIVED = ROOT / "data" / "derived"


def load_split():
    with open(SPLIT_FILE, encoding="utf-8") as f:
        return json.load(f)


def test_no_person_in_two_splits():
    split = load_split()
    train, val, test = set(split["train"]), set(split["val"]), set(split["test"])
    assert not train & val, "people in both train and val: %s" % sorted(train & val)
    assert not train & test, "people in both train and test: %s" % sorted(train & test)
    assert not val & test, "people in both val and test: %s" % sorted(val & test)


def test_everyone_is_in_a_split():
    split = load_split()
    total = sum(len(ids) for ids in split.values())
    # TremorDB describes 16 people, but subject v3 has no recordings in the dataset, so 15.
    assert total == 469 + 15, "expected 484 people (469 PADS + 15 TremorDB), got %d" % total


@pytest.mark.parametrize("kind", ["detector", "corrector", "detector_continuous",
                                  "detector_x0.5", "detector_x2", "corrector_x0.5", "corrector_x2"])
def test_built_examples_only_use_their_own_split(kind):
    """Also checks the extra sets (pause-free; half and double tremor size)."""
    split = load_split()
    base, _, extra = kind.partition("_")
    for name, ids in split.items():
        path = DERIVED / (f"{base}_{name}_{extra}.npz" if extra else f"{base}_{name}.npz")
        if not path.exists():
            pytest.skip("built data not found; run data_pipeline/build_dataset.py first")
        used = set(np.load(path)["subject"]) - {"synthetic"}
        outside = used - set(ids)
        assert not outside, "%s %s uses people from another split: %s" % (kind, name, sorted(outside)[:5])
