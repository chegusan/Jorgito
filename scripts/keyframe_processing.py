"""Shared deterministic processing for manually-generated raw keyframes.

Purely deterministic (Camino B): no network calls, no API keys, no model
inference. Input is already-committed JPEGs under assets/keyframes/raw/,
each a single pose on a flat hot-magenta chroma-key background, generated
manually by the user with jorgito_canonical.png as grounding reference.

Reuses Hermes's own deterministic chroma-key/fit-to-cell primitives
(agent.pet.generate.atlas.remove_background / _fit_to_cell) instead of
reimplementing background removal, since that logic already handles the
exact magenta backdrop these keyframes were generated against (see
agent/pet/generate/prompts.py's _BACKGROUND spec) and already produces the
project's target 192x208 cell format. This module only adds what atlas.py
doesn't provide: JPEG-artifact-tolerant keying (looser threshold than the
lossless-PNG-strip case atlas.py was built for) and the contact-sheet
composition for visual review.

Extracted from the original Phase 1 script (scripts/process_phase1_keyframes.py)
so Phase 3 (and any future phase adding more manually-sourced keyframes) can
reuse the exact same chroma-key/fit-to-cell/contact-sheet logic instead of
duplicating it per phase.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_env import ensure_hermes_on_path  # noqa: E402

ensure_hermes_on_path()

from agent.pet.generate import atlas  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RAW_DIR = REPO / "assets/keyframes/raw"
PROCESSED_DIR = REPO / "assets/keyframes/processed"

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


def process_keyframe(
    state: str,
    raw_dir: Path = RAW_DIR,
    chroma_key: tuple[int, int, int] | None = (255, 0, 255),
) -> Image.Image:
    """Chroma-key + fit-to-cell a single raw keyframe.

    `chroma_key=(255, 0, 255)` (the default, matching Phase 1's raw source)
    assumes the backdrop is pure hot-magenta. Pass `chroma_key=None` when the
    source backdrop has drifted from pure magenta (seen in Phase 3's raw
    material — a ComfyUI/JPEG-export shade shift, not just per-pixel noise:
    corner samples came back around (230, 35, 199) instead of (255, 0, 255),
    i.e. already ~65-95 color-distance from the assumed key before any
    threshold is applied). `None` lets atlas.remove_background() fall back to
    its own `_dominant_corner_color()` detection, which samples the actual
    backdrop per image instead of assuming an exact color — atlas.py's own
    built-in mechanism for exactly this case, not something reimplemented
    here. Confirmed via a residual-magenta measurement: forcing pure-magenta
    on the Phase 3 raw images left 25-76% of each cell's opaque pixels still
    background-colored (background never keyed out at all, not just fringe
    noise); auto-detection brings that to 0.00% (see PHASE_3_RESULT.md §3).
    """
    raw_path = raw_dir / f"{state}.jpeg"
    with Image.open(raw_path) as src:
        rgba = src.convert("RGBA")
        keyed = atlas.remove_background(
            rgba, chroma_key=chroma_key, threshold=JPEG_CHROMA_THRESHOLD
        )
        cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic
    return cell


def build_contact_sheet(cells: dict[str, Image.Image], states: list[str]) -> Image.Image:
    cell_w, cell_h = atlas.CELL_WIDTH * SCALE, atlas.CELL_HEIGHT * SCALE
    n = len(states)
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

    for i, state in enumerate(states):
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


def process_states(
    states: list[str],
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    chroma_key: tuple[int, int, int] | None = (255, 0, 255),
) -> dict[str, Image.Image]:
    processed_dir.mkdir(parents=True, exist_ok=True)

    cells: dict[str, Image.Image] = {}
    for state in states:
        print(f"processing '{state}'...")
        cell = process_keyframe(state, raw_dir=raw_dir, chroma_key=chroma_key)
        out_path = processed_dir / f"{state}.png"
        cell.save(out_path)
        print(f"  -> {out_path} ({cell.size[0]}x{cell.size[1]}, {cell.mode})")
        cells[state] = cell

    return cells
