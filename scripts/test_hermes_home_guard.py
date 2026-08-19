"""Regression test for the ``~/.hermes`` real-profile guard bypasses found by
two independent opencode cross-reviews of PR #9 (2026-08-19).

Round 1 bug -- symlinked ``~/.hermes``: if the user's ``~/.hermes`` is ever a
symlink (e.g. a dotfile manager like stow/chezmoi pointing it at a managed
target directory), the ORIGINAL guard --

    Path(hermes_home).resolve() == Path.home().resolve() / ".hermes"

-- only resolves ``Path.home()``, not the ``.hermes`` component appended
after it. So the RHS stays the *unresolved* symlink path while the LHS
always resolves fully (``Path(hermes_home).resolve()`` follows any symlink
in ``hermes_home`` itself) -- they never compare equal whenever ``~/.hermes``
is a symlink, whether the caller passes that symlink path directly or its
resolved target.

Round 1 fix -- resolve the whole RHS path too:

    Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve()

Round 2 bug -- subdirectory of the real ``~/.hermes``: the round-1 fix is
still a strict ``==``, so it never fires when ``HERMES_HOME`` points *inside*
the real profile (e.g. ``~/.hermes/pets``, or a symlink that resolves to a
subdirectory of it) -- the script would then write within the real profile's
data (e.g. ``~/.hermes/pets/pets/``).

Round 2 fix -- also reject any ``hermes_home`` that is a descendant of the
real ``~/.hermes``:

    hermes_resolved = Path(hermes_home).resolve()
    real_hermes = (Path.home() / ".hermes").resolve()
    hermes_resolved == real_hermes or real_hermes in hermes_resolved.parents

Run directly: ``python3 scripts/test_hermes_home_guard.py``. Exits non-zero
on any failed assertion. No writes outside a throwaway ``TemporaryDirectory``;
never touches the real ``~/.hermes``.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest import mock


def original_guard_blocks(hermes_home: str, fake_home: Path) -> bool:
    """Verbatim pre-round-1-fix guard condition (round 1 bug)."""
    with mock.patch.object(Path, "home", return_value=fake_home):
        return Path(hermes_home).resolve() == Path.home().resolve() / ".hermes"


def equality_only_guard_blocks(hermes_home: str, fake_home: Path) -> bool:
    """Verbatim round-1-fix guard condition (fixes symlinks, still vulnerable
    to a HERMES_HOME pointing at a subdirectory of the real ~/.hermes -- the
    round 2 bug)."""
    with mock.patch.object(Path, "home", return_value=fake_home):
        return Path(hermes_home).resolve() == (Path.home() / ".hermes").resolve()


def descendant_aware_guard_blocks(hermes_home: str, fake_home: Path) -> bool:
    """Verbatim round-2-fix guard condition (current, in both scripts)."""
    with mock.patch.object(Path, "home", return_value=fake_home):
        hermes_resolved = Path(hermes_home).resolve()
        real_hermes = (Path.home() / ".hermes").resolve()
        return hermes_resolved == real_hermes or real_hermes in hermes_resolved.parents


def main() -> None:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        fake_home = Path(tmp)
        real_target = fake_home / "dotfiles" / "hermes-config"
        real_target.mkdir(parents=True)
        symlinked_hermes = fake_home / ".hermes"
        symlinked_hermes.symlink_to(real_target, target_is_directory=True)

        # A subdirectory *inside* the real profile, reachable two ways: the
        # literal path through the symlink, and the resolved path under the
        # symlink's target. Both must be rejected by the round-2 guard.
        subdir_via_symlink = symlinked_hermes / "pets"
        subdir_via_symlink.mkdir()
        subdir_via_target = real_target / "pets"  # same on-disk dir as above

        isolated_profile = fake_home / "hermes-jorgito-test"
        isolated_profile.mkdir()

        def check(label: str, hermes_home: str, *, expect_original: bool, expect_equality_only: bool, expect_descendant_aware: bool) -> None:
            original = original_guard_blocks(hermes_home, fake_home)
            equality_only = equality_only_guard_blocks(hermes_home, fake_home)
            descendant_aware = descendant_aware_guard_blocks(hermes_home, fake_home)
            print(
                f"[{label}] original blocks={original} equality_only blocks={equality_only} "
                f"descendant_aware blocks={descendant_aware}"
            )
            if original is not expect_original:
                failures.append(f"{label}: expected original guard blocks={expect_original}, got {original}")
            if equality_only is not expect_equality_only:
                failures.append(f"{label}: expected equality_only guard blocks={expect_equality_only}, got {equality_only}")
            if descendant_aware is not expect_descendant_aware:
                failures.append(f"{label}: expected descendant_aware guard blocks={expect_descendant_aware}, got {descendant_aware}")

        # Round 1 bypass: symlink target passed directly.
        check(
            "round1: bypass via symlink target",
            str(real_target),
            expect_original=False,
            expect_equality_only=True,
            expect_descendant_aware=True,
        )
        # Round 1 bypass: symlink path passed directly.
        check(
            "round1: direct symlink path",
            str(symlinked_hermes),
            expect_original=False,
            expect_equality_only=True,
            expect_descendant_aware=True,
        )
        # Round 2 bypass: subdirectory of ~/.hermes via the symlink path.
        check(
            "round2: subdir via symlink path (e.g. ~/.hermes/pets)",
            str(subdir_via_symlink),
            expect_original=False,
            expect_equality_only=False,
            expect_descendant_aware=True,
        )
        # Round 2 bypass: subdirectory of ~/.hermes via the resolved target.
        check(
            "round2: subdir via resolved target",
            str(subdir_via_target),
            expect_original=False,
            expect_equality_only=False,
            expect_descendant_aware=True,
        )
        # No false positive: a genuinely isolated profile must never be
        # blocked, by any of the three guards.
        check(
            "isolated profile (no false positive)",
            str(isolated_profile),
            expect_original=False,
            expect_equality_only=False,
            expect_descendant_aware=False,
        )

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(
        "\nAll checks passed: both the symlink bypass (round 1) and the "
        "subdirectory bypass (round 2) are reproduced against their "
        "respective pre-fix guards and closed by descendant_aware_guard_blocks "
        "(the guard now deployed in install_final_atlas_pet.py and "
        "render_final_atlas_pet.py), with no false positive on a genuinely "
        "isolated profile."
    )


if __name__ == "__main__":
    main()
