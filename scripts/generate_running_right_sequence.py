"""Thin per-state runner: generate 3 real chained poses for ``running-right``.

Config-only wrapper around the generalized
``scripts/pose_sequence.generate_pose_sequence`` (see that module's
docstring for the chaining/grounding/processing logic this reuses
unchanged). Same pattern validated on
``review``/``waiting``/``failed``/``jumping``/``waving``
(docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addenda #1-#6): a
three-pose stride cycle for the locomotion row, per this project's convention
of pinning a clearly different silhouette per pose rather than a subtle
variation on one pose (learned from ``waiting``'s near-miss).

ONLY ever run against the isolated HERMES_HOME test profile -- same
refusal guard as the rest of this project's Phase 2B scripts.

Addendum #8 note: despite every ``ACTION_DESCRIPTIONS`` prompt below asking
for rightward-facing poses, the model rendered all 3 leftward-facing
(addendum #7's visual caveat). The human's zero-cost decision was to keep
these real, already-paid-for poses and relabel the row they build as
``running-left`` instead of retrying -- see
``scripts/build_running_left_row.py`` and
``scripts/build_running_right_row.py`` (which now derives ``running-right``
as a horizontal mirror of the ``running-left`` row via Hermes's
``atlas.mirror_frames()``). This file is left unchanged as the accurate
historical record of what was actually generated and requested; only the
row assembly downstream was relabeled.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_running_right_sequence.py
"""

from __future__ import annotations

from pose_sequence import generate_pose_sequence

STATE = "running-right"

ACTION_DESCRIPTIONS = [
    (
        "Jorgito mid-run stride, facing and moving toward the right side of "
        "the frame: right leg reaching far forward and bent at the knee "
        "about to plant, left leg extended straight back behind the body, "
        "arms in an opposite running swing (left arm forward, right arm "
        "back), torso leaning forward into the run with clear forward "
        "momentum, tail trailing straight out behind for balance, focused "
        "energetic expression -- a clearly OPEN, wide-stride leg silhouette, "
        "unmistakably different from legs together or crossing"
    ),
    (
        "Jorgito mid-run passing position, facing and moving toward the "
        "right side of the frame, grounded on the previous stride pose: "
        "both legs momentarily close together and crossing directly "
        "underneath the body (the driving/support phase of the stride, "
        "knees bent and stacked near the body's centerline), body slightly "
        "higher and more upright/compact than the reaching stride, arms "
        "swung to a tucked mid-swing position close to the torso, a "
        "dynamic sense of quick motion -- a clearly COMPACT, legs-together "
        "silhouette, unmistakably different from the wide reaching stride"
    ),
    (
        "Jorgito mid-run stride, facing and moving toward the right side of "
        "the frame, grounded on the previous passing pose: left leg now "
        "reaching far forward and bent at the knee about to plant, right "
        "leg extended straight back behind the body -- the mirror-opposite "
        "leg placement of the first stride pose -- arms swapped to the "
        "opposite running swing (right arm forward, left arm back), torso "
        "leaning forward into the run with clear forward momentum, tail "
        "trailing straight out behind for balance, focused energetic "
        "expression -- a clearly OPEN, wide-stride leg silhouette mirrored "
        "from the first pose, unmistakably different from the compact "
        "passing position"
    ),
]


def main() -> None:
    generate_pose_sequence(STATE, ACTION_DESCRIPTIONS, n_poses=3)


if __name__ == "__main__":
    main()
