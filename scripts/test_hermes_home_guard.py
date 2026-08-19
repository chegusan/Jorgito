"""Regression test for the ``~/.hermes`` real-profile guard bypass (opencode
cross-review of PR #9, 2026-08-19).

Reproduces the exact scenario the reviewer found: if the user's ``~/.hermes``
is ever a symlink (e.g. a dotfile manager like stow/chezmoi pointing it at a
managed target directory), the OLD guard --

    Path(hermes_home).resolve() == Path.home().resolve() / ".hermes"

-- only resolves ``Path.home()``, not the ``.hermes`` component appended
after it. So the RHS stays the *unresolved* symlink path while the LHS
always resolves fully (``Path(hermes_home).resolve()`` follows any symlink
in ``hermes_home`` itself) -- they never compare equal whenever ``~/.hermes``
is a symlink, whether the caller passes that symlink path directly or its
resolved target. Either way the guard silently lets the script run against
the real profile's data.

The FIXED guard resolves the whole RHS path (symlink included) --

    Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve()

-- so both sides land on the same real directory and the bypass is caught.

Run directly: ``python3 scripts/test_hermes_home_guard.py``. Exits non-zero
on any failed assertion. No writes outside a throwaway ``TemporaryDirectory``;
never touches the real ``~/.hermes``.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest import mock


def old_guard_is_real_profile(hermes_home: str, fake_home: Path) -> bool:
    """Verbatim pre-fix guard condition (the bug)."""
    with mock.patch.object(Path, "home", return_value=fake_home):
        return Path(hermes_home).resolve() == Path.home().resolve() / ".hermes"


def new_guard_is_real_profile(hermes_home: str, fake_home: Path) -> bool:
    """Verbatim post-fix guard condition."""
    with mock.patch.object(Path, "home", return_value=fake_home):
        return Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve()


def main() -> None:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        fake_home = Path(tmp)
        real_target = fake_home / "dotfiles" / "hermes-config"
        real_target.mkdir(parents=True)
        symlinked_hermes = fake_home / ".hermes"
        symlinked_hermes.symlink_to(real_target, target_is_directory=True)

        isolated_profile = fake_home / "hermes-jorgito-test"
        isolated_profile.mkdir()

        # 1. Reproduce the bypass: caller passes the symlink's REAL TARGET
        #    directly (same on-disk data as ~/.hermes, different literal
        #    path). Old guard must have failed to catch this (that's the bug
        #    we're regression-testing against); new guard must catch it.
        old_result = old_guard_is_real_profile(str(real_target), fake_home)
        new_result = new_guard_is_real_profile(str(real_target), fake_home)
        print(f"[bypass via symlink target] old_guard blocks={old_result} new_guard blocks={new_result}")
        if old_result is not False:
            failures.append("expected OLD guard to FAIL to block the symlink-target bypass (old_result should be False)")
        if new_result is not True:
            failures.append("expected NEW guard to BLOCK the symlink-target bypass (new_result should be True)")

        # 2. Passing ~/.hermes's own symlink path directly is ALSO broken
        #    under the old guard: `Path(hermes_home).resolve()` follows the
        #    symlink to `real_target` on the LHS regardless of which form
        #    the caller passed, while the RHS stays the unresolved literal
        #    `<home>/.hermes` -- so the old guard fails to block even this
        #    direct, unmodified case whenever ~/.hermes is a symlink. The
        #    new guard resolves the RHS too and blocks it correctly.
        old_direct = old_guard_is_real_profile(str(symlinked_hermes), fake_home)
        new_direct = new_guard_is_real_profile(str(symlinked_hermes), fake_home)
        print(f"[direct symlink path]      old_guard blocks={old_direct} new_guard blocks={new_direct}")
        if old_direct is not False:
            failures.append("expected OLD guard to FAIL to block the direct symlink path too (old_result should be False)")
        if new_direct is not True:
            failures.append("expected NEW guard to BLOCK the direct symlink path")

        # 3. No false positive: a genuinely different isolated profile must
        #    never be blocked by either guard.
        old_isolated = old_guard_is_real_profile(str(isolated_profile), fake_home)
        new_isolated = new_guard_is_real_profile(str(isolated_profile), fake_home)
        print(f"[isolated profile]         old_guard blocks={old_isolated} new_guard blocks={new_isolated}")
        if old_isolated or new_isolated:
            failures.append("expected NEITHER guard to block a genuinely isolated profile (false positive)")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("\nAll checks passed: the symlink bypass is reproduced against the old guard and closed by the new one.")


if __name__ == "__main__":
    main()
