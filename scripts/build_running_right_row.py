"""Thin per-state runner: derive the ``running-right`` row as a mirror.

Addendum #8: the real generated pose-sequence poses rendered LEFTWARD-facing
despite a rightward-facing prompt (Phase 2B addendum #7's visual caveat), so
the human decided (zero-cost) to relabel that already-generated, already-
validated row as ``running-left`` (see ``scripts/build_running_left_row.py``)
and derive ``running-right`` from it as a horizontal mirror instead of
spending more API budget on a retry.

Uses Hermes's own, unmodified ``atlas.mirror_frames()`` -- the same
primitive ``phase-4-full-atlas`` used to derive ``running-left`` from an
approved ``running-right`` row, applied here in the reverse direction (see
``scripts/state_row.build_mirrored_row``'s docstring). NOT a whole-strip
reverse: each of the 8 frames is flipped in place, so ``running-right``
plays back with the exact same frame order/timing as ``running-left``, just
facing the other way.

Pure image processing -- no network, no ``HERMES_HOME``, ZERO new
``generate()`` calls. Re-derives ``running-left``'s arranged frames via
``state_row.load_and_arrange`` (deterministic -- same inputs, same pixels)
rather than re-reading them off disk, so this script is runnable
standalone.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_running_right_row.py
"""

from __future__ import annotations

from build_running_left_row import POSE_FILES, ROW_FRAME_COUNT
from state_row import build_mirrored_row, load_and_arrange

STATE = "running-right"
SOURCE_STATE = "running-left"


def main() -> None:
    frames, row_pose_order = load_and_arrange(POSE_FILES, ROW_FRAME_COUNT)
    build_mirrored_row(STATE, frames, row_pose_order, SOURCE_STATE)


if __name__ == "__main__":
    main()
