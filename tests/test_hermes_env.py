"""Unit tests for scripts/hermes_env.py — the single owner of the Hermes-source
path resolution and the isolated-HERMES_HOME safety guard.

The guard (``require_isolated_hermes_home``) is safety code: it refuses to let a
pet-installing script write to the real ``~/.hermes`` profile. It was duplicated
verbatim across four scripts before this consolidation; these tests lock its
behavior down in its now-single home.

Two of these tests (``test_guard_exits_when_hermes_home_is_a_symlinked_real_profile``
and ``test_guard_exits_when_hermes_home_is_a_subdirectory_of_the_real_profile``)
are regression tests for bypasses found by two independent cross-reviews of
this exact guard: (1) if ``~/.hermes`` is itself a symlink, an earlier version
of this guard compared an unresolved RHS and never matched; (2) even after
resolving both sides, a strict ``==`` still missed ``HERMES_HOME`` pointing at
a subdirectory of the real profile. Both are fixed in
``require_isolated_hermes_home`` and locked down here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import hermes_env


def test_hermes_src_defaults_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(hermes_env.HERMES_SRC_ENV, raising=False)
    assert hermes_env.hermes_src() == hermes_env.DEFAULT_HERMES_SRC


def test_hermes_src_honors_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(hermes_env.HERMES_SRC_ENV, "/opt/hermes-agent")
    assert hermes_env.hermes_src() == Path("/opt/hermes-agent")


def test_hermes_src_ignores_blank_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(hermes_env.HERMES_SRC_ENV, "   ")
    assert hermes_env.hermes_src() == hermes_env.DEFAULT_HERMES_SRC


def test_ensure_hermes_on_path_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(hermes_env.HERMES_SRC_ENV, "/opt/hermes-xyz")
    hermes_env.ensure_hermes_on_path()
    hermes_env.ensure_hermes_on_path()
    assert sys.path.count("/opt/hermes-xyz") == 1


def test_guard_exits_when_hermes_home_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HERMES_HOME", raising=False)
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()


def test_guard_exits_when_pointed_at_real_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    real = str(Path.home() / ".hermes")
    monkeypatch.setenv("HERMES_HOME", real)
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()


def test_guard_returns_value_for_isolated_profile(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    isolated = str(tmp_path / "hermes-jorgito-test")
    monkeypatch.setenv("HERMES_HOME", isolated)
    assert hermes_env.require_isolated_hermes_home() == isolated


def test_guard_strips_whitespace_then_treats_blank_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HERMES_HOME", "   ")
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()


def test_guard_exits_when_hermes_home_is_a_symlinked_real_profile(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Regression test: ~/.hermes as a symlink (e.g. stow/chezmoi) must still
    be caught, whether HERMES_HOME is passed as the symlink path itself or as
    its resolved target -- both are the same on-disk data as the real profile.
    """
    fake_home = tmp_path / "fake_home"
    real_target = fake_home / "dotfiles" / "hermes-config"
    real_target.mkdir(parents=True)
    symlinked_hermes = fake_home / ".hermes"
    symlinked_hermes.symlink_to(real_target, target_is_directory=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    monkeypatch.setenv("HERMES_HOME", str(symlinked_hermes))
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()

    monkeypatch.setenv("HERMES_HOME", str(real_target))
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()


def test_guard_exits_when_hermes_home_is_a_subdirectory_of_the_real_profile(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Regression test: HERMES_HOME pointing *inside* the real ~/.hermes (e.g.
    ~/.hermes/pets) must be rejected too, not just an exact match -- reachable
    both directly and through a symlinked ~/.hermes.
    """
    fake_home = tmp_path / "fake_home2"
    real_target = fake_home / "dotfiles" / "hermes-config"
    real_target.mkdir(parents=True)
    symlinked_hermes = fake_home / ".hermes"
    symlinked_hermes.symlink_to(real_target, target_is_directory=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    subdir_via_symlink = symlinked_hermes / "pets"
    subdir_via_symlink.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(subdir_via_symlink))
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()

    subdir_via_target = real_target / "pets"  # same on-disk dir as above
    monkeypatch.setenv("HERMES_HOME", str(subdir_via_target))
    with pytest.raises(SystemExit):
        hermes_env.require_isolated_hermes_home()


def test_guard_returns_value_for_isolated_profile_even_with_symlinked_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No false positive: a genuinely isolated profile must still pass, even
    when ~/.hermes happens to be a symlink."""
    fake_home = tmp_path / "fake_home3"
    real_target = fake_home / "dotfiles" / "hermes-config"
    real_target.mkdir(parents=True)
    (fake_home / ".hermes").symlink_to(real_target, target_is_directory=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    isolated = fake_home / "hermes-jorgito-test"
    isolated.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(isolated))
    assert hermes_env.require_isolated_hermes_home() == str(isolated)
