from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import numpy as np


@dataclass(frozen=True)
class MaskResult:
    mask_id: str
    shape: tuple[int, int, int]
    voxel_count: int
    voxel_volume_mm3: float
    volume_ml: float
    slice_counts: tuple[int, ...]
    peak_slice: int | None

    def record(self) -> dict:
        return {
            "mask_id": self.mask_id,
            "shape_0": self.shape[0], "shape_1": self.shape[1],
            "shape_2": self.shape[2], "voxel_count": self.voxel_count,
            "voxel_volume_mm3": self.voxel_volume_mm3,
            "volume_ml": self.volume_ml, "peak_slice": self.peak_slice,
            "is_empty": self.voxel_count == 0,
        }


def binary_mask(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    if values.ndim != 3 or values.size == 0:
        raise ValueError("A non-empty 3D array is required.")
    if values.dtype.kind not in "buif" or not np.all(np.isfinite(values)):
        raise ValueError("Mask values must be real, finite numbers.")
    zero = np.isclose(values, 0, atol=1e-6, rtol=0)
    one = np.isclose(values, 1, atol=1e-6, rtol=0)
    if not np.all(zero | one):
        raise ValueError("Mask labels must be within 1e-6 of zero or one.")
    return one.astype(np.uint8)


def analyze_array(values: np.ndarray, affine: np.ndarray,
                  mask_id: str = "mask-0001") -> MaskResult:
    mask = binary_mask(values)
    affine = np.asarray(affine, dtype=float)
    if affine.shape != (4, 4) or not np.all(np.isfinite(affine)):
        raise ValueError("A finite 4 by 4 affine is required.")
    if not np.allclose(affine[3], [0, 0, 0, 1], atol=1e-12, rtol=0):
        raise ValueError("The affine must use homogeneous spatial coordinates.")
    voxel_volume = float(abs(np.linalg.det(affine[:3, :3])))
    if not np.isfinite(voxel_volume) or voxel_volume <= 0:
        raise ValueError("Voxel volume must be positive and finite.")
    count = int(np.count_nonzero(mask))
    slices = tuple(int(value) for value in np.count_nonzero(mask, axis=(1, 2)))
    peak = int(np.argmax(slices)) + 1 if count else None
    return MaskResult(mask_id, tuple(mask.shape), count, voxel_volume,
                      count * voxel_volume / 1000, slices, peak)


def analyze_file(path: str | Path, mask_id: str = "mask-0001") -> MaskResult:
    path = Path(path)
    if not path.name.lower().endswith((".nii", ".nii.gz")):
        raise ValueError("Expected a local NIfTI mask.")
    image = nib.load(path)
    if not isinstance(image, (nib.Nifti1Image, nib.Nifti2Image)):
        raise ValueError("Expected a NIfTI image.")
    if image.header.get_xyzt_units()[0] != "mm":
        raise ValueError("Spatial units must be millimeters.")
    return analyze_array(image.get_fdata(), image.affine, mask_id)


def find_masks(directory: str | Path) -> list[Path]:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError("The local input directory does not exist.")
    paths = sorted(path for path in directory.rglob("*") if path.is_file()
                   and path.name.lower().endswith((".nii", ".nii.gz")))
    if not paths:
        raise ValueError("No NIfTI masks found.")
    return paths
