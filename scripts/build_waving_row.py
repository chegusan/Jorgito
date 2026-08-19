"""Thin per-state runner: assemble the real ``waving`` row.

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic).
Pure image processing -- no network, no ``HERMES_HOME`` -- run after
``scripts/generate_waving_sequence.py`` has produced the 3 processed poses.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_waving_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "waving"
ROW_FRAME_COUNT = 4  # atlas.FRAME_COUNTS["waving"], per Hermes's real ROW_SPECS
# NOTE: the real state key is "waving" (row 3, 4 frames) per atlas.ROW_SPECS
# -- NOT "wave", and NOT the 6 frames of e.g. "waiting"/"review". Confirmed
# by reading /home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py
# directly rather than assumed, per this project's established gotcha
# (jumping's real key/count also differed from the naive guess).

# The 3 real generated poses, in wave-progression order: pose 1 arm starting
# to raise, pose 2 arm fully raised at the peak, pose 3 arm swept to the
# opposite/mid-swing point (see scripts/generate_waving_sequence.py).
POSE_FILES = [
    PROCESSED_DIR / "waving_pose1.png",
    PROCESSED_DIR / "waving_pose2.png",
    PROCESSED_DIR / "waving_pose3.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
