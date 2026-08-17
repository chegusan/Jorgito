"""Full 9-row atlas assembly for the complete Jorgito pet (Phase 4).

Reuses Hermes's own atlas machinery (``agent.pet.generate.atlas``) instead of
reinventing spritesheet geometry: ``ROW_SPECS`` / ``compose_atlas`` /
``validate_atlas`` already define the real 8x9 (1536x1872) Codex atlas shape
and per-state frame counts, and ``mirror_frames`` is Hermes's own documented
mechanism for deriving ``running-left`` from ``running-right`` (atlas.py's own
docstring: "Used to derive running-left from an approved running-right row").

This project has one static pose per state (no animation), so each state's
single processed 192x208 cell is repeated across that row's real frame count
(per ``ROW_SPECS``) -- same "steady repeat plays back as held still" approach
``scripts/build_phase1_test_pet.py`` used for a 3-state subset in Phase 1.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet.generate import atlas  # noqa: E402
from PIL import Image  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO / "assets/keyframes/processed"

# Our processed-keyframe filename stem (Phase 1 / Phase 3 naming) -> the
# agent.pet.generate.atlas.ROW_SPECS row name it fills. Matches the Jorgito
# semantic mapping table in docs/03_INTERFACES_AND_CONTRACTS.md exactly.
PROCESSED_TO_ROW: dict[str, str] = {
    "idle": "idle",
    "running-right": "running-right",
    "wave": "waving",
    "jump": "jumping",
    "failed": "failed",
    "waiting": "waiting",
    "run": "running",
    "review": "review",
}


def load_processed(state: str) -> Image.Image:
    """Load an already chroma-keyed + fit-to-cell 192x208 processed keyframe."""
    path = PROCESSED_DIR / f"{state}.png"
    with Image.open(path) as im:
        return im.convert("RGBA")


def derive_running_left() -> Image.Image:
    """``running-left`` = horizontal mirror of ``running-right``.

    Uses ``atlas.mirror_frames`` (Hermes's own primitive for exactly this,
    per its docstring) rather than reimplementing a Pillow flip.
    """
    right = load_processed("running-right")
    mirrored = atlas.mirror_frames([right])
    return mirrored[0]


def build_frames_by_state() -> dict[str, list[Image.Image]]:
    """One state's single pose repeated across that row's real frame count."""
    row_counts = {state: count for state, _row, count in atlas.ROW_SPECS}

    cells_by_row: dict[str, Image.Image] = {
        row: load_processed(processed) for processed, row in PROCESSED_TO_ROW.items()
    }
    cells_by_row["running-left"] = derive_running_left()

    return {row: [cell] * row_counts[row] for row, cell in cells_by_row.items()}


def build_atlas_image() -> Image.Image:
    """Compose the full 1536x1872 (8x9) atlas via Hermes's own compose_atlas()."""
    return atlas.compose_atlas(build_frames_by_state())


def validate(atlas_image: Image.Image) -> dict:
    """Run Hermes's own structural validator (not a project-invented one)."""
    return atlas.validate_atlas(atlas_image)
