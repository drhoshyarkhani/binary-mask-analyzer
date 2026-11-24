from contextlib import closing
from pathlib import Path
import json
import re
import sqlite3

from .core import MaskResult

_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_SCHEMA = """CREATE TABLE IF NOT EXISTS analyses (
    run_id TEXT NOT NULL, mask_id TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK(source_kind IN ('synthetic', 'user_input')),
    shape_0 INTEGER NOT NULL, shape_1 INTEGER NOT NULL, shape_2 INTEGER NOT NULL,
    voxel_count INTEGER NOT NULL CHECK(voxel_count >= 0),
    voxel_volume_mm3 REAL NOT NULL CHECK(voxel_volume_mm3 > 0),
    volume_ml REAL NOT NULL CHECK(volume_ml >= 0),
    peak_slice INTEGER, slice_counts_json TEXT NOT NULL,
    PRIMARY KEY (run_id, mask_id)
)"""


def save_results(database: str | Path, run_id: str, source_kind: str,
                 results: list[MaskResult]) -> None:
    if not _ID.fullmatch(run_id) or source_kind not in {"synthetic", "user_input"}:
        raise ValueError("Invalid run identifier or source kind.")
    if not results or any(not _ID.fullmatch(item.mask_id) for item in results):
        raise ValueError("Results require non-empty, valid generated identifiers.")
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as connection:
        with connection:
            connection.execute(_SCHEMA)
            connection.executemany(
                "INSERT INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(run_id, item.mask_id, source_kind, *item.shape,
                  item.voxel_count, item.voxel_volume_mm3, item.volume_ml,
                  item.peak_slice, json.dumps(item.slice_counts)) for item in results],
            )


def list_results(database: str | Path) -> list[dict]:
    database = Path(database)
    if not database.is_file():
        raise ValueError("The local results database does not exist.")
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM analyses ORDER BY run_id, mask_id"
        ).fetchall()
    return [dict(row) for row in rows]
