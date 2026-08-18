"""Thin per-state runner: generate 3 real chained poses for ``jumping``.

Config-only wrapper around the generalized
``scripts/pose_sequence.generate_pose_sequence`` (see that module's
docstring for the chaining/grounding/processing logic this reuses
unchanged). Same pattern validated on ``review``, ``waiting``, and
``failed`` (docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addenda
#1/#2/#3/#4): a micro-progression within the state's action, per
docs/04_ASSET_SPEC.md's "Jumping: Short celebratory jump; slight wing
opening" -- a crouch wind-up, an airborne celebratory peak, and a landing.

Learned from ``waiting``'s caveat (poses came out too visually similar):
each action description below asks for a CLEARLY DIFFERENT, unambiguous
body pose and silhouette -- crouched-low vs airborne-extended vs
landed-and-braced -- not just a subtler expression/gaze shift, so the
progression reads at a glance even at small size.

ROW_SPECS names this state ``"jumping"`` (not ``"jump"``) --
``/home/chegusan/.hermes/hermes-agent/agent/pet/generate/atlas.py``,
``ROW_SPECS = [..., ("jumping", 4, 5), ...]`` -- so this runner uses that
exact state key throughout (matches ``atlas.FRAME_COUNTS["jumping"]`` /
``atlas.compose_atlas({"jumping": ...})``).

ONLY ever run against the isolated HERMES_HOME test profile -- same
refusal guard as the rest of this project's Phase 2B scripts.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_jumping_sequence.py
"""

from __future__ import annotations

from pose_sequence import generate_pose_sequence

STATE = "jumping"

ACTION_DESCRIPTIONS = [
    (
        "Jorgito winding up to jump, pose 1 of 3: crouched low and close to "
        "the ground, knees bent deeply, body compact and hunched down, both "
        "arms pulled back and down close to the sides as if coiling energy, "
        "wings folded flat and tucked against its back, head tilted slightly "
        "down with a focused, determined expression, eyes narrowed -- a "
        "clear low, compact, grounded silhouette, nothing raised or "
        "extended"
    ),
    (
        "Jorgito at the peak of a celebratory jump, pose 2 of 3: fully "
        "airborne with both feet off the ground and legs extended/tucked "
        "beneath it, body stretched tall and upright, both arms raised "
        "straight up above its head in an exuberant cheering gesture (paws "
        "open), wings spread open and flared out to the sides, head tilted "
        "back slightly, big wide-open joyful smile and bright excited eyes "
        "-- a clear tall, open, airborne silhouette, unmistakably different "
        "from the crouched pose 1 (arms up not down, wings open not "
        "folded, body stretched not compact, off the ground not grounded)"
    ),
    (
        "Jorgito landing after the jump, pose 3 of 3: back on the ground, "
        "knees bent and braced to absorb the landing impact, both arms out "
        "to the sides at roughly shoulder height for balance (paws open), "
        "wings half-open and settling downward, torso leaning slightly "
        "forward, a satisfied happy grin with eyes still bright from the "
        "jump -- a clear wide, braced, grounded silhouette, unmistakably "
        "different from both pose 1 (arms out to the sides not pulled in, "
        "wings settling not folded flat, torso leaning forward not hunched "
        "down) and pose 2 (feet back on the ground, arms out not raised "
        "overhead)"
    ),
]


def main() -> None:
    generate_pose_sequence(STATE, ACTION_DESCRIPTIONS, n_poses=3)


if __name__ == "__main__":
    main()
