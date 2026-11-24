import hashlib
import json

import pytest

from mask_analyzer.core import analyze_file
from mask_analyzer.synthetic import generate


def test_procedural_examples_match_independent_box_counts(tmp_path):
    records = generate(tmp_path)
    assert len(records) == 7
    assert [row["expected_voxel_count"] for row in records] == [0, 1, 120, 60, 35, 42, 24]
    for row in records:
        result = analyze_file(tmp_path / row["file"], row["mask_id"])
        assert result.voxel_count == row["expected_voxel_count"]
        assert result.voxel_volume_mm3 == pytest.approx(row["expected_voxel_volume_mm3"])
        assert result.volume_ml == pytest.approx(row["expected_volume_ml"])
        assert hashlib.sha256((tmp_path / row["file"]).read_bytes()).hexdigest() == row["sha256"]
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["contains_human_data"] is False
    assert manifest["external_dataset_inputs"] == []


def test_generator_repeats_geometry_and_bytes_on_same_runtime(tmp_path):
    first = generate(tmp_path / "first")
    second = generate(tmp_path / "second")
    assert first == second


def test_generator_does_not_overwrite_existing_samples(tmp_path):
    generate(tmp_path)
    with pytest.raises(ValueError, match="already exist"):
        generate(tmp_path)
