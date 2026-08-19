"""Phase 1 / F1-B: package idle/review/run into a real Hermes pet for
in-terminal legibility testing — reusing Hermes's own pet-store format
instead of reinventing it.

Reads the already-processed 192x208 cells from
``assets/keyframes/processed/{idle,review,run}.png`` (see
``process_phase1_keyframes.py``) and tiles each into a legacy-taxonomy
spritesheet (``agent.pet.constants.LEGACY_STATE_ROWS``: 8 rows of 192x208,
narrower than the 9-row Codex grid so the renderer's ``rows < 9`` branch
picks it, landing idle/run/review at rows 0/2/4). Each state gets its single
frame repeated across ``FRAMES_PER_STATE`` (6) columns — this project has one
static pose per state, not an animation loop, so a steady repeat plays back
as "held still", not as a flicker into blank padding.

Then calls ``agent.pet.store.register_local_pet`` (Hermes's own local-pet
registration path — same one ``/pet generate`` uses for freshly-hatched
pets) to write ``pets/jorgito-test/{pet.json,spritesheet.webp}`` under
whatever ``HERMES_HOME`` this process sees. This script sets no HERMES_HOME
itself — the caller MUST export ``HERMES_HOME`` to the isolated test profile
before running it, so it never touches the real ``~/.hermes``.

Usage (HERMES_AGENT_SRC overrides the Hermes source location; see
scripts/hermes_env.py):
    HERMES_HOME=/path/to/isolated-profile \\
        HERMES_AGENT_SRC=/path/to/hermes-agent \\
        /path/to/hermes-agent/venv/bin/python3 scripts/build_phase1_test_pet.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_env import ensure_hermes_on_path, require_isolated_hermes_home  # noqa: E402

ensure_hermes_on_path()

from PIL import Image  # noqa: E402

from agent.pet.constants import FRAME_H, FRAME_W, FRAMES_PER_STATE, LEGACY_STATE_ROWS  # noqa: E402
from agent.pet import store  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO / "assets/keyframes/processed"

SLUG = "jorgito-test"
DISPLAY_NAME = "Jorgito (Phase 1 test)"

# Map our 3 processed states onto legacy row slots.
STATE_TO_ROW_NAME = {"idle": "idle", "run": "run", "review": "review"}


def build_sheet() -> Image.Image:
    cols = FRAMES_PER_STATE
    rows = len(LEGACY_STATE_ROWS)
    sheet = Image.new("RGBA", (FRAME_W * cols, FRAME_H * rows), (0, 0, 0, 0))

    for state, row_name in STATE_TO_ROW_NAME.items():
        cell_path = PROCESSED_DIR / f"{state}.png"
        with Image.open(cell_path) as im:
            cell = im.convert("RGBA")
        assert cell.size == (FRAME_W, FRAME_H), f"{cell_path} is {cell.size}, expected {(FRAME_W, FRAME_H)}"
        row = LEGACY_STATE_ROWS.index(row_name)
        top = row * FRAME_H
        for col in range(cols):
            left = col * FRAME_W
            sheet.alpha_composite(cell, (left, top))

    return sheet


def main() -> None:
    hermes_home = require_isolated_hermes_home()

    print(f"HERMES_HOME={hermes_home}")
    sheet = build_sheet()
    pet = store.register_local_pet(
        sheet,
        slug=SLUG,
        display_name=DISPLAY_NAME,
        description="Phase 1 minimal visual proof — idle/run/review legibility test",
    )
    print(f"registered pet '{pet.slug}' -> {pet.spritesheet}")
    print(f"  exists={pet.exists} generated={pet.generated}")


if __name__ == "__main__":
    main()
