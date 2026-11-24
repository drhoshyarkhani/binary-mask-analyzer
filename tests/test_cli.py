import csv
import json
import os
from pathlib import Path
import subprocess
import sys

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def command(*args):
    return subprocess.run([sys.executable, "-m", "mask_analyzer", *map(str, args)],
                          cwd=ROOT, env=os.environ.copy(), capture_output=True,
                          text=True, timeout=90)


def test_demo_and_database_listing(tmp_path):
    output = tmp_path / "demo"
    completed = command("demo", "--output", output)
    assert completed.returncode == 0, completed.stderr
    assert "Analyzed 7 masks; 1 empty." in completed.stdout
    assert command("list", output / "registry.sqlite3").returncode == 0
    summary = next(csv.DictReader((output / "summary.csv").open()))
    assert int(summary["mask_count"]) == 7
    assert int(summary["empty_mask_count"]) == 1
    for name in ("volumes.png", "slice_profile.png"):
        assert (output / name).stat().st_size > 0


def test_private_input_names_are_not_persisted_or_echoed(tmp_path):
    marker = "private-input-marker"
    image = nib.Nifti1Image(np.ones((2, 2, 2), dtype=np.uint8), np.eye(4))
    image.header.set_xyzt_units("mm")
    path = tmp_path / (marker + ".nii.gz")
    nib.save(image, path)
    output = tmp_path / "output"
    completed = command("analyze", path, "--output", output)
    assert completed.returncode == 0, completed.stderr
    assert marker not in completed.stdout + completed.stderr
    for name in ("measurements.csv", "summary.csv"):
        assert marker not in (output / name).read_text()
        assert str(tmp_path) not in (output / name).read_text()
    assert marker.encode() not in (output / "registry.sqlite3").read_bytes()


def test_invalid_file_fails_without_echoing_private_path(tmp_path):
    completed = command("analyze", tmp_path / "private-input-marker.nii.gz")
    assert completed.returncode == 2
    assert "private-input-marker" not in completed.stdout + completed.stderr
    assert str(tmp_path) not in completed.stdout + completed.stderr


def test_batch_accepts_generic_names(tmp_path):
    directory = tmp_path / "masks"
    directory.mkdir()
    for index in range(2):
        image = nib.Nifti1Image(np.full((2, 2, 2), index, dtype=np.uint8), np.eye(4))
        image.header.set_xyzt_units("mm")
        nib.save(image, directory / f"example{index}.nii.gz")
    completed = command("batch", directory, "--output", tmp_path / "reports")
    assert completed.returncode == 0, completed.stderr
    assert "Analyzed 2 masks; 1 empty." in completed.stdout
