"""Thin per-state runner: generate 3 real chained poses for ``waiting``.

Config-only wrapper around the generalized
``scripts/pose_sequence.generate_pose_sequence`` (see that module's
docstring for the chaining/grounding/processing logic this reuses
unchanged). Same pattern validated on ``review``
(docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addenda #1/#2): a
micro-progression within the state's action, per
docs/04_ASSET_SPEC.md's "Waiting: Still/sitting pose with small eye/head
movement" -- center calm pose -> head tilts to look one direction -> head
tilts to look the other direction. No props, per D-004's action semantics
for secondary/idle-style states.

ONLY ever run against the isolated HERMES_HOME test profile -- same
refusal guard as the rest of this project's Phase 2B scripts.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_waiting_sequence.py
"""

from __future__ import annotations

from pose_sequence import generate_pose_sequence

STATE = "waiting"

ACTION_DESCRIPTIONS = [
    (
        "Jorgito waiting patiently, centered and settled: sitting calmly in a "
        "relaxed, upright posture, hands/feet settled and still, head facing "
        "forward, calm neutral expression, no props, as if quietly waiting "
        "for something to happen"
    ),
    (
        "Jorgito waiting patiently, glancing to one side: sitting calmly in "
        "the exact same relaxed, upright posture as before, only the head "
        "turned and tilted gently to look off toward the left, calm neutral "
        "expression, no props, as if checking whether something is coming "
        "from that direction"
    ),
    (
        "Jorgito waiting patiently, glancing to the other side: sitting "
        "calmly in the exact same relaxed, upright posture as before, only "
        "the head turned and tilted gently to look off toward the right, "
        "calm neutral expression, no props, as if checking whether something "
        "is coming from that direction instead"
    ),
]


def main() -> None:
    generate_pose_sequence(STATE, ACTION_DESCRIPTIONS, n_poses=3)


if __name__ == "__main__":
    main()
