"""Phase Final: render all 9 atlas states at REAL terminal size and combine
them into one labeled contact sheet -- the final visual gate artifact.

Adapted from Phase 4's ``render_full_atlas_pet.py`` (same technique, applied
to the reconciled final atlas instead of the Phase-4 deterministic one).

Uses ``agent.pet.render.PetRenderer`` directly at the project's default
terminal scale (``display.pet.scale`` default = 0.33, floors to
``UNICODE_MIN_COLS`` = 16 columns -- see ``agent/pet/constants.py``), the same
encoder the real ``hermes pets show`` CLI uses once it detects a truecolor
terminal. This session's own terminal already exercised the real CLI path via
``script``-faked TTYs (see ``terminal_render_final/*.script.txt``, produced
separately) -- this script turns that same pixel data into an inspectable PNG.

Requires HERMES_HOME set by the caller (isolated test profile).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet import store  # noqa: E402
from agent.pet.constants import DEFAULT_SCALE, cols_for_scale  # noqa: E402
from agent.pet.render import PetRenderer, _downscale_cells  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "assets/keyframes/terminal_render_final"
UPSCALE = 12  # pixels per half-block cell in each per-state preview

# (state name as passed to --state / PetRenderer, contact-sheet label)
STATES: list[tuple[str, str]] = [
    ("idle", "idle"),
    ("running-right", "running-right"),
    ("running-left", "running-left"),
    ("waving", "waving"),
    ("jumping", "jumping"),
    ("failed", "failed"),
    ("waiting", "waiting"),
    ("running", "running"),
    ("review", "review"),
]

PADDING = 20
LABEL_HEIGHT = 30
BG = (24, 24, 24, 255)


def _render_state_preview(renderer: PetRenderer, state: str, cols: int) -> Image.Image:
    frame = renderer._frames(state)[0]  # noqa: SLF001 - same scaled frame the encoder uses
    grid = _downscale_cells(frame, target_cols=cols)
    rows = len(grid)
    cell_cols = len(grid[0]) if rows else 0

    preview = Image.new("RGBA", (cell_cols * UPSCALE, rows * 2 * UPSCALE), BG)
    for ry, row in enumerate(grid):
        for cx, (top, bottom) in enumerate(row):
            top_block = Image.new("RGBA", (UPSCALE, UPSCALE), top if top[3] >= 32 else BG)
            bottom_block = Image.new("RGBA", (UPSCALE, UPSCALE), bottom if bottom[3] >= 32 else BG)
            preview.paste(top_block, (cx * UPSCALE, (ry * 2) * UPSCALE))
            preview.paste(bottom_block, (cx * UPSCALE, (ry * 2 + 1) * UPSCALE))
    return preview


def main() -> None:
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if not hermes_home:
        print("ERROR: HERMES_HOME must be set (isolated test profile).", file=sys.stderr)
        sys.exit(1)
    if Path(hermes_home).resolve() == Path.home().resolve() / ".hermes":
        print("ERROR: refusing to run against the real ~/.hermes profile.", file=sys.stderr)
        sys.exit(1)

    pet = store.load_pet("jorgito")
    if pet is None or not pet.exists:
        print("ERROR: 'jorgito' pet not installed in this HERMES_HOME.", file=sys.stderr)
        sys.exit(1)

    scale = DEFAULT_SCALE
    cols = cols_for_scale(scale)
    print(f"scale={scale} -> unicode_cols={cols} (real Hermes default terminal width)")

    renderer = PetRenderer(pet.spritesheet, mode="unicode", scale=scale, unicode_cols=cols)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    previews: dict[str, Image.Image] = {}
    for state, label in STATES:
        count = renderer.frame_count(state)
        print(f"{state}: frame_count={count}")
        preview = _render_state_preview(renderer, state, cols)
        preview.convert("RGB").save(OUT_DIR / f"{label}_realsize_preview.png")
        previews[label] = preview

    cell_w = max(p.width for p in previews.values())
    cell_h = max(p.height for p in previews.values())
    n = len(STATES)
    sheet_w = PADDING * (n + 1) + cell_w * n
    sheet_h = PADDING * 2 + cell_h + LABEL_HEIGHT

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (245, 245, 245, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    for i, (_state, label) in enumerate(STATES):
        x0 = PADDING + i * (cell_w + PADDING)
        y0 = PADDING
        sheet.alpha_composite(previews[label], (x0, y0))
        draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], outline=(150, 150, 150, 255), width=1)
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        draw.text(
            (x0 + (cell_w - label_w) // 2, y0 + cell_h + 4),
            label,
            fill=(30, 30, 30, 255),
            font=font,
        )

    sheet_path = OUT_DIR / "contact_sheet_terminal_final.png"
    sheet.save(sheet_path)
    print(f"-> {sheet_path} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
