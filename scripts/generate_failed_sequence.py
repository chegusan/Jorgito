"""Thin per-state runner: generate 3 real chained poses for ``failed``.

Config-only wrapper around the generalized
``scripts/pose_sequence.generate_pose_sequence`` (see that module's
docstring for the chaining/grounding/processing logic this reuses
unchanged). Same pattern validated on ``review`` and ``waiting``
(docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md addenda #1/#2/#3): a
micro-progression within the state's action, per docs/04_ASSET_SPEC.md's
"Failed: Friendly confused reaction; optional tiny smoke puff" -- neutral,
mildly confused start -> head tilts and an arm raises to scratch the head
-> fuller confused gesture with a small puff of smoke. Comedic and gentle,
NOT scary or aggressive, per the same doc entry and D-004's tone.

Learned from ``waiting``'s caveat (poses came out too visually similar):
each action description below asks for a CLEARLY DIFFERENT, unambiguous
body pose -- not just a subtler expression/gaze shift -- so the
progression reads at a glance.

ONLY ever run against the isolated HERMES_HOME test profile -- same
refusal guard as the rest of this project's Phase 2B scripts.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_failed_sequence.py
"""

from __future__ import annotations

from pose_sequence import generate_pose_sequence

STATE = "failed"

ACTION_DESCRIPTIONS = [
    (
        "Jorgito mildly confused and surprised, pose 1 of 3: standing "
        "upright with both arms down at its sides, torso leaned back "
        "slightly, head tilted to one side, eyebrows raised and eyes "
        "slightly wide, mouth in a small confused 'huh?' shape, as if "
        "something unexpected just happened -- no smoke, no props, a clear "
        "surprised-but-gentle first reaction"
    ),
    (
        "Jorgito mildly confused, pose 2 of 3: standing upright, one arm "
        "now bent and raised up with the hand/paw scratching the top of "
        "its head, the other arm still down at its side, head tilted "
        "further and eyes looking upward and off to one side as if puzzling "
        "over the problem, eyebrows knit together in a comedic 'thinking "
        "hard about what went wrong' expression -- no smoke yet, clearly a "
        "different body pose from pose 1 (arm now up at the head, not down)"
    ),
    (
        "Jorgito fully confused, pose 3 of 3: standing upright, both arms "
        "now raised up near its head in an exaggerated shrugging/puzzled "
        "gesture (palms/paws up and open), head tilted back slightly, eyes "
        "wide with a small comedic sweat-drop, a tiny single wisp of white "
        "smoke or steam puffing gently from just above its head, mouth open "
        "in a small 'uh-oh' shape -- gentle and cute, NOT scary or "
        "aggressive, clearly a different, bigger gesture than poses 1 and 2 "
        "(both arms up, small smoke puff present)"
    ),
]


def main() -> None:
    generate_pose_sequence(STATE, ACTION_DESCRIPTIONS, n_poses=3)


if __name__ == "__main__":
    main()
