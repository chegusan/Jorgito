"""Reusable per-state pose-sequence generation.

Generalizes the ``review`` state's Phase 2B addenda #1/#2
(``generate_single_pose.py`` + ``generate_review_sequence.py``) into one
state-parameterized function, so each further state (``waiting``, ``failed``,
``jumping``, ``waving``, ``running``) needs only a thin few-line runner
script -- config plus one call -- instead of a new near-duplicate ~120-line
file. Row assembly from the generated poses lives in ``scripts/state_row.py``.

``generate_pose_sequence`` drives Hermes's real ``imagegen.generate()`` once
per pose (``n=1``, no retries, no fallback provider), chaining each pose on
``BASE_IMAGE`` + the immediately-preceding pose's raw output (pose 0 grounds
on ``BASE_IMAGE`` alone -- the same grounding review's pose 1 used) via
``prompts_single_pose.build_single_pose_prompt``'s ``action_override``, then
chroma-keys + fits each to a cell with Hermes's own
``atlas.remove_background`` / ``atlas._fit_to_cell`` primitives
(``chroma_key=None`` == auto-detect, correct for lossless PNG generator
output -- see ``keyframe_processing.py``'s docstring for why the JPEG-tuned
threshold there doesn't apply to this raw material).

Touches the network and ``HERMES_HOME`` (isolated test profile only, same
refusal guard as the rest of this project's Phase 2B scripts).
"""

from __future__ import annotations

import json
import math
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

ISOLATED_HOME = "/home/chegusan/.hermes-jorgito-test"
REAL_HOME = str(Path.home() / ".hermes")

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

BASE_IMAGE = REPO / "assets/reference/jorgito_canonical.png"
CONCEPT = (
    "a small friendly Petdex-style pixel-art dragon mascot, crimson/burgundy "
    "body, large green eyes, yellow belly/neck plates and wing membranes, "
    "red wings, curled tail"
)

RAW_OUT_DIR = REPO / "assets/keyframes/raw_single_pose"
PROCESSED_DIR = REPO / "assets/keyframes/processed"
KEYFRAMES_DIR = REPO / "assets/keyframes"


def _credits() -> dict:
    key = os.environ["OPENROUTER_API_KEY"]
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)["data"]
    return {
        "total_credits": data["total_credits"],
        "total_usage": data["total_usage"],
        "balance": data["total_credits"] - data["total_usage"],
    }


def _activate_isolated_home() -> None:
    """Point HERMES_HOME at the isolated test profile, refusing the real one."""
    if Path(REAL_HOME).resolve() == Path(ISOLATED_HOME).resolve():
        print("ERROR: ISOLATED_HOME resolves to the real ~/.hermes -- refusing.", file=sys.stderr)
        sys.exit(1)
    os.environ["HERMES_HOME"] = ISOLATED_HOME

    from hermes_cli.env_loader import load_hermes_dotenv

    loaded = load_hermes_dotenv()
    print(f"loaded env from: {[str(p) for p in loaded]}")
    if Path(os.environ.get("HERMES_HOME", "")).resolve() == Path(REAL_HOME).resolve():
        print("ERROR: HERMES_HOME resolved to the real profile -- refusing.", file=sys.stderr)
        sys.exit(1)


