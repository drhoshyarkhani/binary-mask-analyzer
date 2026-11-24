"""Deterministic geometric fixtures; no external data or randomness."""
import gzip
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np

GENERATOR_VERSION = "1"
# Counts come from integer box dimensions, independently of the analyzer.
SPECS = (
    ("empty", (), (1, 1, 1), 0, False),
    ("single_voxel", ((3, 4, 5, 1, 1, 1),), (1, 1, 1), 1, False),
    ("box", ((2, 3, 4, 4, 5, 6),), (1, 1, 1), 120, False),
    ("anisotropic_box", ((2, 3, 4, 3, 4, 5),), (2, 3, 4), 60, False),
    ("two_boxes", ((1, 1, 1, 2, 2, 2), (12, 12, 12, 3, 3, 3)),
     (1, 1, 1), 35, False),
    ("offset_box", ((10, 7, 3, 7, 3, 2),), (0.5, 0.5, 2), 42, False),
    ("rotated_grid", ((4, 5, 6, 2, 3, 4),), (1, 2, 3), 24, True),
)


def generate(directory: str | Path) -> list[dict]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "manifest.json"
    names = [f"synthetic-{i:04d}.nii.gz" for i in range(1, len(SPECS) + 1)]
    if manifest_path.exists() or any((directory / name).exists() for name in names):
        raise ValueError("Synthetic destinations already exist; choose a new directory.")
    records = []
    for index, (label, boxes, spacing, expected_count, rotated) in enumerate(SPECS, 1):
        mask = np.zeros((24, 24, 24), dtype=np.uint8)
        for x, y, z, nx, ny, nz in boxes:
            mask[x:x+nx, y:y+ny, z:z+nz] = 1
        affine = np.diag([*spacing, 1.0])
        if rotated:
            rotation = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
            affine[:3, :3] = rotation @ affine[:3, :3]
        image = nib.Nifti1Image(mask, affine)
        image.header.set_xyzt_units("mm")
        image.header["descrip"] = b"PROCEDURAL_SYNTHETIC_V1"
        payload = gzip.compress(image.to_bytes(), mtime=0)
        name = names[index - 1]
        (directory / name).write_bytes(payload)
        voxel_volume = float(spacing[0] * spacing[1] * spacing[2])
        records.append({
            "mask_id": f"synthetic-{index:04d}", "file": name,
            "geometry": label, "boxes_xyz_size": [list(box) for box in boxes],
            "spacing_mm": list(spacing), "rotated_grid": rotated,
            "expected_voxel_count": expected_count,
            "expected_voxel_volume_mm3": voxel_volume,
            "expected_volume_ml": expected_count * voxel_volume / 1000,
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "origin": "Integer-indexed geometric boxes defined in bundled source code",
        "contains_human_data": False, "external_dataset_inputs": [],
        "shape": [24, 24, 24], "cases": records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return records
