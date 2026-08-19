"""Phase 1: turn the 3 manually-generated raw keyframes into sprite cells.

Thin per-phase wrapper around scripts/keyframe_processing.py (the shared
chroma-key/fit-to-cell/contact-sheet logic, extracted here in Phase 3 so it
isn't duplicated per phase). See that module's docstring for the method.

Usage:

    python3 scripts/process_phase1_keyframes.py

Outputs:
    assets/keyframes/processed/{idle,review,run}.png  (192x208 RGBA cells)
    assets/keyframes/contact_sheet_phase1.png          (review sheet)
"""

from __future__ import annotations

from pathlib import Path

from keyframe_processing import REPO, build_contact_sheet, process_states

CONTACT_SHEET = REPO / "assets/keyframes/contact_sheet_phase1.png"

STATES = ["idle", "review", "run"]


def main() -> None:
    cells = process_states(STATES)

    print("building contact sheet...")
    sheet = build_contact_sheet(cells, STATES)
    sheet.convert("RGB").save(CONTACT_SHEET)
    print(f"  -> {CONTACT_SHEET} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
