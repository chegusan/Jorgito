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

    Refuses to run when ``HERMES_HOME`` is unset, when it resolves to the real
    ``~/.hermes`` profile, or when it resolves to anything *inside* the real
    profile. This is the single owner of that safety check — previously
    duplicated in four scripts, where a fix to one copy would have silently
    left the others behind.

    Two things must both be resolved before comparing, or the check is
    bypassable:

    - ``Path(hermes_home).resolve()`` always follows any symlink in
      ``hermes_home`` itself, so the real ``~/.hermes`` side of the comparison
      must be resolved too (``(Path.home() / ".hermes").resolve()``, not
      ``Path.home().resolve() / ".hermes"``) — otherwise, if ``~/.hermes`` is
      itself a symlink (a common dotfile-manager setup, e.g. stow/chezmoi),
      the two sides never compare equal and the guard silently lets the
      script run against the real profile's data.
    - A strict ``==`` alone still misses ``HERMES_HOME`` pointing at a
      *subdirectory* of the real ``~/.hermes`` (e.g. ``~/.hermes/pets``, or a
      symlink resolving there) — the script would then write within the real
      profile's data. Rejecting any resolved path that has the real
      ``~/.hermes`` among its parents closes that gap too.

    Both bypasses were found and confirmed against this exact guard by two
    independent cross-reviews; see ``tests/test_hermes_env.py`` for the
    regression coverage.
    """
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if not hermes_home:
        print(
            "ERROR: HERMES_HOME must be set to the isolated test profile before running this.",
            file=sys.stderr,
        )
        sys.exit(1)
    hermes_resolved = Path(hermes_home).resolve()
    real_hermes = (Path.home() / ".hermes").resolve()
    if hermes_resolved == real_hermes or real_hermes in hermes_resolved.parents:
        print("ERROR: refusing to run against or within the real ~/.hermes profile.", file=sys.stderr)
        sys.exit(1)
    return hermes_home
