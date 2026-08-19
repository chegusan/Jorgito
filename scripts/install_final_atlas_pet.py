"""Install the final 9-row Jorgito atlas as a real Hermes pet -- ISOLATED PROFILE ONLY.

Reuses ``agent.pet.store.register_local_pet()`` -- the same local-pet
registration path Hermes's own ``/hatch`` command and the earlier
``install_full_atlas_pet.py`` (Phase 4) use -- so ``pet.json`` / spritesheet
follow the real on-disk pet-store contract. Refuses to run against the real
``~/.hermes``; Phase 5 (installing into the user's production Hermes) is a
separate, later task after this atlas is approved.

Usage:
    HERMES_HOME=/home/chegusan/.hermes-jorgito-test \\
        /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/install_final_atlas_pet.py
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

import build_final_atlas  # noqa: E402
from agent.pet import store  # noqa: E402

SLUG = "jorgito"
DISPLAY_NAME = "Jorgito"
DESCRIPTION = (
    "Jorgito -- final 9-state atlas (Phase Final): idle / running-right / "
    "running-left / waving / jumping / failed / waiting / running / review. "
    "Reconciled from PR #3, #6, #7, #8, #5 -- no new generation."
)


def main() -> None:
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if not hermes_home:
        print(
            "ERROR: HERMES_HOME must be set to the isolated test profile before running this.",
            file=sys.stderr,
        )
        sys.exit(1)
    if Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve():
        print("ERROR: refusing to run against the real ~/.hermes profile.", file=sys.stderr)
        sys.exit(1)

    print(f"HERMES_HOME={hermes_home}")

    atlas_image, report, _frames_by_state = build_final_atlas.build_and_validate()
    if not report["validate_atlas"]["ok"] or not report["all_rows_unique"] or report["states_filled"] != 9:
        print("ERROR: final atlas failed validation, refusing to install:", file=sys.stderr)
        print(report, file=sys.stderr)
        sys.exit(1)
    print(f"validate_atlas(): ok=True, filled_states={report['states_filled']}/9, all_rows_unique=True")

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
