"""Phase 2B: fire Hermes's native AI generation pipeline (``hatch_pet()``) to
produce a REAL multi-pose animation atlas for Jorgito, grounded on the
approved reference image, superseding the deterministic ``_vary()``
sine-wave transform from Phase 3/4.

ONLY ever run against the isolated HERMES_HOME test profile. Refuses to run
if HERMES_HOME resolves to the real ``~/.hermes``. Installs under slug
``jorgito-hatch`` (not ``jorgito``) so it does not collide with the existing
Phase 4 deterministic-transform pet already installed under that slug in the
same isolated profile.

Checks the real (free, no-cost) OpenRouter ``/credits`` balance immediately
before and after the hatch call and writes a JSON report with the exact
delta, per-state progress log, and either the HatchResult or the captured
GenerationError.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/hatch_pet_run.py
"""

from __future__ import annotations

import json
import os
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
BASE_IMAGE = REPO / "assets/reference/jorgito_canonical.png"
SLUG = "jorgito-hatch"
DISPLAY_NAME = "Jorgito"
CONCEPT = (
    "a small friendly Petdex-style pixel-art dragon mascot, crimson/burgundy "
    "body, large green eyes, yellow belly/neck plates and wing membranes, "
    "red wings, curled tail"
)
OUT_REPORT = REPO / "assets/keyframes/hatch_pet_report.json"


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

    from agent.pet.generate import GenerationError, hatch_pet
    from agent.pet.generate.imagegen import resolve_provider

    sprite = resolve_provider(require_references=True, prefer="openrouter")
    print(f"resolved provider: name={sprite.name!r} supports_references={sprite.supports_references}")

    progress_log: list[dict] = []

    def on_progress(event: str, detail: str) -> None:
        entry = {"t": round(time.monotonic(), 2), "event": event, "detail": detail}
        progress_log.append(entry)
        print(f"[progress] {event}: {detail}")

    report: dict = {
        "slug": SLUG,
        "provider": sprite.name,
        "balance_before": balance_before,
    }

    t0 = time.monotonic()
    try:
        result = hatch_pet(
            base_image=str(BASE_IMAGE),
            slug=SLUG,
            display_name=DISPLAY_NAME,
            concept=CONCEPT,
            provider=sprite,
            on_progress=on_progress,
        )
        elapsed = time.monotonic() - t0
        report.update(
            {
                "status": "success",
                "elapsed_s": round(elapsed, 1),
                "result": {
                    "slug": result.slug,
                    "display_name": result.display_name,
                    "spritesheet": str(result.spritesheet),
                    "states": sorted(result.states),
                    "validation": result.validation,
                },
            }
        )
        print(f"SUCCESS: slug={result.slug} states={sorted(result.states)} elapsed={elapsed:.1f}s")
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

    balance_after = _credits()
    report["balance_after"] = balance_after
    report["spent_usd"] = round(balance_before["balance"] - balance_after["balance"], 4)
    report["progress_log"] = progress_log
    print(f"balance after: ${balance_after['balance']:.4f}")
    print(f"spent: ${report['spent_usd']:.4f}")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(report, indent=2, default=str))
    print(f"-> {OUT_REPORT}")

    if report["status"] != "success":
        sys.exit(2)


if __name__ == "__main__":
    main()
