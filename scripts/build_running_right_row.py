"""Thin per-state runner: assemble the real ``running-right`` row.

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic).
Pure image processing -- no network, no ``HERMES_HOME`` -- run after
``scripts/generate_running_right_sequence.py`` has produced the 3 processed
poses.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_running_right_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "running-right"
ROW_FRAME_COUNT = 8  # atlas.FRAME_COUNTS["running-right"], per Hermes's real ROW_SPECS
# NOTE: the real state key is "running-right" (row 1, 8 frames) per
# atlas.ROW_SPECS -- confirmed by reading
# /home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py directly
# rather than assumed, per this project's established gotcha (jumping's and
# waving's real key/count also differed from a naive guess). "running" (row
# 7, 6 frames) is a different, unrelated state (in-place working/digging
# pose) -- not to be confused with this one.

# The 3 real generated poses, in stride-progression order: pose 1 right-leg
# forward / left-leg back, pose 2 compact mid-air passing position, pose 3
# left-leg forward / right-leg back (mirror of pose 1) -- see
# scripts/generate_running_right_sequence.py.
POSE_FILES = [
    PROCESSED_DIR / "running-right_pose1.png",
    PROCESSED_DIR / "running-right_pose2.png",
    PROCESSED_DIR / "running-right_pose3.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
