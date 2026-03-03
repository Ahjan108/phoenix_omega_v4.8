"""
Shared pytest fixtures and configuration.
See docs/FULL_REPO_TEST_SUITE_PLAN.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    """Repo root path."""
    return REPO_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    """tests/fixtures directory."""
    return REPO_ROOT / "tests" / "fixtures"


@pytest.fixture
def config_root() -> Path:
    """config/ directory."""
    return REPO_ROOT / "config"


@pytest.fixture
def atoms_root() -> Path:
    """atoms/ directory (or override via ATOMS_ROOT env)."""
    import os
    raw = os.environ.get("ATOMS_ROOT")
    return Path(raw) if raw else (REPO_ROOT / "atoms")
