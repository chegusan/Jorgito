"""Phase 2B pilot: single-pose-per-call generation for ONE state (``review``).

Tests whether asking the model for one centered pose per API call (instead of
a multi-pose row strip) sidesteps the segmentation failures documented in
``docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md`` -- ``review`` was one of
the 4 states that failed there ("frame 3 contains multiple separated
subjects"), which makes it a good test of whether this fixes the problem.

Calls ``imagegen.generate(prompt, n=1, reference_images=[...], provider=...)``
directly (the same primitive ``generate_base_drafts()`` uses in production,
already single-image-per-call, no strip/slicing) with a prompt built by the
new ``scripts/prompts_single_pose.build_single_pose_prompt()``. Exactly ONE
top-level call into that function for this run -- no retry loop, no fallback
to another provider. (``imagegen.generate()`` itself may issue a second HTTP
call internally IF AND ONLY IF the first response is rejected specifically
for the ``background=transparent`` param -- that's existing production
behavior in the read-only Hermes primitive, not a retry loop added here.)

ONLY ever run against the isolated HERMES_HOME test profile -- same guardrail
as ``scripts/hatch_pet_run.py``: refuses if HERMES_HOME resolves to the real
``~/.hermes``.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/generate_single_pose.py
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

RAW_OUT_DIR = REPO / "assets/keyframes/raw_single_pose"
PROCESSED_OUT = REPO / "assets/keyframes/processed" / f"{STATE}_singlepose_pilot.png"
OUT_REPORT = REPO / "assets/keyframes/single_pose_pilot_report.json"


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

    balance_before = _credits()
    print(f"balance before: ${balance_before['balance']:.4f}")

    from agent.pet.generate import atlas
    from agent.pet.generate.imagegen import GenerationError, resolve_provider, generate

    from prompts_single_pose import build_single_pose_prompt

    sprite = resolve_provider(require_references=True, prefer="openrouter")
    print(f"resolved provider: name={sprite.name!r} supports_references={sprite.supports_references}")

    prompt = build_single_pose_prompt(STATE, CONCEPT, style="auto")
    print(f"prompt ({len(prompt)} chars):\n{prompt}\n")

    report: dict = {
        "state": STATE,
        "provider": sprite.name,
        "balance_before": balance_before,
        "prompt": prompt,
    }

    t0 = time.monotonic()
    raw_path: Path | None = None
    try:
        # Exactly ONE call into imagegen.generate() for this whole run. n=1.
        paths = generate(
            prompt,
            n=1,
            reference_images=[BASE_IMAGE],
            provider=sprite,
            prefix="pet_single_pose_review",
            aspect_ratio="square",
        )
        raw_path = paths[0]
        elapsed = time.monotonic() - t0
        report.update({"status": "success", "elapsed_s": round(elapsed, 1), "raw_path": str(raw_path)})
        print(f"SUCCESS: raw image at {raw_path} elapsed={elapsed:.1f}s")
    except GenerationError as exc:
        elapsed = time.monotonic() - t0
        report.update({"status": "FAIL", "error": str(exc), "elapsed_s": round(elapsed, 1)})
        print(f"FAIL (GenerationError): {exc}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - capture anything unexpected, still report balance
        elapsed = time.monotonic() - t0
        report.update(
            {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "elapsed_s": round(elapsed, 1)}
        )
        print(f"FAIL (unexpected {type(exc).__name__}): {exc}", file=sys.stderr)

    if raw_path is not None:
        RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)
        raw_copy = RAW_OUT_DIR / f"{STATE}{raw_path.suffix}"
        shutil.copyfile(raw_path, raw_copy)
        report["raw_copy"] = str(raw_copy)
        print(f"copied raw -> {raw_copy}")

        try:
            from PIL import Image

            with Image.open(raw_copy) as src:
                rgba = src.convert("RGBA")
                # Same chroma-key + fit-to-cell primitives keyframe_processing.py
                # wraps (atlas.remove_background / atlas._fit_to_cell), applied
                # directly to this single generated image rather than through a
                # raw_dir/{state}.jpeg-shaped helper.
                keyed = atlas.remove_background(rgba, chroma_key=None, threshold=90.0)
                cell = atlas._fit_to_cell(keyed)  # noqa: SLF001 - reusing project's own fit logic
            PROCESSED_OUT.parent.mkdir(parents=True, exist_ok=True)
            cell.save(PROCESSED_OUT)
            report["processed_path"] = str(PROCESSED_OUT)
            print(f"processed -> {PROCESSED_OUT} ({cell.size[0]}x{cell.size[1]}, {cell.mode})")
        except Exception as exc:  # noqa: BLE001
            report["processing_error"] = f"{type(exc).__name__}: {exc}"
            print(f"WARNING: chroma-key/fit-to-cell processing failed: {exc}", file=sys.stderr)

    balance_after = _credits()
    report["balance_after"] = balance_after
    report["spent_usd"] = round(balance_before["balance"] - balance_after["balance"], 4)
    print(f"balance after: ${balance_after['balance']:.4f}")
    print(f"spent: ${report['spent_usd']:.4f}")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(report, indent=2, default=str))
    print(f"-> {OUT_REPORT}")

    if report["status"] != "success":
        sys.exit(2)


if __name__ == "__main__":
    main()
