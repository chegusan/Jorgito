"""Install the final 9-row Jorgito atlas as a real Hermes pet -- REAL PROFILE ONLY.

Phase 5. This is the intentional counterpart to ``install_final_atlas_pet.py``,
which exists specifically to *refuse* the real ``~/.hermes`` profile. This
script does the opposite: it is the only script in this project meant to
write into the user's production Hermes install. Because of that it requires
an explicit, unambiguous opt-in (``CONFIRM_REAL_INSTALL=yes``) on top of the
normal atlas re-validation, and it pins ``HERMES_HOME`` to the real profile
itself rather than trusting an unset/ambient value.

Reuses ``build_final_atlas.build_and_validate()`` (no regeneration, same
atlas already visually approved in PR #9) and Hermes's real
``agent.pet.store.register_local_pet()`` -- the same local-pet registration
path ``/hatch`` and ``install_final_atlas_pet.py`` use.

Usage:
    CONFIRM_REAL_INSTALL=yes \\
        /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/install_real_pet.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REAL_HERMES_HOME = Path.home() / ".hermes"

HERMES_SRC = REAL_HERMES_HOME / "hermes-agent"
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
    if os.environ.get("CONFIRM_REAL_INSTALL", "").strip() != "yes":
        print(
            "ERROR: refusing to install into the real ~/.hermes profile without "
            "explicit confirmation. Set CONFIRM_REAL_INSTALL=yes to proceed.",
            file=sys.stderr,
        )
        sys.exit(1)

    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if hermes_home and Path(hermes_home).resolve() != REAL_HERMES_HOME.resolve():
        print(
            f"ERROR: HERMES_HOME={hermes_home!r} does not point at the real "
            f"profile ({REAL_HERMES_HOME}). This script only installs into the "
            "real profile; use install_final_atlas_pet.py for isolated profiles.",
            file=sys.stderr,
        )
        sys.exit(1)
    os.environ["HERMES_HOME"] = str(REAL_HERMES_HOME)

    print(f"HERMES_HOME={os.environ['HERMES_HOME']} (real profile, pinned)")

    atlas_image, report, _frames_by_state = build_final_atlas.build_and_validate()
    if not report["validate_atlas"]["ok"] or not report["all_rows_unique"] or report["states_filled"] != 9:
        print("ERROR: final atlas failed re-validation, refusing to install:", file=sys.stderr)
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
