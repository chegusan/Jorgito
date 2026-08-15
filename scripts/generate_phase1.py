"""Phase 1 minimal visual proof: generate idle/review/running rows for Jorgito.

Reuses Hermes's own pet-generation primitives (``agent.pet.generate.imagegen``,
``atlas``, ``prompts``, ``agent.pet.store``) instead of
``orchestrate.hatch_pet()``, because ``hatch_pet()`` always generates every
non-mirrored row (8 image-generation calls) in one pass. Phase 1's budget is
3 generations total -- one per requested state (idle, review, running) -- so
this script drives the same building blocks directly, grounded on
``assets/reference/jorgito_canonical.png``.

Run with the Hermes venv, HERMES_HOME pointed at the isolated test profile:

    HERMES_HOME=/home/chegusan/.hermes-jorgito-test \
        /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \
        -c "import sys; sys.path.insert(0, '/home/chegusan/.hermes/hermes-agent')" \
        scripts/generate_phase1.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

from agent.pet.generate import atlas, imagegen, prompts  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CANONICAL = REPO / "assets/reference/jorgito_canonical.png"
WORK_GENERATED = REPO / "work/generated"
BUILD_DIR = REPO / "build/phase1"

CONCEPT = (
    "Jorgito, a small friendly crimson/burgundy baby dragon with huge green "
    "eyes and visible white sclera, small tan horns, yellow-gold belly and "
    "neck plates, folded wings with red struts and yellow-gold membranes, "
    "and a long curled tail"
)

STATES = ["idle", "review", "running"]


def main() -> None:
    WORK_GENERATED.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if not CANONICAL.is_file():
        raise SystemExit(f"canonical reference not found: {CANONICAL}")

    sprite = imagegen.resolve_provider(require_references=True)
    print(f"resolved provider: {sprite.name} (supports_references={sprite.supports_references})")

    frames_by_state: dict[str, list] = {}
    manifest: list[dict] = []

    for state in STATES:
        count = atlas.FRAME_COUNTS[state]
        prompt = prompts.build_row_prompt(state, count, CONCEPT, style="auto")
        print(f"\n=== generating row: {state} ({count} frames) ===")
        strips = imagegen.generate(
            prompt,
            n=1,
            reference_images=[CANONICAL],
            provider=sprite,
            prefix=f"jorgito_phase1_{state}",
            aspect_ratio="landscape",
        )
        strip_path = strips[0]
        print(f"raw strip saved by provider at: {strip_path}")

        saved_raw = WORK_GENERATED / f"{state}_row_raw{strip_path.suffix}"
        saved_raw.write_bytes(strip_path.read_bytes())

        frames = atlas.extract_strip_frames(strip_path, count, method="auto", fit=False)
        frames_by_state[state] = frames
        manifest.append(
            {
                "state": state,
                "frame_count": count,
                "raw_strip": str(saved_raw.relative_to(REPO)),
                "provider": sprite.name,
            }
        )
        print(f"extracted {len(frames)} frames for '{state}'")

    print("\n=== normalizing + composing atlas (3/9 rows filled) ===")
    normalized = atlas.normalize_cells(frames_by_state)
    sheet = atlas.compose_atlas(normalized)
    validation = atlas.validate_atlas(sheet)
    print(json.dumps(validation, indent=2))

    atlas_path = BUILD_DIR / "jorgito_phase1_atlas.webp"
    atlas_bytes = atlas.atlas_to_webp_bytes(sheet)
    atlas_path.write_bytes(atlas_bytes)
    print(f"\natlas written: {atlas_path} ({len(atlas_bytes)} bytes)")

    manifest_path = BUILD_DIR / "generation_manifest.json"
    manifest_path.write_text(
        json.dumps({"states": manifest, "validation": validation}, indent=2),
        encoding="utf-8",
    )
    print(f"manifest written: {manifest_path}")

    if not validation["ok"]:
        raise SystemExit(f"atlas validation FAILED: {validation['errors']}")

    print("\n=== installing as temporary test pet 'jorgito-test' ===")
    from agent.pet import store

    pet = store.register_local_pet(
        sheet,
        slug="jorgito-test",
        display_name="Jorgito (Phase 1 test)",
        description="Phase 1 minimal visual proof -- idle/review/running only.",
    )
    print(f"installed: {pet.slug} -> {pet.spritesheet}")


if __name__ == "__main__":
    main()
