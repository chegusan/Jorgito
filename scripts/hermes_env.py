"""Single owner for Hermes-integration environment concerns.

Every pipeline script needs the same two things before it can touch Hermes:

1. the upstream Hermes agent source on ``sys.path`` so ``agent.pet.*`` imports
   resolve;
2. (for scripts that write a pet store) a guarantee that they are pointed at an
   *isolated* ``HERMES_HOME`` and never the real ``~/.hermes`` profile.

Both used to be copy-pasted into every script — the Hermes path was even
hardcoded to one developer's absolute home directory (13 copies), and the
"refuse to run against the real ~/.hermes" safety guard was duplicated verbatim
in four scripts. This module makes each concept have exactly one owner (per
docs/02_FILE_AND_CODE_RULES.md) and removes the machine-specific hardcoding
(AUDIT_REPORT.md F-1/F-2).

This module intentionally imports nothing from Hermes, so it is safe to import
anywhere (including in tests, with no Hermes source present).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Fallback location for the Hermes agent source. Overridable via the
# ``HERMES_AGENT_SRC`` environment variable so the pipeline is not pinned to one
# developer's machine (AUDIT_REPORT.md F-1). The default preserves the original
# path so existing local runs keep working with no configuration.
DEFAULT_HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")

# Environment variable that overrides the Hermes source location.
HERMES_SRC_ENV = "HERMES_AGENT_SRC"


def hermes_src() -> Path:
    """Resolved location of the Hermes agent source tree."""
    override = os.environ.get(HERMES_SRC_ENV, "").strip()
    return Path(override) if override else DEFAULT_HERMES_SRC


def ensure_hermes_on_path() -> Path:
    """Put the Hermes agent source on ``sys.path`` (idempotent).

    Returns the resolved path so callers can log or assert on it.
    """
    src = hermes_src()
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return src


def require_isolated_hermes_home() -> str:
    """Return ``HERMES_HOME``, or exit(1) if it is unsafe to proceed.

    Refuses to run when ``HERMES_HOME`` is unset, or when it resolves to the
    real ``~/.hermes`` profile. This is the single owner of that safety check —
    previously duplicated in four scripts, where a fix to one copy would have
    silently left the others behind.
    """
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
    return hermes_home
