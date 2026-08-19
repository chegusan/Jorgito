"""Test bootstrap: make the scripts/ modules importable without the Hermes
source tree installed.

The pipeline scripts do ``from agent.pet.generate import atlas`` at module
import time (see AUDIT_REPORT.md F-4: that module-level coupling is what
currently blocks importing the pure helpers any other way). The Hermes source
is not available in CI or on a fresh checkout, so we install a *minimal*
stand-in that satisfies only the surface the units under test actually touch:

  - ``atlas.CELL_WIDTH`` / ``atlas.CELL_HEIGHT`` — read by
    ``keyframe_processing.build_contact_sheet``.

``full_atlas._vary`` touches none of the stub. The stub's cell dimensions are
deliberately tiny and distinctive so contact-sheet geometry assertions test
the function's own formula rather than real Hermes constants.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

# Stub cell dimensions — intentionally not the real Hermes 192x208 so that a
# geometry test asserting sheet size in terms of these proves the formula, not
# a coincidence with production constants.
STUB_CELL_WIDTH = 8
STUB_CELL_HEIGHT = 10


def _install_hermes_stub() -> None:
    if "agent.pet.generate.atlas" in sys.modules:
        return
    agent = types.ModuleType("agent")
    pet = types.ModuleType("agent.pet")
    generate = types.ModuleType("agent.pet.generate")
    atlas = types.ModuleType("agent.pet.generate.atlas")
    atlas.CELL_WIDTH = STUB_CELL_WIDTH
    atlas.CELL_HEIGHT = STUB_CELL_HEIGHT
    agent.pet = pet  # type: ignore[attr-defined]
    pet.generate = generate  # type: ignore[attr-defined]
    generate.atlas = atlas  # type: ignore[attr-defined]
    sys.modules.update(
        {
            "agent": agent,
            "agent.pet": pet,
            "agent.pet.generate": generate,
            "agent.pet.generate.atlas": atlas,
        }
    )


_install_hermes_stub()

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
