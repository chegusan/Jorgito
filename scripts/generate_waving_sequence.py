"""Thin per-state runner: generate 3 real chained poses for ``waving``.

Config-only wrapper around the generalized
``scripts/pose_sequence.generate_pose_sequence`` (see that module's
docstring for the chaining/grounding/processing logic this reuses
unchanged). Same pattern validated on ``review``/``waiting``/``failed``
(docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addenda #1/#2/#3/#4): a
micro-progression within the state's action, per docs/04_ASSET_SPEC.md's
"Waving: Simple clear arm wave" -- arm starting to raise -> arm fully
raised at the peak of the wave -> arm swept to the opposite/mid-swing
point, so the ping-pong distribution in ``build_waving_row.py`` reads as
continuous side-to-side waving motion rather than a single up-down blip.

Learned from ``waiting``'s near-miss (docs/phase_results -- those poses
were too subtle/similar and barely passed validation): each action
description below pins a clearly different arm silhouette/angle so the
three poses are unmistakably distinct, not a subtle variation on one pose.

ONLY ever run against the isolated HERMES_HOME test profile -- same
refusal guard as the rest of this project's Phase 2B scripts.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_waving_sequence.py
"""

from __future__ import annotations

from pose_sequence import generate_pose_sequence

STATE = "waving"

ACTION_DESCRIPTIONS = [
    (
        "Jorgito starting a friendly wave, arm just beginning to lift: one "
        "arm raised partway up and slightly out to the side, only about "
        "chest height, elbow bent, hand starting to open, as if the wave is "
        "just beginning -- a clearly LOW, early-stage arm position, "
        "unmistakably different from a fully raised arm; the other arm "
        "resting naturally at the side, tail resting naturally, warm "
        "friendly smile, facing forward"
    ),
    (
        "Jorgito at the peak of a big friendly wave: one arm raised "
        "straight up high above the head/shoulder, fully extended, hand "
        "wide open with palm facing forward in a clear, unmistakable wave "
        "gesture -- the arm at its highest, most vertical point, a "
        "dramatically different silhouette from a low partially-raised "
        "arm; the other arm resting naturally at the side, tail resting "
        "naturally, big warm friendly smile, facing forward"
    ),
    (
        "Jorgito mid-wave, arm swept to the opposite side at the far end of "
        "the swing: the waving arm bent and extended diagonally out and "
        "down to the OPPOSITE side of the body from where it started, "
        "roughly shoulder height, hand open in a clear wave gesture -- a "
        "distinctly different diagonal arm angle from both the low starting "
        "raise and the straight-up peak, reading as the far side of a "
        "side-to-side wave swing, NOT a return to a resting pose; the other "
        "arm resting naturally at the side, tail resting naturally, warm "
        "friendly smile, facing forward"
    ),
]


def main() -> None:
    generate_pose_sequence(STATE, ACTION_DESCRIPTIONS, n_poses=3)


if __name__ == "__main__":
    main()
