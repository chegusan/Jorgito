"""Build a labeled static contact sheet + one animated collage GIF for the
final 9-row atlas, for human visual review. Pure Pillow, no generation.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_final_atlas  # noqa: E402
from agent.pet.generate import atlas  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "assets/keyframes"

CELL_W = atlas.CELL_WIDTH
CELL_H = atlas.CELL_HEIGHT
LABEL_W = 150
PAD = 6
BG = (24, 24, 28, 255)
CHECKER_A = (40, 40, 46, 255)
CHECKER_B = (30, 30, 34, 255)


def _checker_bg(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), CHECKER_A)
    draw = ImageDraw.Draw(img)
    step = 12
    for y in range(0, h, step):
        for x in range(0, w, step):
            if (x // step + y // step) % 2:
                draw.rectangle([x, y, x + step, y + step], fill=CHECKER_B)
    return img


def build_contact_sheet(frames_by_state: dict[str, list]) -> Image.Image:
    max_cols = max(count for _, _, count in atlas.ROW_SPECS)
    rows = len(atlas.ROW_SPECS)
    sheet_w = LABEL_W + max_cols * (CELL_W + PAD) + PAD
    sheet_h = rows * (CELL_H + PAD) + PAD
    sheet = Image.new("RGBA", (sheet_w, sheet_h), BG)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 18
        )
    except Exception:
        font = ImageFont.load_default()

    for state, row, count in atlas.ROW_SPECS:
        y = PAD + row * (CELL_H + PAD)
        draw.text((PAD, y + CELL_H // 2 - 10), state, fill=(255, 255, 255, 255), font=font)
        for col, frame in enumerate(frames_by_state[state]):
            x = LABEL_W + col * (CELL_W + PAD)
            cell_bg = _checker_bg(CELL_W, CELL_H)
            cell_bg.alpha_composite(frame)
            sheet.alpha_composite(cell_bg, (x, y))
    return sheet


def build_collage_gif(frames_by_state: dict[str, list], out_frames: int = 8) -> Image.Image | list:
    max_cols = max(count for _, _, count in atlas.ROW_SPECS)
    rows = len(atlas.ROW_SPECS)
    scale = 0.6
    cell_w = int(CELL_W * scale)
    cell_h = int(CELL_H * scale)
    sheet_w = LABEL_W + max_cols * (cell_w + PAD) + PAD
    sheet_h = rows * (cell_h + PAD) + PAD

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 14
        )
    except Exception:
        font = ImageFont.load_default()

    gif_frames = []
    for i in range(out_frames):
        frame_img = Image.new("RGBA", (sheet_w, sheet_h), BG)
        draw = ImageDraw.Draw(frame_img)
        for state, row, count in atlas.ROW_SPECS:
            y = PAD + row * (cell_h + PAD)
            draw.text((PAD, y + cell_h // 2 - 8), state, fill=(255, 255, 255, 255), font=font)
            frames = frames_by_state[state]
            cell = frames[i % len(frames)].resize((cell_w, cell_h))
            cell_bg = _checker_bg(cell_w, cell_h)
            cell_bg.alpha_composite(cell)
            x = LABEL_W
            frame_img.alpha_composite(cell_bg, (x, y))
        gif_frames.append(frame_img.convert("RGB"))
    return gif_frames


def main() -> None:
    frames_by_state = build_final_atlas.build_frames_by_state()

    sheet = build_contact_sheet(frames_by_state)
    sheet_path = OUT_DIR / "atlas_final_contact_sheet.png"
    sheet.convert("RGB").save(sheet_path)
    print(f"Wrote {sheet_path}")

    gif_frames = build_collage_gif(frames_by_state)
    gif_path = OUT_DIR / "atlas_final_collage.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=180,
        loop=0,
    )
    print(f"Wrote {gif_path}")


if __name__ == "__main__":
    main()
