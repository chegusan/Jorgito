"""Final 9-row atlas assembly (Phase Final) -- reconciliation, not generation.

Every row here was already generated and visually approved in an earlier
branch/PR. This script does zero image generation and zero API calls: it
crops each state's already-composited, already-``validate_atlas()``-passed
cells out of that row's own source atlas fragment, then re-packs all nine
into one final atlas via Hermes's real, unmodified
``agent.pet.generate.atlas.compose_atlas()``.

Row provenance (state -> source file -> branch/commit/PR):

    idle           <- assets/keyframes/atlas_full.png       (row 0)  phase-4-full-atlas @ 7353a27 (PR #3)
    running        <- assets/keyframes/atlas_full.png       (row 7)  phase-4-full-atlas @ 7353a27 (PR #3)   ["run" state]
    running-right  <- assets/keyframes/running-right_row_atlas_fragment.png (row 1)  phase2b-pose-sequence-running-right @ 427c804 (PR #8)
    running-left   <- assets/keyframes/running-left_row_atlas_fragment.png  (row 2)  phase2b-pose-sequence-running-right @ 427c804 (PR #8)
    waving         <- assets/keyframes/waving_row_atlas_fragment.png        (row 3)  phase2b-pose-sequence-wave @ 2ce096a (PR #7, merged into #8 chain)
    jumping        <- assets/keyframes/jumping_row_atlas_fragment.png       (row 4)  phase2b-pose-sequence-jump @ 0c4432f (PR #5, cherry-picked)
    failed         <- assets/keyframes/failed_row_atlas_fragment.png        (row 5)  phase2b-fix-failed-chromakey @ fc4678f (PR #6, merged into #8 chain)
    waiting        <- assets/keyframes/waiting_row_atlas_fragment.png       (row 6)  phase2b-hatch-pet-regen @ fd615f1 (merged into #8 chain)
    review         <- assets/keyframes/review_row_atlas_fragment.png        (row 8)  phase2b-hatch-pet-regen @ a7d9006 (merged into #8 chain)

Each ``*_row_atlas_fragment.png`` is itself a full 1536x1872 ``compose_atlas()``
output with only its own row filled (the other 8 rows fully transparent) --
that is the contract ``state_row.py`` / ``full_atlas.py`` already produce, so
cropping the row's own band out of its own fragment recovers the exact
192x208 cells that were already validated for that row, byte-for-byte.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet.generate import atlas  # noqa: E402
from PIL import Image  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
KEYFRAMES_DIR = REPO / "assets/keyframes"

CELL_W = atlas.CELL_WIDTH
CELL_H = atlas.CELL_HEIGHT

# state -> (source file, row index in that source atlas)
ROW_SOURCES: dict[str, tuple[str, int]] = {
    "idle": ("atlas_full.png", 0),
    "running-right": ("running-right_row_atlas_fragment.png", 1),
    "running-left": ("running-left_row_atlas_fragment.png", 2),
    "waving": ("waving_row_atlas_fragment.png", 3),
    "jumping": ("jumping_row_atlas_fragment.png", 4),
    "failed": ("failed_row_atlas_fragment.png", 5),
    "waiting": ("waiting_row_atlas_fragment.png", 6),
    "running": ("atlas_full.png", 7),
    "review": ("review_row_atlas_fragment.png", 8),
}


def _crop_row(source_name: str, row: int, count: int) -> list:
    path = KEYFRAMES_DIR / source_name
    with Image.open(path) as opened:
        source = opened.convert("RGBA")
    top = row * CELL_H
    frames = []
    for col in range(count):
        left = col * CELL_W
        cell = source.crop((left, top, left + CELL_W, top + CELL_H))
        frames.append(cell)
    return frames


def build_frames_by_state() -> dict[str, list]:
    frames_by_state: dict[str, list] = {}
    for state, row, count in atlas.ROW_SPECS:
        source_name, source_row = ROW_SOURCES[state]
        frames_by_state[state] = _crop_row(source_name, source_row, count)
    return frames_by_state


def _row_hashes(frames: list) -> list[str]:
    return [hashlib.sha256(f.tobytes()).hexdigest()[:16] for f in frames]


def build_and_validate() -> tuple[Image.Image, dict, dict[str, list]]:
    frames_by_state = build_frames_by_state()
    final_atlas = atlas.compose_atlas(frames_by_state)
    validation = atlas.validate_atlas(final_atlas)

    per_row: dict[str, dict] = {}
    for state, row, count in atlas.ROW_SPECS:
        frames = frames_by_state[state]
        hashes = _row_hashes(frames)
        source_name, source_row = ROW_SOURCES[state]
        per_row[state] = {
            "row": row,
            "count": count,
            "source": source_name,
            "source_row": source_row,
            "hashes": hashes,
            "unique_hash_count": len(set(hashes)),
            "unique_within_row": len(set(hashes)) == len(hashes),
        }

    report = {
        "validate_atlas": validation,
        "rows": per_row,
        "all_rows_unique": all(r["unique_within_row"] for r in per_row.values()),
        "states_filled": len(validation.get("filled_states", [])),
    }
    return final_atlas, report, frames_by_state


def main() -> None:
    final_atlas, report, _frames_by_state = build_and_validate()

    out_png = KEYFRAMES_DIR / "atlas_final.png"
    final_atlas.save(out_png)

    out_webp = KEYFRAMES_DIR / "atlas_final.webp"
    out_webp.write_bytes(atlas.atlas_to_webp_bytes(final_atlas))

    out_report = KEYFRAMES_DIR / "atlas_final_report.json"
    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    ok = report["validate_atlas"]["ok"]
    filled = report["states_filled"]
    all_unique = report["all_rows_unique"]
    print(f"validate_atlas(): ok={ok} filled_states={filled}/9")
    print(f"all rows internally unique-hash: {all_unique}")
    if report["validate_atlas"]["errors"]:
        print("ERRORS:", report["validate_atlas"]["errors"], file=sys.stderr)
    for state, row_info in report["rows"].items():
        print(f"  {state:16s} row={row_info['row']} count={row_info['count']} "
              f"unique={row_info['unique_hash_count']}/{row_info['count']} "
              f"source={row_info['source']}")

    if not ok or not all_unique or filled != 9:
        print("FAILED final atlas validation.", file=sys.stderr)
        sys.exit(1)

    print(f"\nWrote {out_png}")
    print(f"Wrote {out_webp}")
    print(f"Wrote {out_report}")


if __name__ == "__main__":
    main()
