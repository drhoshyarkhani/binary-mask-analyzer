import sqlite3

import numpy as np
import pytest

from mask_analyzer.core import analyze_array
from mask_analyzer.storage import list_results, save_results


def result():
    return analyze_array(np.ones((2, 3, 4)), np.eye(4))


def test_database_round_trip_has_only_measurements(tmp_path):
    database = tmp_path / "registry.sqlite3"
    save_results(database, "test-run", "synthetic", [result()])
    rows = list_results(database)
    assert len(rows) == 1
    assert rows[0]["voxel_count"] == 24
    assert rows[0]["volume_ml"] == pytest.approx(0.024)
    assert set(rows[0]) == {"run_id", "mask_id", "source_kind", "shape_0", "shape_1",
                          "shape_2", "voxel_count", "voxel_volume_mm3", "volume_ml",
                          "peak_slice", "slice_counts_json"}


def test_repeated_runs_append_without_overwriting(tmp_path):
    database = tmp_path / "registry.sqlite3"
    save_results(database, "run-a", "synthetic", [result()])
    save_results(database, "run-b", "synthetic", [result()])
    assert len(list_results(database)) == 2


def test_duplicate_batch_rolls_back(tmp_path):
    database = tmp_path / "registry.sqlite3"
    save_results(database, "first", "synthetic", [result()])
    with pytest.raises(sqlite3.IntegrityError):
        save_results(database, "duplicate", "synthetic", [result(), result()])
    assert len(list_results(database)) == 1


@pytest.mark.parametrize("run_id, source", [("bad id", "synthetic"), ("ok", "unknown")])
def test_invalid_storage_inputs_rejected(tmp_path, run_id, source):
    with pytest.raises(ValueError):
        save_results(tmp_path / "registry.sqlite3", run_id, source, [result()])
