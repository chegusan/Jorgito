"""Phase 4: install the full 9-row Jorgito atlas as a real Hermes pet.

ONLY ever run against an isolated HERMES_HOME. Installing into the real
``~/.hermes`` is Phase 5, dispatched separately after the user approves this
phase's visual gate. Rebuilds the atlas via ``full_atlas.py`` (same
deterministic build ``build_full_atlas.py`` uses) and registers it with
``agent.pet.store.register_local_pet()`` -- the same local-pet registration
path Hermes's own ``/hatch`` command uses, so ``pet.json`` / spritesheet
follow the real on-disk pet-store contract instead of an invented format.

Usage:
    HERMES_HOME=/home/chegusan/.hermes-jorgito-test \\
        /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/install_full_atlas_pet.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
if str(HERMES_SRC) not in sys.path:
    sys.path.insert(0, str(HERMES_SRC))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import full_atlas  # noqa: E402
from agent.pet import store  # noqa: E402

SLUG = "jorgito"
DISPLAY_NAME = "Jorgito"
DESCRIPTION = (
    "Jorgito -- full 9-state atlas (Phase 4): idle / running-right / "
    "running-left / waving / jumping / failed / waiting / running / review"
)


def main() -> None:
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if not hermes_home:
        print(
            "ERROR: HERMES_HOME must be set to the isolated test profile before running this.",
            file=sys.stderr,
        )
        sys.exit(1)
    if Path(hermes_home).resolve() == Path.home().resolve() / ".hermes":
        print("ERROR: refusing to run against the real ~/.hermes profile.", file=sys.stderr)
        sys.exit(1)

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
