"""Unit tests for ``full_atlas._vary`` — the deterministic per-column frame
variation that turns one static keyframe into an animatable row.

These lock down the exact regression the function's own comment documents: an
earlier version repeated identical pixels across a row, so Hermes had nothing
to animate and the state looked frozen even though ``validate_atlas`` reported
the row as filled. The guarantee is that, on a real-size detailed cell, every
column of a row renders to distinct pixels while column 0 stays byte-identical
to the approved reference pose.

Note: distinctness is a property of *real-size* cells (192x208). On a tiny or
near-empty cell, the small sub-pixel bob/tilt/scale can round back to identical
pixels — so we test against realistically-sized, detailed cells (a seeded
synthetic one, plus the real committed processed cells when present), matching
how the pipeline actually uses ``_vary``. See AUDIT_REPORT.md F-4.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import full_atlas

REPO = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO / "assets/keyframes/processed"

# The frame counts real Hermes rows use (agent.pet.generate.atlas.ROW_SPECS
# spans small even/odd counts); we cover a representative spread including the
# even counts where a naive same-phase implementation collapsed columns.
FRAME_COUNTS = [1, 2, 3, 4, 6, 8, 12]


def _detailed_cell(w: int = 192, h: int = 208) -> Image.Image:
    """A seeded, real-size, detailed RGBA cell (stand-in for a sprite)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            if 40 < x < 150 and 30 < y < 190 and ((x - 95) ** 2 / 60**2 + (y - 110) ** 2 / 80**2) < 1:
                px[x, y] = ((x * 7) % 256, (y * 5) % 256, (x * y) % 256, 255)
    return im


def _real_cells() -> list[Image.Image]:
    if not PROCESSED_DIR.is_dir():
        return []
    cells = []
    for p in sorted(PROCESSED_DIR.glob("*.png")):
        with Image.open(p) as im:
            cells.append(im.convert("RGBA"))
    return cells


def test_column_zero_is_a_byte_identical_copy() -> None:
    cell = _detailed_cell()
    out = full_atlas._vary(cell, 0, 8)
    assert out.tobytes() == cell.tobytes(), "column 0 must be the untouched reference pose"
    assert out is not cell, "column 0 must be a copy, not the same object"


def test_single_frame_row_returns_copy() -> None:
    cell = _detailed_cell()
    out = full_atlas._vary(cell, 0, 1)
    assert out.tobytes() == cell.tobytes()
    assert out is not cell


@pytest.mark.parametrize("n", FRAME_COUNTS)
def test_output_preserves_cell_size(n: int) -> None:
    cell = _detailed_cell()
    for i in range(n):
        assert full_atlas._vary(cell, i, n).size == cell.size


@pytest.mark.parametrize("n", [c for c in FRAME_COUNTS if c > 1])
def test_all_columns_render_distinct_on_realsize_cell(n: int) -> None:
    """The frozen-row regression guard: every column must differ."""
    cell = _detailed_cell()
    digests = [full_atlas._vary(cell, i, n).tobytes() for i in range(n)]
    assert len(set(digests)) == n, f"row of {n} frames collapsed to duplicate frames"


@pytest.mark.parametrize("n", [c for c in FRAME_COUNTS if c > 1])
def test_distinct_on_real_committed_cells(n: int) -> None:
    """Same guarantee, but against the project's actual processed keyframes."""
    cells = _real_cells()
    if not cells:
        pytest.skip("no processed keyframes committed")
    for cell in cells:
        digests = [full_atlas._vary(cell, i, n).tobytes() for i in range(n)]
        assert len(set(digests)) == n
