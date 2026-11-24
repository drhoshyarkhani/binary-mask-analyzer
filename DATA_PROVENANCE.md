# Procedural data provenance

The bundled collection was generated specifically for this project by the
source file `mask_analyzer/synthetic.py`. No external dataset is used as an
input to the generator. All masks start as zero-filled 24 × 24 × 24 arrays.
Integer-defined rectangular regions are set to one. One case remains all zero.
Spacing and one 90-degree grid rotation are explicitly specified in source.

The foreground counts are derived analytically from box dimensions:
0; 1; 4×5×6=120; 3×4×5=60; 2×2×2+3×3×3=35;
7×3×2=42; and 2×3×4=24. The two boxes do not overlap.
Expected physical volumes use the specified spacing products, independently
of the analyzer's determinant calculation.

Every image is labeled `PROCEDURAL_SYNTHETIC_V1` in its NIfTI description.
The manifest records the geometry, expected measurements, and SHA-256 of each
produced compressed file. No random seed, learned model, person, photograph,
medical acquisition, or external pixel/voxel array is involved.

Geometry and measurements repeat deterministically. Exact compressed bytes
can depend on writer/compressor versions; manifest hashes describe the actual
files produced in that particular generation.

The demonstration database and plots are computed solely from these seven
masks by the included analyzer. The examples are for testing and teaching,
not a clinical dataset or a substitute for evaluation on real-world data.
