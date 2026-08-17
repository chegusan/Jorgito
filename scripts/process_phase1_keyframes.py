"""Phase 1: turn the 3 manually-generated raw keyframes into sprite cells.

Purely deterministic (Camino B): no network calls, no API keys, no model
inference. Input is 3 already-committed JPEGs
(assets/keyframes/raw/{idle,review,run}.jpeg), each a single pose on a flat
hot-magenta chroma-key background, generated manually by the user with
jorgito_canonical.png as grounding reference (see docs/phase_results/
PHASE_1_RESULT.md).

Reuses Hermes's own deterministic chroma-key/fit-to-cell primitives
(agent.pet.generate.atlas.remove_background / _fit_to_cell) instead of
reimplementing background removal, since that logic already handles the
exact magenta backdrop these keyframes were generated against (see
agent/pet/generate/prompts.py's _BACKGROUND spec) and already produces the
project's target 192x208 cell format. This script only adds what atlas.py
doesn't provide: JPEG-artifact-tolerant keying (looser threshold than the
lossless-PNG-strip case atlas.py was built for) and the contact-sheet
composition for visual review.

Usage:

    python3 scripts/process_phase1_keyframes.py

Outputs:
    assets/keyframes/processed/{idle,review,run}.png  (192x208 RGBA cells)
    assets/keyframes/contact_sheet_phase1.png          (review sheet)
"""

from __future__ import annotations

import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet.generate import atlas  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RAW_DIR = REPO / "assets/keyframes/raw"
PROCESSED_DIR = REPO / "assets/keyframes/processed"
CONTACT_SHEET = REPO / "assets/keyframes/contact_sheet_phase1.png"

STATES = ["idle", "review", "run"]

# JPEG re-encoding of a flat #FF00FF backdrop introduces per-pixel noise (DCT
# ringing near the character's dark outline, chroma subsampling drift toward
# image edges), so corner pixels aren't perfectly (255, 0, 255). atlas.py's
# default threshold (90) is tuned for lossless PNG strips straight out of an
# image-gen API; widen it for JPEG source material. Confirmed sufficient by
# inspecting each output for background residue / silhouette bites.
JPEG_CHROMA_THRESHOLD = 130.0

CONTACT_BG = (245, 245, 245, 255)  # light gray
LABEL_HEIGHT = 40
PADDING = 24
SCALE = 3  # upscale cells in the contact sheet so they're actually visible


def process_keyframe(state: str) -> Image.Image:
    raw_path = RAW_DIR / f"{state}.jpeg"
    with Image.open(raw_path) as src:
        rgba = src.convert("RGBA")
        keyed = atlas.remove_background(
            rgba, chroma_key=(255, 0, 255), threshold=JPEG_CHROMA_THRESHOLD
        )
        cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic
    return cell


def build_contact_sheet(cells: dict[str, Image.Image]) -> Image.Image:
    cell_w, cell_h = atlas.CELL_WIDTH * SCALE, atlas.CELL_HEIGHT * SCALE
    n = len(STATES)
    sheet_w = PADDING * (n + 1) + cell_w * n
    sheet_h = PADDING * 2 + cell_h + LABEL_HEIGHT

    sheet = Image.new("RGBA", (sheet_w, sheet_h), CONTACT_BG)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 28
        )
    except OSError:
        font = ImageFont.load_default()

    checker_a, checker_b = (222, 222, 222, 255), (200, 200, 200, 255)
    checker_size = 8

    for i, state in enumerate(STATES):
        x0 = PADDING + i * (cell_w + PADDING)
        y0 = PADDING

        checker = Image.new("RGBA", (cell_w, cell_h))
        cpx = checker.load()
        for cy in range(cell_h):
            for cx in range(cell_w):
                cpx[cx, cy] = (
                    checker_a if (cx // checker_size + cy // checker_size) % 2 == 0 else checker_b
                )
        sheet.alpha_composite(checker, (x0, y0))

        upscaled = cells[state].resize((cell_w, cell_h), Image.Resampling.NEAREST)
        sheet.alpha_composite(upscaled, (x0, y0))

        draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], outline=(150, 150, 150, 255), width=1)

        label = state
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        label_x = x0 + (cell_w - label_w) // 2
        label_y = y0 + cell_h + (LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2
        draw.text((label_x, label_y), label, fill=(30, 30, 30, 255), font=font)

    return sheet


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    cells: dict[str, Image.Image] = {}
    for state in STATES:
        print(f"processing '{state}'...")
        cell = process_keyframe(state)
        out_path = PROCESSED_DIR / f"{state}.png"
        cell.save(out_path)
        print(f"  -> {out_path} ({cell.size[0]}x{cell.size[1]}, {cell.mode})")
        cells[state] = cell

    print("building contact sheet...")
    sheet = build_contact_sheet(cells)
    sheet.convert("RGB" if CONTACT_BG[3] == 255 else "RGBA").save(CONTACT_SHEET)
    print(f"  -> {CONTACT_SHEET} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
