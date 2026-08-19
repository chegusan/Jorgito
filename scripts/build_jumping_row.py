"""Thin per-state runner: assemble the real ``jumping`` row.

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic).
Pure image processing -- no network, no ``HERMES_HOME`` -- run after
``scripts/generate_jumping_sequence.py`` has produced the 3 processed poses.

``jumping``'s row is 5 frames (``atlas.ROW_SPECS`` / ``FRAME_COUNTS["jumping"]``
-- Hermes's real ``ROW_SPECS`` has ``("jumping", 4, 5)``, not 6 like
``review``/``waiting``), so ``_pingpong_order(3, 5)`` takes the first 5
entries of the base 6-length ping-pong cycle: ``[0, 1, 2, 2, 1]`` (crouch,
airborne peak, landing, landing again, airborne peak again -- the cycle
truncates before looping back to the crouch, which reads fine for a short
jump-and-land beat).

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_jumping_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "jumping"
ROW_FRAME_COUNT = 5  # atlas.FRAME_COUNTS["jumping"], per Hermes's real ROW_SPECS

# The 3 real generated poses, in jump-progression order: pose 1 crouched
# wind-up, pose 2 airborne celebratory peak, pose 3 landing/braced (see
# scripts/generate_jumping_sequence.py).
POSE_FILES = [
    PROCESSED_DIR / "jumping_pose1.png",
    PROCESSED_DIR / "jumping_pose2.png",
    PROCESSED_DIR / "jumping_pose3.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