def _flood_extend_transparency(rgba, key: tuple[int, int, int], threshold: float):
    """Grow the transparent region left by ``atlas.remove_background`` into
    connected soft-shadow/despill residue that didn't pass its stricter
    first-pass key match.

    A soft drop-shadow (blended toward the backdrop color rather than flat)
    can sit just outside ``remove_background``'s threshold, leaving a small
    patch of near-key color behind wherever it touches the ground/backdrop.
    Widening ``remove_background``'s own threshold isn't safe for a strongly
    saturated key (its fast path removes any matching pixel globally, no
    connectivity check -- see its docstring on why that punched holes in
    interior highlights before the border-flood approach existed) -- e.g. a
    green key would risk eating this character's green eyes.

    This second pass reuses the same border-flood-fill *shape* as
    ``atlas.remove_background`` (BFS over 4-connected near-key pixels), but
    seeded from the pixels ``remove_background`` already made transparent,
    not just the image border, and gated purely by connectivity: a pixel is
    only removed if reachable from already-removed background without
    crossing a pixel outside *threshold*. An isolated key-ish interior pixel
    (like an eye) stays untouched because it's surrounded by genuinely
    non-key-colored pixels, not because of a tighter color threshold.
    """
    from collections import deque

    from PIL import Image

    rgba = rgba.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()

    def _is_bg(x: int, y: int) -> bool:
        r, g, b, a = px[x, y]
        if a <= 16:
            return False
        return math.sqrt((r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2) <= threshold

    visited = bytearray(w * h)
    remove = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()

    for y in range(h):
        for x in range(w):
            if px[x, y][3] <= 16:
                idx = y * w + x
                visited[idx] = 1
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                idx = ny * w + nx
                if not visited[idx]:
                    visited[idx] = 1
                    if _is_bg(nx, ny):
                        remove[idx] = 1
                        queue.append((nx, ny))

    if not any(remove):
        return rgba

    mask = Image.frombytes("L", (w, h), bytes(remove)).point(lambda v: 255 if v else 0)
    return Image.composite(Image.new("RGBA", rgba.size, (0, 0, 0, 0)), rgba, mask)


# Loose second-pass threshold for `_flood_extend_transparency`. Measured
# against `failed` pose 3's shadow patch: shadow-tinted pixels top out
# ~110 color-distance from the auto-detected key, with a wide gap before the
# nearest real character color (~218, red/yellow scale tones) -- see
# docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md's chroma-key fix addendum.
# Kept below that gap with margin. Safe to leave generous because the pass
# is connectivity-gated, not a global color match.
DESPILL_THRESHOLD = 170.0


def _remove_background_despilled(rgba, chroma_key: tuple[int, int, int] | None, threshold: float):
    """``atlas.remove_background`` plus the shadow-despill extension above.

    Shared by both fresh generation (`generate_pose_sequence`) and
    after-the-fact reprocessing of an already-generated raw pose
    (`reprocess_pose`), so a processing-only fix never needs a new
    `imagegen.generate()` call.
    """
    from agent.pet.generate import atlas

    keyed = atlas.remove_background(rgba, chroma_key=chroma_key, threshold=threshold)
    key = chroma_key or atlas._dominant_corner_color(rgba.convert("RGBA"))  # noqa: SLF001
    return _flood_extend_transparency(keyed, key, DESPILL_THRESHOLD)


def reprocess_pose(state: str, name: str, raw_path: Path | None = None) -> Path:
    """Re-run chroma-key + fit-to-cell for an already-generated pose, no network.

    For fixing a processing defect (e.g. an unkeyed shadow) discovered after
    the fact, without spending on a new `generate()` call. Reads
    ``assets/keyframes/raw_single_pose/{state}_{name}.png`` (or *raw_path*),
    reprocesses through the exact same pipeline `generate_pose_sequence` uses
    inline, and overwrites ``assets/keyframes/processed/{state}_{name}.png``.
    Pure Pillow -- no network, no `HERMES_HOME`.
    """
    from agent.pet.generate import atlas
    from PIL import Image

    raw_path = raw_path or (RAW_OUT_DIR / f"{state}_{name}.png")
    with Image.open(raw_path) as src:
        rgba = src.convert("RGBA")
        keyed = _remove_background_despilled(rgba, chroma_key=None, threshold=90.0)
        cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / f"{state}_{name}.png"
    cell.save(out_path)
    print(f"reprocessed -> {out_path} ({cell.size[0]}x{cell.size[1]}, {cell.mode})")
    return out_path


def generate_pose_sequence(state: str, action_descriptions: list[str], n_poses: int) -> dict:
    """Generate *n_poses* real, chained poses for *state* via ``imagegen.generate()``.

    Pose 0 grounds on ``BASE_IMAGE`` alone; pose *i* (``i > 0``) grounds on
    ``BASE_IMAGE`` + pose *i-1*'s raw output, so the sequence reads as one
    chained progression rather than *n* independent grounds on the canonical
    reference. Exactly one ``generate()`` call per pose -- no retry loop, no
    fallback provider. Each pose is immediately chroma-keyed + fit-to-cell.

    Writes raw copies to ``assets/keyframes/raw_single_pose/{state}_pose{i}.png``,
    processed cells to ``assets/keyframes/processed/{state}_pose{i}.png``, and
    the full report to ``assets/keyframes/{state}_sequence_report.json``.
    Returns the report dict (also includes ``"processed_paths"``, the ordered
    list consumed by ``state_row.build_state_row``).
    """
    if len(action_descriptions) != n_poses:
        raise ValueError(f"expected {n_poses} action_descriptions, got {len(action_descriptions)}")

    _activate_isolated_home()

    if not BASE_IMAGE.is_file():
        print(f"ERROR: base image not found: {BASE_IMAGE}", file=sys.stderr)
        sys.exit(1)

    from agent.pet.generate import atlas
    from agent.pet.generate.imagegen import GenerationError, resolve_provider, generate
    from prompts_single_pose import build_single_pose_prompt

    sprite = resolve_provider(require_references=True, prefer="openrouter")
    print(f"resolved provider: name={sprite.name!r} supports_references={sprite.supports_references}")

    balance_before_run = _credits()
    print(f"balance before sequence: ${balance_before_run['balance']:.4f}")

    report: dict = {"state": state, "provider": sprite.name, "balance_before_run": balance_before_run, "poses": []}

    RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    prev_raw: Path | None = None
    for idx, action in enumerate(action_descriptions):
        name = f"pose{idx + 1}"
        reference_images = [BASE_IMAGE] if prev_raw is None else [BASE_IMAGE, prev_raw]
        prompt = build_single_pose_prompt(state, CONCEPT, style="auto", action_override=action)
        print(f"\n=== {state} {name} ===")
        print(f"grounding on: {', '.join(str(p) for p in reference_images)}")
        print(f"prompt ({len(prompt)} chars):\n{prompt}\n")

        pose_report: dict = {"name": name, "reference_images": [str(p) for p in reference_images], "prompt": prompt}
        t0 = time.monotonic()
        raw_path: Path | None = None
        try:
            # Exactly ONE call into imagegen.generate() per pose. n=1.
            paths = generate(
                prompt,
                n=1,
                reference_images=reference_images,
                provider=sprite,
                prefix=f"pet_{state}_{name}",
                aspect_ratio="square",
            )
            raw_path = paths[0]
            elapsed = time.monotonic() - t0
            pose_report.update({"status": "success", "elapsed_s": round(elapsed, 1), "raw_path": str(raw_path)})
            print(f"SUCCESS: raw image at {raw_path} elapsed={elapsed:.1f}s")
        except GenerationError as exc:
            elapsed = time.monotonic() - t0
            pose_report.update({"status": "FAIL", "error": str(exc), "elapsed_s": round(elapsed, 1)})
            print(f"FAIL (GenerationError): {exc}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - capture anything unexpected, still report balance
            elapsed = time.monotonic() - t0
            pose_report.update(
                {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "elapsed_s": round(elapsed, 1)}
            )
            print(f"FAIL (unexpected {type(exc).__name__}): {exc}", file=sys.stderr)

        if raw_path is not None:
            raw_copy = RAW_OUT_DIR / f"{state}_{name}{raw_path.suffix}"
            shutil.copyfile(raw_path, raw_copy)
            pose_report["raw_copy"] = str(raw_copy)
            print(f"copied raw -> {raw_copy}")

            try:
                from PIL import Image

                with Image.open(raw_copy) as src:
                    rgba = src.convert("RGBA")
                    keyed = _remove_background_despilled(rgba, chroma_key=None, threshold=90.0)
                    cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic
                processed_path = PROCESSED_DIR / f"{state}_{name}.png"
                cell.save(processed_path)
                pose_report["processed_path"] = str(processed_path)
                print(f"processed -> {processed_path} ({cell.size[0]}x{cell.size[1]}, {cell.mode})")
            except Exception as exc:  # noqa: BLE001
                pose_report["processing_error"] = f"{type(exc).__name__}: {exc}"
                print(f"WARNING: chroma-key/fit-to-cell processing failed: {exc}", file=sys.stderr)

        balance_after = _credits()
        pose_report["balance_after_immediate"] = balance_after
        report["poses"].append(pose_report)

        if pose_report["status"] != "success":
            print(f"\nSTOPPING: {name} failed, not attempting further poses.", file=sys.stderr)
            report["stopped_early_after"] = name
            break

        prev_raw = raw_copy  # chain: next pose grounds on THIS pose's raw output

    balance_after_run = _credits()
    report["balance_after_run_immediate"] = balance_after_run
    report["spent_usd_immediate"] = round(balance_before_run["balance"] - balance_after_run["balance"], 4)
    report["processed_paths"] = [p["processed_path"] for p in report["poses"] if "processed_path" in p]
    print(f"\nbalance after sequence (immediate): ${balance_after_run['balance']:.4f}")
    print(f"spent (immediate, may lag actual charge): ${report['spent_usd_immediate']:.4f}")

    out_report = KEYFRAMES_DIR / f"{state}_sequence_report.json"
    out_report.write_text(json.dumps(report, indent=2, default=str))
    print(f"-> {out_report}")

    if any(p["status"] != "success" for p in report["poses"]):
        sys.exit(2)

    return report
