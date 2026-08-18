"""Thin per-state runner: assemble the real ``review`` row (Phase 2B addendum #2).

Config-only wrapper around the generalized ``scripts/state_row.build_state_row``
(see that module's docstring for the ping-pong/wobble/validation logic this
reuses unchanged). Re-running this against the already-committed 3 processed
review poses is a pure-image-processing dry check confirming the
generalized code reproduces addendum #2's original result -- it costs no
API calls and touches no ``HERMES_HOME``.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_review_row.py
"""

from __future__ import annotations

from pose_sequence import PROCESSED_DIR
from state_row import build_state_row

STATE = "review"
ROW_FRAME_COUNT = 6  # atlas.FRAME_COUNTS["review"], per Hermes's real ROW_SPECS

# The 3 real generated poses, in page-turn order (pose 1: book open/starting,
# from the single-pose pilot; pose 2: mid-page-turn; pose 3: page turned
# further -- see docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addendum #2).
POSE_FILES = [
    PROCESSED_DIR / "review_singlepose_pilot.png",
    PROCESSED_DIR / "review_pose2_midturn.png",
    PROCESSED_DIR / "review_pose3_turned.png",
]


def main() -> None:
    build_state_row(STATE, POSE_FILES, ROW_FRAME_COUNT)


if __name__ == "__main__":
    main()
