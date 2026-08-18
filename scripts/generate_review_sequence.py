"""Phase 2B addendum #2: real pose variation for the ``review`` row.

The single-pose pilot (``scripts/generate_single_pose.py``, addendum #1)
proved the segmentation problem goes away with one-pose-per-call generation,
but the human flagged that a single static pose wobbled by
``scripts/build_review_row.py``'s deterministic bob/tilt/scale math isn't
real animation -- it just guarantees the row's frame hashes aren't
byte-identical. This script generates the two ADDITIONAL real poses needed
for a genuine page-turning progression (pose 1 already exists from the
pilot): book closed/starting (pose 1, existing) -> mid-page-turn (pose 2,
new) -> page turned further along (pose 3, new).

Same primitive as the pilot -- ``imagegen.generate(prompt, n=1,
reference_images=[...], provider=...)`` -- called exactly ONCE per new pose
(twice total for this script), no retry loop, no fallback provider. Each new
pose is grounded on BOTH ``assets/reference/jorgito_canonical.png`` (identity
lock) AND the immediately-preceding pose's raw generated image (continuity of
motion), per ``generate()``'s documented ``reference_images: list[Path]``
support -- so pose 3 is grounded on canonical + pose 2's raw output, not
pose 1's, keeping the progression chained rather than three independent
grounds on the same single image.

ONLY ever run against the isolated HERMES_HOME test profile -- same refusal
guard as ``scripts/generate_single_pose.py`` / ``scripts/hatch_pet_run.py``.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_review_sequence.py
"""

from __future__ import annotations

import json
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
sys.path.insert(0, str(REPO / "scripts"))

BASE_IMAGE = REPO / "assets/reference/jorgito_canonical.png"
STATE = "review"
CONCEPT = (
    "a small friendly Petdex-style pixel-art dragon mascot, crimson/burgundy "
    "body, large green eyes, yellow belly/neck plates and wing membranes, "
    "red wings, curled tail"
)

# Pose 1 already exists from the single-pose pilot (addendum #1) -- this
# script generates poses 2 and 3 only, each grounded on canonical + the
# immediately-preceding pose's raw image.
POSE1_RAW = REPO / "assets/keyframes/raw_single_pose/review.png"

RAW_OUT_DIR = REPO / "assets/keyframes/raw_single_pose"
PROCESSED_DIR = REPO / "assets/keyframes/processed"
OUT_REPORT = REPO / "assets/keyframes/review_sequence_report.json"

# Page-turn progression: pose 1 (existing) is the "book closed/starting"
# pose from _STATE_ACTIONS in prompts_single_pose.py. Poses 2/3 continue the
# same action ("Jorgito thinking/reading: sitting or standing with a small
# pair of reading glasses on, holding an open book up in front of them, head
# tilted slightly down as if studying the page intently") into two further
# page-turn moments, keeping every other descriptive detail identical so
# only the page/hand position changes between generations.
POSES: list[dict] = [
    {
        "name": "pose2_midturn",
        "prev_raw": POSE1_RAW,
        "action": (
            "Jorgito thinking/reading, mid-page-turn: sitting or standing with "
            "a small pair of reading glasses on, holding an open book up in "
            "front of them, one hand lifted up and away from the book with a "
            "page caught mid-flip curling up in the air between the fingers, "
            "head still tilted slightly down toward the book as if watching "
            "the page turn"
        ),
    },
    {
        "name": "pose3_turned",
        "prev_raw": None,  # filled in with pose2's raw path after it generates
        "action": (
            "Jorgito thinking/reading, having just turned to a new page: "
            "sitting or standing with a small pair of reading glasses on, "
            "holding an open book up in front of them, the turned page now "
            "lying flat and the hand resting back down on the book, head "
            "tilted slightly down continuing to study the new page intently"
        ),
    },
]


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


def main() -> None:
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

    if not BASE_IMAGE.is_file():
        print(f"ERROR: base image not found: {BASE_IMAGE}", file=sys.stderr)
        sys.exit(1)
    if not POSE1_RAW.is_file():
        print(f"ERROR: pose 1 raw image not found: {POSE1_RAW}", file=sys.stderr)
        sys.exit(1)

    from agent.pet.generate import atlas
    from agent.pet.generate.imagegen import GenerationError, resolve_provider, generate

    from prompts_single_pose import build_single_pose_prompt

    sprite = resolve_provider(require_references=True, prefer="openrouter")
    print(f"resolved provider: name={sprite.name!r} supports_references={sprite.supports_references}")

    balance_before_run = _credits()
    print(f"balance before sequence: ${balance_before_run['balance']:.4f}")

    report: dict = {"state": STATE, "provider": sprite.name, "balance_before_run": balance_before_run, "poses": []}

    prev_raw = POSE1_RAW
    RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for spec in POSES:
        name = spec["name"]
        prompt = build_single_pose_prompt(STATE, CONCEPT, style="auto", action_override=spec["action"])
        print(f"\n=== {name} ===")
        print(f"grounding on: canonical + {prev_raw}")
        print(f"prompt ({len(prompt)} chars):\n{prompt}\n")

        pose_report: dict = {"name": name, "reference_images": [str(BASE_IMAGE), str(prev_raw)], "prompt": prompt}
        balance_before = _credits()

        t0 = time.monotonic()
        raw_path: Path | None = None
        try:
            # Exactly ONE call into imagegen.generate() per pose. n=1.
            paths = generate(
                prompt,
                n=1,
                reference_images=[BASE_IMAGE, prev_raw],
                provider=sprite,
                prefix=f"pet_review_{name}",
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
            raw_copy = RAW_OUT_DIR / f"review_{name}{raw_path.suffix}"
            shutil.copyfile(raw_path, raw_copy)
            pose_report["raw_copy"] = str(raw_copy)
            print(f"copied raw -> {raw_copy}")

            try:
                from PIL import Image

                with Image.open(raw_copy) as src:
                    rgba = src.convert("RGBA")
                    keyed = atlas.remove_background(rgba, chroma_key=None, threshold=90.0)
                    cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic
                processed_path = PROCESSED_DIR / f"review_{name}.png"
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

        # Chain: next pose grounds on this pose's raw output, not pose 1's.
        prev_raw = raw_copy

    balance_after_run = _credits()
    report["balance_after_run_immediate"] = balance_after_run
    report["spent_usd_immediate"] = round(balance_before_run["balance"] - balance_after_run["balance"], 4)
    print(f"\nbalance after sequence (immediate): ${balance_after_run['balance']:.4f}")
    print(f"spent (immediate, may lag actual charge): ${report['spent_usd_immediate']:.4f}")

    OUT_REPORT.write_text(json.dumps(report, indent=2, default=str))
    print(f"-> {OUT_REPORT}")

    if any(p["status"] != "success" for p in report["poses"]):
        sys.exit(2)


if __name__ == "__main__":
    main()
