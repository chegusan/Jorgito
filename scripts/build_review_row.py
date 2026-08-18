"""Phase 2B addendum #2: assemble the real ``review`` row (6 frames, 3 real poses).

``agent.pet.generate.atlas.ROW_SPECS`` (Hermes's real, unmodified atlas spec)
requires exactly 6 frames for the ``review`` row. This project now has 3 real,
distinct generated poses for ``review`` (a page-turn progression: pose 1
book-open/starting, pose 2 mid-page-turn, pose 3 page-turned-further --
``scripts/generate_single_pose.py`` + ``scripts/generate_review_sequence.py``),
not 6, so the 3 real poses are distributed across the 6 row positions in a
page-turn order, then each column additionally gets the Phase 4 deterministic
bob/tilt/scale wobble (``_vary``, copied verbatim below from
``phase-4-full-atlas``'s ``scripts/full_atlas.py`` -- that branch is never
merged, so the function can't be imported directly; see its cross-review
commit ``7353a27`` for the decoupled-phase fix this preserves unmodified) so
that even the two columns sharing a base pose (pose 1 at both row ends, pose
3 in the middle) don't hash-collide.

Row order: pose1, pose2, pose3, pose3, pose2, pose1 -- a forward-then-back
page-turn ping-pong. This keeps the loop seam smooth (the row's last frame
and its first frame are both close to the same "settled" pose rather than
jump-cutting from a fully-turned page back to a closed book) while still
showing the full page-turn progression forward AND in reverse across one
6-frame loop, unlike the single-pose pilot's one wobbled static image.

Builds a full-size (1536x1872) atlas image with ONLY the ``review`` row
filled (every other row's cells stay transparent, per
``atlas.compose_atlas``'s own documented behavior for missing states) so
Hermes's real, unmodified ``atlas.validate_atlas()`` can run structurally
without needing the other 8 states -- ``validate_atlas`` only *warns* (not
errors) on an unfilled state row, so this is a legitimate use of the real
validator, not a project-invented substitute.

Pure image processing -- no HERMES_HOME, no network calls, no pet-store
writes.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/build_review_row.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet.generate import atlas  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO / "assets/keyframes/processed"
OUT_DIR = REPO / "assets/keyframes"

STATE = "review"
ROW_COUNT = atlas.FRAME_COUNTS[STATE]  # 6, per Hermes's real ROW_SPECS

# The 3 real generated poses, in page-turn order. Matches
# scripts/generate_review_sequence.py's naming (pose 2/3) and the pilot's
# review_singlepose_pilot.png (pose 1).
POSE_FILES = [
    PROCESSED_DIR / "review_singlepose_pilot.png",  # pose 1: book open, starting
    PROCESSED_DIR / "review_pose2_midturn.png",  # pose 2: mid-page-turn
    PROCESSED_DIR / "review_pose3_turned.png",  # pose 3: page turned further
]

# Ping-pong across the row's 6 slots: forward through the page-turn, then
# back. Indexes into POSE_FILES.
ROW_POSE_ORDER = [0, 1, 2, 2, 1, 0]
assert len(ROW_POSE_ORDER) == ROW_COUNT, f"row order must have {ROW_COUNT} entries"

# ───────────────────────── wobble (copied verbatim from phase-4-full-atlas) ─────────────────────────
# Amplitude of the deterministic per-column variation. Small on purpose: this
# is a subtle bob/breathe ON TOP OF each real pose, not a replacement for the
# pose variation above.
_BOB_PX = 3
_TILT_DEG = 1.5
_SCALE_DELTA = 0.02


def _vary(cell: Image.Image, i: int, n: int) -> Image.Image:
    """Return a distinct copy of *cell* for column *i* of *n*.

    Unmodified from ``phase-4-full-atlas``'s ``scripts/full_atlas.py`` (commit
    ``7353a27``, cross-review fix for column collapse). Column 0 stays
    byte-identical to whatever pose is assigned there; every other column
    gets the same deterministic sine-phase nudge (vertical bob, slight tilt,
    slight scale), with bob on ``sin`` and tilt/scale on ``cos`` specifically
    so mirrored columns within a cycle don't collapse to the same triple.
    """
    if i == 0 or n <= 1:
        return cell.copy()

    phase = 2 * math.pi * i / n
    dy = round(_BOB_PX * math.sin(phase))
    angle = _TILT_DEG * math.cos(phase)
    scale = 1.0 - _SCALE_DELTA * math.cos(phase)

    w, h = cell.size
    rotated = cell.rotate(angle, resample=Image.Resampling.NEAREST, fillcolor=(0, 0, 0, 0))
    sw, sh = max(1, round(w * scale)), max(1, round(h * scale))
    scaled = rotated.resize((sw, sh), Image.Resampling.NEAREST) if (sw, sh) != (w, h) else rotated

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(scaled, ((w - sw) // 2, (h - sh) // 2 + dy))
    return out


# ───────────────────────── row assembly ─────────────────────────


def load_poses() -> list[Image.Image]:
    poses = []
    for path in POSE_FILES:
        if not path.is_file():
            raise FileNotFoundError(f"missing processed pose: {path}")
        with Image.open(path) as im:
            poses.append(im.convert("RGBA"))
    return poses


def build_review_frames() -> list[Image.Image]:
    """6 frames: real pose per column (ping-pong order) + wobble on top."""
    poses = load_poses()
    frames = []
    for i, pose_idx in enumerate(ROW_POSE_ORDER):
        base = poses[pose_idx]
        frames.append(_vary(base, i, ROW_COUNT))
    return frames


def frame_hashes(frames: list[Image.Image]) -> list[str]:
    return [hashlib.sha256(f.tobytes()).hexdigest()[:16] for f in frames]


def build_contact_sheet(frames: list[Image.Image]) -> Image.Image:
    """Labeled contact sheet: one column per row frame, in page-turn order."""
    scale = 3
    cell_w, cell_h = atlas.CELL_WIDTH * scale, atlas.CELL_HEIGHT * scale
    padding = 24
    label_h = 56
    n = len(frames)
    sheet_w = padding * (n + 1) + cell_w * n
    sheet_h = padding * 2 + cell_h + label_h

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (245, 245, 245, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()

    checker_a, checker_b = (222, 222, 222, 255), (200, 200, 200, 255)
    checker_size = 8

    for i, frame in enumerate(frames):
        x0 = padding + i * (cell_w + padding)
        y0 = padding

        checker = Image.new("RGBA", (cell_w, cell_h))
        cpx = checker.load()
        for cy in range(cell_h):
            for cx in range(cell_w):
                cpx[cx, cy] = checker_a if (cx // checker_size + cy // checker_size) % 2 == 0 else checker_b
        sheet.alpha_composite(checker, (x0, y0))

        upscaled = frame.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        sheet.alpha_composite(upscaled, (x0, y0))
        draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], outline=(150, 150, 150, 255), width=1)

        pose_idx = ROW_POSE_ORDER[i]
        label = f"col{i}: pose{pose_idx + 1}"
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        label_x = x0 + (cell_w - label_w) // 2
        label_y = y0 + cell_h + (label_h - (bbox[3] - bbox[1])) // 2
        draw.text((label_x, label_y), label, fill=(30, 30, 30, 255), font=font)

    return sheet


def build_gif(frames: list[Image.Image], scale: int = 3, duration_ms: int = 280) -> Image.Image:
    """Looping animated preview: upscaled frames on a light checker backdrop."""
    cell_w, cell_h = atlas.CELL_WIDTH * scale, atlas.CELL_HEIGHT * scale
    checker_a, checker_b = (222, 222, 222, 255), (200, 200, 200, 255)
    checker_size = 8
    checker = Image.new("RGBA", (cell_w, cell_h))
    cpx = checker.load()
    for cy in range(cell_h):
        for cx in range(cell_w):
            cpx[cx, cy] = checker_a if (cx // checker_size + cy // checker_size) % 2 == 0 else checker_b

    rgb_frames = []
    for frame in frames:
        canvas = checker.copy()
        canvas.alpha_composite(frame.resize((cell_w, cell_h), Image.Resampling.NEAREST))
        rgb_frames.append(canvas.convert("RGB"))

    out = rgb_frames[0]
    return out, rgb_frames, duration_ms


def main() -> None:
    frames = build_review_frames()
    hashes = frame_hashes(frames)
    unique = len(set(hashes))
    print(f"review row: {len(frames)} frames, {unique}/{len(frames)} unique hashes")
    for i, (h, pose_idx) in enumerate(zip(hashes, ROW_POSE_ORDER)):
        print(f"  col{i} (pose{pose_idx + 1}): {h}")

    # Full-atlas-shaped image with ONLY the review row filled, so Hermes's
    # real, unmodified validate_atlas() can run without the other 8 states.
    atlas_image = atlas.compose_atlas({STATE: frames})
    validation = atlas.validate_atlas(atlas_image)
    print("\nvalidate_atlas():")
    print(json.dumps(validation, indent=2))

    atlas_path = OUT_DIR / "review_row_atlas_fragment.png"
    atlas_image.save(atlas_path)
    print(f"\n-> {atlas_path} ({atlas_image.size[0]}x{atlas_image.size[1]})")

    contact_sheet = build_contact_sheet(frames)
    contact_path = OUT_DIR / "review_row_contact_sheet.png"
    contact_sheet.save(contact_path)
    print(f"-> {contact_path}")

    _, gif_frames, duration_ms = build_gif(frames)
    gif_path = OUT_DIR / "review_row_preview.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
    )
    print(f"-> {gif_path} ({len(gif_frames)} frames, {duration_ms}ms/frame, looping)")

    report = {
        "state": STATE,
        "row_count": ROW_COUNT,
        "row_pose_order": ROW_POSE_ORDER,
        "pose_files": [str(p) for p in POSE_FILES],
        "frame_hashes": hashes,
        "unique_hash_count": unique,
        "validate_atlas": validation,
        "atlas_fragment_path": str(atlas_path),
        "contact_sheet_path": str(contact_path),
        "gif_path": str(gif_path),
    }
    report_path = OUT_DIR / "review_row_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"-> {report_path}")

    if unique != len(frames):
        print("\nERROR: frame hashes are not all unique.", file=sys.stderr)
        sys.exit(1)
    if not validation["ok"]:
        print("\nERROR: validate_atlas() reported errors.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
