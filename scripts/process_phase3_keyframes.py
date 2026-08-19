"""Phase 3: turn the 5 manually-generated raw keyframes into sprite cells.

Same method as Phase 1 (scripts/process_phase1_keyframes.py), reusing the
shared chroma-key/fit-to-cell/contact-sheet logic in
scripts/keyframe_processing.py rather than duplicating it. Input is 5
already-committed JPEGs (assets/keyframes/raw/{waiting,failed,jump,wave,
running-right}.jpeg), each a single pose on the same flat hot-magenta
chroma-key background as Phase 1's keyframes, generated manually by the
user via local ComfyUI with jorgito_canonical.png as grounding reference
(see docs/phase_results/PHASE_3_RESULT.md).

`running-left` is intentionally NOT included here — it is deferred to a
future full-atlas phase, where it will be derived by horizontal mirror of
`running-right` rather than generated/processed separately.

Usage:

    python3 scripts/process_phase3_keyframes.py

Outputs:
    assets/keyframes/processed/{waiting,failed,jump,wave,running-right}.png
        (192x208 RGBA cells)
    assets/keyframes/contact_sheet_phase3.png (review sheet)
"""

from __future__ import annotations

from keyframe_processing import REPO, build_contact_sheet, process_states

CONTACT_SHEET = REPO / "assets/keyframes/contact_sheet_phase3.png"

STATES = ["waiting", "failed", "jump", "wave", "running-right"]


def main() -> None:
    # chroma_key=None: these raw JPEGs' backdrop has drifted from pure
    # magenta (measured corner color ~(230, 35, 199), not (255, 0, 255) —
    # see keyframe_processing.process_keyframe's docstring and
    # PHASE_3_RESULT.md §3), so auto-detect the actual per-image backdrop
    # color instead of assuming Phase 1's exact key.
    cells = process_states(STATES, chroma_key=None)

    print("building contact sheet...")
    sheet = build_contact_sheet(cells, STATES)
    sheet.convert("RGB").save(CONTACT_SHEET)
    print(f"  -> {CONTACT_SHEET} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
