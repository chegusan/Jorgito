"""Phase 4: assemble + validate the full 9-row atlas.

Pure image processing -- no HERMES_HOME / pet-store writes here (that's
``install_full_atlas_pet.py``). Derives ``running-left`` (mirror of
``running-right``), composes the real Hermes 9-row atlas via
``agent.pet.generate.atlas.compose_atlas()``, validates it with
``atlas.validate_atlas()`` (Hermes's own validator, per docs/phase_results/
PHASE_0_RESULT.md's recommendation -- not a project-invented one), and builds
the final 9-state contact sheet for the user's visual gate.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_full_atlas.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import full_atlas  # noqa: E402
from keyframe_processing import build_contact_sheet  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO / "assets/keyframes/processed"
OUT_DIR = REPO / "assets/keyframes"

# (processed-file stem, contact-sheet label) in the row order that reads best
# for the visual gate: idle, the two directional rows side by side, then the
# rest of docs/03's row order.
CONTACT_ENTRIES: list[tuple[str, str]] = [
    ("idle", "idle"),
    ("running-right", "running-right"),
    ("running-left", "running-left"),
    ("wave", "waving"),
    ("jump", "jumping"),
    ("failed", "failed"),
    ("waiting", "waiting"),
    ("run", "running"),
    ("review", "review"),
]


def main() -> None:
    print("deriving running-left (mirror of running-right)...")
    running_left = full_atlas.derive_running_left()
    running_left_path = PROCESSED_DIR / "running-left.png"
    running_left.save(running_left_path)
    print(
        f"  -> {running_left_path} "
        f"({running_left.size[0]}x{running_left.size[1]}, {running_left.mode})"
    )

    print("composing full 9-row atlas via agent.pet.generate.atlas.compose_atlas()...")
    atlas_image = full_atlas.build_atlas_image()
    atlas_path = OUT_DIR / "atlas_full.png"
    atlas_image.save(atlas_path)
    print(f"  -> {atlas_path} ({atlas_image.size[0]}x{atlas_image.size[1]})")

    print("validating via agent.pet.generate.atlas.validate_atlas()...")
    report = full_atlas.validate(atlas_image)
    report_path = OUT_DIR / "atlas_full_validation.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"  -> {report_path}")

    print("building final 9-state contact sheet...")
    cells = {
        label: (running_left if stem == "running-left" else full_atlas.load_processed(stem))
        for stem, label in CONTACT_ENTRIES
    }
    labels = [label for _stem, label in CONTACT_ENTRIES]
    sheet = build_contact_sheet(cells, labels)
    sheet_path = OUT_DIR / "contact_sheet_phase4_full.png"
    sheet.save(sheet_path)
    print(f"  -> {sheet_path} ({sheet.size[0]}x{sheet.size[1]})")

    if not report["ok"]:
        print("VALIDATION FAILED", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
