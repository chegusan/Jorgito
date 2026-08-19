"""Single-pose prompt builder for Phase 2B's pilot approach.

Companion to Hermes's own :mod:`agent.pet.generate.prompts` (row-strip
prompts, multi-pose-per-call), NOT a modification of it. Hermes source
(``/home/chegusan/.hermes/hermes-agent``) is a read-only reference tree for
this project -- it is also the real ``~/.hermes`` profile root, which this
project's guardrails say never to touch -- so ``build_single_pose_prompt``
lives here in the Jorgito repo instead of being added to
``agent/pet/generate/prompts.py`` in place. It is based directly on
``build_row_prompt`` there (same identity-grounding and background framing),
with every strip/gutter/multi-frame instruction removed since
``imagegen.generate(n=1, ...)`` already produces one image per call -- there
is nothing to slice.

Why this pilot exists: Phase 2B's row-strip attempt
(``docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md``) failed on 4/8 states
because the model could not reliably keep multiple poses on one strip from
touching/merging, and ``review`` was one of the 4 failures ("frame 3
contains multiple separated subjects"). A single centered pose per API call
sidesteps that segmentation problem entirely -- there's only ever one
subject to draw. This module builds that one-pose prompt; the pixel
processing (chroma-key + fit-to-cell) is unchanged and reuses
``scripts/keyframe_processing.py``.
"""

from __future__ import annotations

# Project-specific visual semantics (docs/09_DECISIONS.md D-004), overriding
# Hermes's generic STATE_ACTIONS for the states this project has defined a
# concrete pose for. Not every state needs an override -- states without one
# fall back to a plain "doing {state}" phrasing.
_STATE_ACTIONS: dict[str, str] = {
    "review": (
        "Jorgito thinking/reading: sitting or standing with a small pair of "
        "reading glasses on, holding an open book up in front of them, head "
        "tilted slightly down as if studying the page intently"
    ),
    "running": (
        "Jorgito working/digging: gripping a shovel with both hands, mid-dig "
        "into the ground, leaning into the effort, focused expression"
    ),
}

_BACKGROUND = (
    "Center the character on a SINGLE flat, uniform, high-contrast chroma-key "
    "background -- pure hot magenta #FF00FF (only if magenta appears on the "
    "character, use pure green #00FF00 instead). The background is ONE "
    "continuous even color that completely surrounds the character with NO "
    "gradient, vignette, texture, pattern, scenery, shadow, ground line, "
    "frame, border, panel, or divider of any kind, so it keys out cleanly. "
    "The background color must not appear anywhere on the character. No "
    "text, no labels, no speech bubbles, no UI."
)

_STYLE_HINTS: dict[str, str] = {
    "auto": (
        " Style: crisp 16-bit PIXEL-ART game sprite -- visible square pixels, a "
        "small limited palette, clean dark outline, flat cel shading, chunky "
        "chibi proportions, like a classic SNES/JRPG party member or a "
        "petdex.dev mascot. Absolutely NOT 3D-rendered, NOT a smooth painted "
        "or vector illustration, NOT photorealistic -- no soft gradients, no "
        "realistic lighting, no figurine look."
    ),
}


def _style_hint(style: str | None) -> str:
    return _STYLE_HINTS.get((style or "auto").strip().lower(), _STYLE_HINTS["auto"])


def build_single_pose_prompt(
    state: str, concept: str, style: str | None = "auto", action_override: str | None = None
) -> str:
    """A single centered pose depicting *state*'s specific action.

    Grounded on the attached reference image (identity lock), no strip/gutter/
    multi-frame language -- ``imagegen.generate(n=1, reference_images=[...])``
    already does one image per call, so there is nothing here to slice or
    segment downstream. Mirrors ``build_row_prompt``'s identity/background/style
    framing for continuity with the existing pipeline's look.

    *action_override* lets a caller describe a specific pose variant (e.g. one
    step of a page-turn sequence) instead of the single fixed action in
    ``_STATE_ACTIONS`` -- used by ``generate_review_sequence.py`` so each pose
    in the sequence still routes through this one prompt template.
    """
    action = action_override or _STATE_ACTIONS.get(
        state, f"Jorgito {state}, a clear single readable pose"
    )
    concept = (concept or "the mascot").strip()
    return (
        f"Using the attached reference image as the exact same character "
        f"(same species, face, colors, markings, proportions, and props: "
        f"{concept}), preserving the same emotional tone/mood, "
        f"draw ONE single pixel-art pose of this character showing: {action}. "
        "The character is centered in the frame, whole body visible (nothing "
        "cropped at the edges), drawn at a consistent, healthy, clearly "
        "visible size -- not shrunk tiny, not overflowing the frame. "
        "This is a SINGLE standalone image: exactly one character, one pose, "
        "no additional frames, no strip, no grid, no panels, no repeated or "
        "duplicated poses anywhere in the image. "
        f"{_BACKGROUND}{_style_hint(style)}"
    )
