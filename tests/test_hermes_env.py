"""Unit tests for scripts/hermes_env.py — the single owner of the Hermes-source
path resolution and the isolated-HERMES_HOME safety guard.

The guard (``require_isolated_hermes_home``) is safety code: it refuses to let a
pet-installing script write to the real ``~/.hermes`` profile. It was duplicated
verbatim across four scripts before this consolidation; these tests lock its
behavior down in its now-single home.
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
