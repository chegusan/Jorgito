"""Phase 4: install the full 9-row Jorgito atlas as a real Hermes pet.

ONLY ever run against an isolated HERMES_HOME. Installing into the real
``~/.hermes`` is Phase 5, dispatched separately after the user approves this
phase's visual gate. Rebuilds the atlas via ``full_atlas.py`` (same
deterministic build ``build_full_atlas.py`` uses) and registers it with
``agent.pet.store.register_local_pet()`` -- the same local-pet registration
path Hermes's own ``/hatch`` command uses, so ``pet.json`` / spritesheet
follow the real on-disk pet-store contract instead of an invented format.

Usage (HERMES_AGENT_SRC overrides the Hermes source location; see
scripts/hermes_env.py):
    HERMES_HOME=/path/to/isolated-profile \\
        HERMES_AGENT_SRC=/path/to/hermes-agent \\
        /path/to/hermes-agent/venv/bin/python3 scripts/install_full_atlas_pet.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_env import ensure_hermes_on_path, require_isolated_hermes_home  # noqa: E402

ensure_hermes_on_path()

import full_atlas  # noqa: E402
from agent.pet import store  # noqa: E402

SLUG = "jorgito"
DISPLAY_NAME = "Jorgito"
DESCRIPTION = (
    "Jorgito -- full 9-state atlas (Phase 4): idle / running-right / "
    "running-left / waving / jumping / failed / waiting / running / review"
)


def main() -> None:
    hermes_home = require_isolated_hermes_home()

    print(f"HERMES_HOME={hermes_home}")

    atlas_image = full_atlas.build_atlas_image()
    report = full_atlas.validate(atlas_image)
    if not report["ok"]:
        print("ERROR: atlas failed validate_atlas(), refusing to install:", file=sys.stderr)
        print(report, file=sys.stderr)
        sys.exit(1)
    print(f"validate_atlas(): ok=True, filled_states={report['filled_states']}")

    pet = store.register_local_pet(
        atlas_image,
        slug=SLUG,
        display_name=DISPLAY_NAME,
        description=DESCRIPTION,
    )
    print(f"registered pet '{pet.slug}' -> {pet.spritesheet}")
    print(f"  exists={pet.exists} generated={pet.generated}")


if __name__ == "__main__":
    main()
