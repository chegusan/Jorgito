"""Phase 1 / F1-B: render idle/run/review at REAL terminal size and save
both the raw ANSI (what `hermes pets show` actually emits) and a magnified
PNG preview (same pixel grid, just scaled up so a human can inspect it
without a truecolor terminal).

Uses agent.pet.render.PetRenderer directly at the project's default terminal
scale (display.pet.scale default = 0.33, which floors to
UNICODE_MIN_COLS = 16 columns wide — see agent/pet/constants.py) instead of
the `hermes pets show` CLI wrapper, because this sandboxed shell has no real
TTY and the CLI's resolve_mode() hard-codes off when stdout.isatty() is
False. This calls the exact same encoder (_encode_unicode / _downscale_cells)
the CLI uses once it detects a truecolor terminal, so the output is byte-for-
byte what `hermes pets show --mode unicode` would print in a real terminal —
confirmed separately against a `script`-faked-TTY run of the actual CLI
command (see build log / PHASE_1_RESULT.md).

Requires HERMES_HOME set by the caller (isolated test profile).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_env import ensure_hermes_on_path, require_isolated_hermes_home  # noqa: E402

ensure_hermes_on_path()

from agent.pet import store  # noqa: E402
from agent.pet.constants import DEFAULT_SCALE, cols_for_scale  # noqa: E402
from agent.pet.render import PetRenderer, _downscale_cells  # noqa: E402
from PIL import Image  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "assets/keyframes/terminal_render_phase1"

STATES = ["idle", "run", "review"]
UPSCALE = 20  # pixels per half-block cell in the magnified PNG preview


def main() -> None:
    require_isolated_hermes_home()

    pet = store.load_pet("jorgito-test")
    if pet is None or not pet.exists:
        print("ERROR: jorgito-test pet not installed in this HERMES_HOME.", file=sys.stderr)
        sys.exit(1)

    scale = DEFAULT_SCALE
    cols = cols_for_scale(scale)
    print(f"scale={scale} -> unicode_cols={cols} (this is the project's real default terminal width)")

    renderer = PetRenderer(pet.spritesheet, mode="unicode", scale=scale, unicode_cols=cols)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        count = renderer.frame_count(state)
        print(f"\n=== {state}: frame_count={count} ===")
        ansi = renderer.frame(state, 0)
        ansi_path = OUT_DIR / f"{state}.ans.txt"
        ansi_path.write_text(ansi, encoding="utf-8")

        frames = renderer._frames(state)  # noqa: SLF001 - same scaled frame the encoder uses
        frame = frames[0]
        grid = _downscale_cells(frame, target_cols=cols)
        rows = len(grid)
        cell_cols = len(grid[0]) if rows else 0
        print(f"  half-block grid: {cell_cols} cols x {rows} rows (each cell = 2 stacked pixels)")

        preview = Image.new("RGBA", (cell_cols * UPSCALE, rows * 2 * UPSCALE), (30, 30, 30, 255))
        for ry, row in enumerate(grid):
            for cx, (top, bottom) in enumerate(row):
                top_block = Image.new("RGBA", (UPSCALE, UPSCALE), top if top[3] >= 32 else (30, 30, 30, 255))
                bottom_block = Image.new("RGBA", (UPSCALE, UPSCALE), bottom if bottom[3] >= 32 else (30, 30, 30, 255))
                preview.paste(top_block, (cx * UPSCALE, (ry * 2) * UPSCALE))
                preview.paste(bottom_block, (cx * UPSCALE, (ry * 2 + 1) * UPSCALE))
        preview_path = OUT_DIR / f"{state}_realsize_preview.png"
        preview.convert("RGB").save(preview_path)
        print(f"  -> {ansi_path}")
        print(f"  -> {preview_path} ({preview.width}x{preview.height}px, {UPSCALE}px per real terminal half-cell)")


if __name__ == "__main__":
    main()
