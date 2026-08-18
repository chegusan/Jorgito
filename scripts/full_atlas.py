"""Full 9-row atlas assembly for the complete Jorgito pet (Phase 4).

Reuses Hermes's own atlas machinery (``agent.pet.generate.atlas``) instead of
reinventing spritesheet geometry: ``ROW_SPECS`` / ``compose_atlas`` /
``validate_atlas`` already define the real 8x9 (1536x1872) Codex atlas shape
and per-state frame counts, and ``mirror_frames`` is Hermes's own documented
mechanism for deriving ``running-left`` from ``running-right`` (atlas.py's own
docstring: "Used to derive running-left from an approved running-right row").

This project has one static pose per state (no keyframed animation), so each
state's single processed 192x208 cell is turned into that row's real frame
count (per ``ROW_SPECS``) via ``_vary()``: a deterministic sine-driven bob +
tilt + breathing-scale applied to a copy of the base cell per column. Naively
repeating the *same* image reference/pixels across a row (an earlier version
of this module did exactly that) produces a row where every cell hashes
identically -- Hermes's renderer then has nothing to animate and the state
looks frozen even though ``validate_atlas()`` reports it as fully filled.
"""

from __future__ import annotations

import math
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


# Amplitude of the deterministic per-column variation. Small on purpose: this
# is a subtle idle-style bob/breathe, not a new hand-drawn animation.
_BOB_PX = 3
_TILT_DEG = 1.5
_SCALE_DELTA = 0.02


def _vary(cell: Image.Image, i: int, n: int) -> Image.Image:
    """Return a distinct copy of *cell* for column *i* of *n*.

    Column 0 stays byte-identical to the base keyframe -- it's the approved
    reference pose. Every other column gets the same deterministic sine-phase
    nudge (vertical bob, slight tilt, slight scale) so a row plays back as a
    gentle breathing/bobbing loop instead of a frozen repeat. Uses NEAREST
    resampling throughout to match ``atlas._fit_to_cell``'s pixel-art-safe
    resample choice -- LANCZOS/BILINEAR would blur the hard pixel-art edges.
    """
    if i == 0 or n <= 1:
        return cell.copy()

    phase = 2 * math.pi * i / n
    dy = round(_BOB_PX * math.sin(phase))
    angle = _TILT_DEG * math.sin(phase)
    scale = 1.0 + _SCALE_DELTA * math.sin(phase)

    w, h = cell.size
    rotated = cell.rotate(angle, resample=Image.Resampling.NEAREST, fillcolor=(0, 0, 0, 0))
    sw, sh = max(1, round(w * scale)), max(1, round(h * scale))
    scaled = rotated.resize((sw, sh), Image.Resampling.NEAREST) if (sw, sh) != (w, h) else rotated

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(scaled, ((w - sw) // 2, (h - sh) // 2 + dy))
    return out


def build_frames_by_state() -> dict[str, list[Image.Image]]:
    """Each state's base pose expanded into that row's real frame count.

    Column 0 is the untouched, approved keyframe; columns 1..n-1 are
    deterministic variations (``_vary``) of a *copy* of it -- never the same
    object/pixels repeated, so the row actually animates on playback.
    """
    row_counts = {state: count for state, _row, count in atlas.ROW_SPECS}

    cells_by_row: dict[str, Image.Image] = {
        row: load_processed(processed) for processed, row in PROCESSED_TO_ROW.items()
    }
    cells_by_row["running-left"] = derive_running_left()

    return {
        row: [_vary(cell, i, row_counts[row]) for i in range(row_counts[row])]
        for row, cell in cells_by_row.items()
    }


def build_atlas_image() -> Image.Image:
    """Compose the full 1536x1872 (8x9) atlas via Hermes's own compose_atlas()."""
    return atlas.compose_atlas(build_frames_by_state())


def validate(atlas_image: Image.Image) -> dict:
    """Run Hermes's own structural validator (not a project-invented one)."""
    return atlas.validate_atlas(atlas_image)
