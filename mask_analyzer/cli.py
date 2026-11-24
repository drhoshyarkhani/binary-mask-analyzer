import argparse
from pathlib import Path
import sqlite3
import sys
import uuid

import nibabel as nib

from .core import analyze_file, find_masks
from .reporting import write_reports
from .storage import list_results, save_results
from .synthetic import generate


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local binary 3D mask analysis.")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Generate and analyze procedural synthetic masks.")
    demo.add_argument("--output", type=Path, default=Path("results/demo"))
    one = commands.add_parser("analyze", help="Analyze an authorized local binary mask.")
    one.add_argument("mask", type=Path)
    one.add_argument("--output", type=Path, default=Path("results/local"))
    batch = commands.add_parser("batch", help="Analyze a local directory containing only masks.")
    batch.add_argument("directory", type=Path)
    batch.add_argument("--output", type=Path, default=Path("results/local"))
    listing = commands.add_parser("list", help="Read measurements from a local SQLite database.")
    listing.add_argument("database", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        if args.command == "list":
            for row in list_results(args.database):
                print(row["run_id"], row["mask_id"], f"{row['volume_ml']:.6f} mL")
            return 0
        run_id = uuid.uuid4().hex
        if args.command == "demo":
            entries = generate(args.output / "synthetic" / run_id)
            paths = [args.output / "synthetic" / run_id / item["file"] for item in entries]
            identifiers = [item["mask_id"] for item in entries]
            source_kind = "synthetic"
        else:
            paths = [args.mask] if args.command == "analyze" else find_masks(args.directory)
            identifiers = [f"mask-{index:04d}" for index in range(1, len(paths) + 1)]
            source_kind = "user_input"
        results = [analyze_file(path, identifier) for path, identifier in zip(paths, identifiers)]
        args.output.mkdir(parents=True, exist_ok=True)
        save_results(args.output / "registry.sqlite3", run_id, source_kind, results)
        summary = write_reports(results, args.output)
        print(f"Analyzed {summary['mask_count']} masks; {summary['empty_mask_count']} empty.")
        print(f"Mean volume: {summary['mean_volume_ml']:.6f} mL")
        print("Saved registry.sqlite3, measurements.csv, summary.csv, volumes.png, slice_profile.png")
        return 0
    except (OSError, ValueError, sqlite3.Error, nib.filebasedimages.ImageFileError):
        print("Input or local operation rejected. Check mask labels, dimensions, units, and file permissions.", file=sys.stderr)
        return 2
