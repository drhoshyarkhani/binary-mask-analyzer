from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .core import MaskResult


def write_reports(results: list[MaskResult], directory: str | Path) -> dict:
    if not results:
        raise ValueError("At least one analysis result is required.")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame([item.record() for item in results])
    volumes = table["volume_ml"]
    summary = {
        "mask_count": len(results), "empty_mask_count": int(table["is_empty"].sum()),
        "mean_volume_ml": float(volumes.mean()),
        "median_volume_ml": float(volumes.median()),
        "min_volume_ml": float(volumes.min()), "max_volume_ml": float(volumes.max()),
    }
    table.to_csv(directory / "measurements.csv", index=False)
    pd.DataFrame([summary]).to_csv(directory / "summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(table["mask_id"], volumes, color="steelblue")
    ax.set(xlabel="Generated mask identifier", ylabel="Mask volume (mL)",
           title="Binary mask volumes")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(directory / "volumes.png", dpi=160)
    plt.close(fig)
    representative = max(results, key=lambda item: item.voxel_count)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(1, len(representative.slice_counts) + 1), representative.slice_counts)
    ax.set(xlabel="Array-axis-0 slice number (one-based)", ylabel="Foreground voxel count",
           title=f"Slice profile: {representative.mask_id}")
    fig.tight_layout()
    fig.savefig(directory / "slice_profile.png", dpi=160)
    plt.close(fig)
    return summary
