"""Reusable per-state atlas row assembly, from real generated poses.

Generalizes the ``review`` state's Phase 2B addendum #2
(``build_review_row.py``) into one state-parameterized function
(``build_state_row``), the companion to ``scripts/pose_sequence.py``'s
``generate_pose_sequence``. Ping-pongs whatever real poses were generated
across the row's frame count, applies the Phase 4 deterministic wobble on
top of each so pose-sharing columns still hash-distinct, and validates with
Hermes's real ``atlas.validate_atlas()``.

Addendum #8 adds ``build_mirrored_row``, which derives one state's row as a
horizontal mirror of another's already-built row via Hermes's own
``atlas.mirror_frames()`` -- zero new generation, used to derive
``running-right`` from the real, approved ``running-left`` row (see
``build_running_right_row.py`` and the addendum in
``docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md``).

Pure Pillow image processing -- no network, no ``HERMES_HOME``.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from pose_sequence import KEYFRAMES_DIR, REPO  # noqa: F401 - REPO kept for callers

# Phase 4 wobble amplitude (unmodified from ``phase-4-full-atlas``'s
# ``scripts/full_atlas.py``, commit ``7353a27``). Small on purpose: a subtle
# bob/breathe ON TOP OF each real pose, not a replacement for pose variation.
_BOB_PX = 3
_TILT_DEG = 1.5
_SCALE_DELTA = 0.02


def _pingpong_order(n_poses: int, row_frame_count: int) -> list[int]:
    """Forward through all poses, then back down: ``[0, 1, ..., n-1, n-1, ..., 1, 0]``.

    Cycles if ``row_frame_count`` doesn't divide evenly into ``2 * n_poses``.
    For the common case here (``n_poses=3, row_frame_count=6``) this yields
    exactly ``[0, 1, 2, 2, 1, 0]``, matching ``review``'s row order.
    """
    if n_poses <= 0:
        raise ValueError("n_poses must be positive")
    cycle = list(range(n_poses)) + list(range(n_poses - 1, -1, -1))
    return [cycle[i % len(cycle)] for i in range(row_frame_count)]


def _vary(cell, i: int, n: int):
    """Return a distinct copy of *cell* for column *i* of *n*.

    Unmodified from ``phase-4-full-atlas``'s ``scripts/full_atlas.py``
    (commit ``7353a27``, cross-review fix for column collapse). Column 0
    stays byte-identical to whatever pose is assigned there; every other
    column gets the same deterministic sine-phase nudge (vertical bob,
    slight tilt, slight scale), with bob on ``sin`` and tilt/scale on
    ``cos`` specifically so mirrored columns within a cycle don't collapse
    to the same triple.
    """
    from PIL import Image

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


def _contact_sheet(frames: list, row_pose_order: list[int]):
    from agent.pet.generate import atlas
    from PIL import Image, ImageDraw, ImageFont

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

        label = f"col{i}: pose{row_pose_order[i] + 1}"
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        label_x = x0 + (cell_w - label_w) // 2
        label_y = y0 + cell_h + (label_h - (bbox[3] - bbox[1])) // 2
        draw.text((label_x, label_y), label, fill=(30, 30, 30, 255), font=font)

    return sheet


def _gif_frames(frames: list, scale: int = 3):
    from agent.pet.generate import atlas
    from PIL import Image

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
    return rgb_frames


def load_and_arrange(poses: list[Path], row_frame_count: int) -> tuple[list, list[int]]:
    """Load *poses* (processed cell images), ping-pong + wobble them into a full row.

    Pure, deterministic (``_pingpong_order`` + ``_vary``) -- calling this
    twice on the same inputs reproduces byte-identical frames. Split out of
    ``build_state_row`` so a row's already-arranged frames can be reused as
    the input to ``build_mirrored_row`` (e.g. deriving ``running-right`` from
    ``running-left``) without re-running generation or duplicating the
    arrange logic.
    """
    from PIL import Image

    for path in poses:
        if not path.is_file():
            raise FileNotFoundError(f"missing processed pose: {path}")

    loaded = []
    for path in poses:
        with Image.open(path) as src:
            loaded.append(src.convert("RGBA"))

    row_pose_order = _pingpong_order(len(poses), row_frame_count)
    frames = [_vary(loaded[pose_idx], i, row_frame_count) for i, pose_idx in enumerate(row_pose_order)]
    return frames, row_pose_order


def _finalize_row(
    state: str,
    frames: list,
    row_pose_order: list[int],
    *,
    pose_files: list[Path] | None = None,
    mirrored_from: str | None = None,
) -> dict:
    """Hash, compose, validate, and write out the artifacts for *state*'s row.

    Shared tail end of ``build_state_row`` and ``build_mirrored_row`` --
    composes a full-atlas-shaped image with only *state*'s row filled and
    validates it with Hermes's real, unmodified ``atlas.validate_atlas()``.
    Writes the atlas fragment, labeled contact sheet, looping GIF, and a
    report JSON under ``assets/keyframes/``. Pure image processing -- no
    network, no ``HERMES_HOME``. Returns the report dict (also written to
    ``assets/keyframes/{state}_row_report.json``).
    """
    from agent.pet.generate import atlas

    hashes = [hashlib.sha256(f.tobytes()).hexdigest()[:16] for f in frames]
    unique = len(set(hashes))
    print(f"{state} row: {len(frames)} frames, {unique}/{len(frames)} unique hashes")
    for i, (h, pose_idx) in enumerate(zip(hashes, row_pose_order)):
        print(f"  col{i} (pose{pose_idx + 1}): {h}")

    atlas_image = atlas.compose_atlas({state: frames})
    validation = atlas.validate_atlas(atlas_image)
    print("\nvalidate_atlas():")
    print(json.dumps(validation, indent=2))

    atlas_path = KEYFRAMES_DIR / f"{state}_row_atlas_fragment.png"
    atlas_image.save(atlas_path)
    print(f"\n-> {atlas_path} ({atlas_image.size[0]}x{atlas_image.size[1]})")

    contact_sheet = _contact_sheet(frames, row_pose_order)
    contact_path = KEYFRAMES_DIR / f"{state}_row_contact_sheet.png"
    contact_sheet.save(contact_path)
    print(f"-> {contact_path}")

    gif_frames = _gif_frames(frames)
    gif_path = KEYFRAMES_DIR / f"{state}_row_preview.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=280,
        loop=0,
    )
    print(f"-> {gif_path} ({len(gif_frames)} frames, 280ms/frame, looping)")

    report = {
        "state": state,
        "row_count": len(frames),
        "row_pose_order": row_pose_order,
        "frame_hashes": hashes,
        "unique_hash_count": unique,
        "validate_atlas": validation,
        "atlas_fragment_path": str(atlas_path),
        "contact_sheet_path": str(contact_path),
        "gif_path": str(gif_path),
    }
    if pose_files is not None:
        report["pose_files"] = [str(p) for p in pose_files]
    if mirrored_from is not None:
        report["mirrored_from"] = mirrored_from
    report_path = KEYFRAMES_DIR / f"{state}_row_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"-> {report_path}")

    if unique != len(frames):
        print("\nERROR: frame hashes are not all unique.", file=sys.stderr)
    if not validation["ok"]:
        print("\nERROR: validate_atlas() reported errors.", file=sys.stderr)

    return report


def build_state_row(state: str, poses: list[Path], row_frame_count: int) -> dict:
    """Assemble *state*'s full row from *poses* (processed cell images).

    Thin wrapper: ``load_and_arrange`` (ping-pong + wobble) followed by
    ``_finalize_row`` (hash/compose/validate/write). See both docstrings.
    """
    frames, row_pose_order = load_and_arrange(poses, row_frame_count)
    return _finalize_row(state, frames, row_pose_order, pose_files=poses)


def build_mirrored_row(target_state: str, source_frames: list, source_row_pose_order: list[int], source_state: str) -> dict:
    """Derive *target_state*'s row as a horizontal mirror of *source_frames*.

    Uses Hermes's own, unmodified ``atlas.mirror_frames()`` -- the same
    primitive ``phase-4-full-atlas`` used to derive ``running-left`` from an
    approved ``running-right`` row, applied here in the reverse direction
    (see ``docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`` addendum #8 for
    why: the real generated poses rendered left-facing despite a
    right-facing prompt, so the approved source row is ``running-left`` and
    ``running-right`` is the derived mirror instead of the other way
    around). ``mirror_frames`` flips per-frame, preserving *source_frames*'
    order/timing -- not a whole-strip reverse. Reuses
    *source_row_pose_order* for column labeling since mirroring doesn't
    change which pose a column represents, only its facing.
    """
    from agent.pet.generate import atlas

    mirrored = atlas.mirror_frames(source_frames)
    return _finalize_row(target_state, mirrored, source_row_pose_order, mirrored_from=source_state)
