"""Unit tests for ``keyframe_processing.build_contact_sheet`` geometry.

The contact sheet is the artifact humans inspect at every visual gate, so its
layout math (per-cell scale, padding, label strip) must stay correct. These
assert the sheet's dimensions follow the documented formula purely from the
module's own constants and the stubbed cell size (see tests/conftest.py), with
no dependency on the real Hermes atlas dimensions.
"""

from __future__ import annotations

from PIL import Image

import keyframe_processing as kp
from conftest import STUB_CELL_WIDTH, STUB_CELL_HEIGHT


def _cells(states: list[str]) -> dict[str, Image.Image]:
    # Any size — build_contact_sheet resizes each to the target cell box.
    return {s: Image.new("RGBA", (5, 5), (i * 10, 0, 0, 255)) for i, s in enumerate(states)}


def _expected_size(n: int) -> tuple[int, int]:
    cell_w = STUB_CELL_WIDTH * kp.SCALE
    cell_h = STUB_CELL_HEIGHT * kp.SCALE
    sheet_w = kp.PADDING * (n + 1) + cell_w * n
    sheet_h = kp.PADDING * 2 + cell_h + kp.LABEL_HEIGHT
    return sheet_w, sheet_h


def test_single_cell_sheet_dimensions() -> None:
    states = ["idle"]
    sheet = kp.build_contact_sheet(_cells(states), states)
    assert sheet.mode == "RGBA"
    assert sheet.size == _expected_size(len(states))


def test_multi_cell_sheet_dimensions() -> None:
    states = ["idle", "review", "run", "waiting", "failed"]
    sheet = kp.build_contact_sheet(_cells(states), states)
    assert sheet.size == _expected_size(len(states))


def test_width_grows_linearly_with_cell_count() -> None:
    one = kp.build_contact_sheet(_cells(["a"]), ["a"]).width
    two = kp.build_contact_sheet(_cells(["a", "b"]), ["a", "b"]).width
    per_cell = STUB_CELL_WIDTH * kp.SCALE + kp.PADDING
    assert two - one == per_cell
