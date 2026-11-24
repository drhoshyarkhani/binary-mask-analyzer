import nibabel as nib
import numpy as np
import pytest

from mask_analyzer.core import analyze_array, analyze_file, binary_mask, find_masks


def test_box_volume_and_first_peak():
    mask = np.zeros((8, 8, 8), dtype=np.uint8)
    mask[2:6, 1:6, 1:7] = 1
    result = analyze_array(mask, np.diag([2, 3, 4, 1]))
    assert result.voxel_count == 120
    assert result.volume_ml == pytest.approx(2.88)
    assert result.peak_slice == 3
    assert sum(result.slice_counts) == result.voxel_count


def test_empty_foreground_has_no_peak():
    result = analyze_array(np.zeros((2, 3, 4)), np.eye(4))
    assert result.voxel_count == 0
    assert result.volume_ml == 0
    assert result.peak_slice is None


@pytest.mark.parametrize("values", [
    np.zeros((2, 3)), np.zeros((2, 0, 3)), np.array([[[0.5]]]),
    np.array([[[2]]]), np.array([[[np.nan]]]), np.array([[[np.inf]]]),
    np.array([[[1.0 + 2e-6]]]), np.array([[[1j]]]), np.array([[["1"]]]),
])
def test_invalid_masks_rejected(values):
    with pytest.raises(ValueError):
        binary_mask(values)


def test_roundoff_is_normalized_without_changing_input():
    values = np.array([[[5e-8, 1 - 5e-8]]])
    original = values.copy()
    np.testing.assert_array_equal(binary_mask(values), [[[0, 1]]])
    np.testing.assert_array_equal(values, original)


@pytest.mark.parametrize("affine", [np.eye(3), np.zeros((4, 4)),
                                     np.full((4, 4), np.nan), np.ones((4, 4))])
def test_invalid_geometry_rejected(affine):
    with pytest.raises(ValueError):
        analyze_array(np.zeros((2, 2, 2)), affine)


def test_reflected_and_sheared_grid_uses_determinant():
    affine = np.array([[-2., 1., 0., 0.], [0., 3., 0., 0.],
                       [0., 0., 4., 0.], [0., 0., 0., 1.]])
    result = analyze_array(np.ones((2, 2, 2)), affine)
    assert result.voxel_volume_mm3 == pytest.approx(24)
    assert result.volume_ml == pytest.approx(0.192)


def test_scaled_file_is_read_as_binary(tmp_path):
    image = nib.Nifti1Image(np.array([[[0, 10]]], dtype=np.int16), np.eye(4))
    image.header.set_xyzt_units("mm")
    image.header.set_slope_inter(0.1, 0.0)
    path = tmp_path / "scaled.nii.gz"
    nib.save(image, path)
    result = analyze_file(path)
    assert result.voxel_count == 1
    assert result.volume_ml == pytest.approx(0.001)


def test_unknown_units_rejected(tmp_path):
    path = tmp_path / "unknown.nii.gz"
    nib.save(nib.Nifti1Image(np.zeros((2, 2, 2), dtype=np.uint8), np.eye(4)), path)
    with pytest.raises(ValueError, match="millimeters"):
        analyze_file(path)


def test_generic_file_discovery(tmp_path):
    for name in ("anything.nii", "another.nii.gz", "notes.txt"):
        (tmp_path / name).write_text("")
    assert [path.name for path in find_masks(tmp_path)] == ["another.nii.gz", "anything.nii"]


def test_empty_directory_rejected(tmp_path):
    with pytest.raises(ValueError):
        find_masks(tmp_path)
