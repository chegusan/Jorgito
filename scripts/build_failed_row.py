"""Thin per-state runner: assemble the real ``failed`` row.

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic).
Pure image processing -- no network, no ``HERMES_HOME`` -- run after
``scripts/generate_failed_sequence.py`` has produced the 3 processed poses.

``failed``'s row is 8 frames (``atlas.ROW_SPECS`` / ``FRAME_COUNTS["failed"]``
-- longer than ``review``/``waiting``'s 6), so ``_pingpong_order(3, 8)``
cycles the base 6-length ping-pong pattern once: ``[0, 1, 2, 2, 1, 0, 0, 1]``.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_failed_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "failed"
ROW_FRAME_COUNT = 8  # atlas.FRAME_COUNTS["failed"], per Hermes's real ROW_SPECS

# The 3 real generated poses, in confusion-progression order: pose 1
# neutral-confused, pose 2 head-tilt + arm scratching head, pose 3 fuller
# confused gesture with smoke puff (see scripts/generate_failed_sequence.py).
POSE_FILES = [
    PROCESSED_DIR / "failed_pose1.png",
    PROCESSED_DIR / "failed_pose2.png",
    PROCESSED_DIR / "failed_pose3.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
