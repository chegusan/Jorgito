"""Thin per-state runner: assemble the real ``waiting`` row.

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic).
Pure image processing -- no network, no ``HERMES_HOME`` -- run after
``scripts/generate_waiting_sequence.py`` has produced the 3 processed poses.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_waiting_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "waiting"
ROW_FRAME_COUNT = 6  # atlas.FRAME_COUNTS["waiting"], per Hermes's real ROW_SPECS

# The 3 real generated poses, in look-progression order: pose 1 centered,
# pose 2 looking left, pose 3 looking right (see
# scripts/generate_waiting_sequence.py).
POSE_FILES = [
    PROCESSED_DIR / "waiting_pose1.png",
    PROCESSED_DIR / "waiting_pose2.png",
    PROCESSED_DIR / "waiting_pose3.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
