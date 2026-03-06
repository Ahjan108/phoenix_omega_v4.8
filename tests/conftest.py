"""
Shared pytest fixtures and configuration.
See docs/FULL_REPO_TEST_SUITE_PLAN.md and docs/ROBUST_INTELLIGENT_TESTING.md.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# #region agent log
DEBUG_LOG = Path(__file__).resolve().parent.parent / ".cursor" / "debug-5802b0.log"
def _debug_log(session_id: str, hypothesis_id: str, location: str, message: str, data: dict[str, Any] | None = None) -> None:
    try:
        payload = {"sessionId": session_id, "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data or {}, "timestamp": __import__("time").time() * 1000}
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass
# #endregion


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
    raw = os.environ.get("ATOMS_ROOT")
    return Path(raw) if raw else (REPO_ROOT / "atoms")


# ─── Robust / intelligent testing: config and locale fixtures ─────────────────

def _load_yaml(path: Path) -> Any:
    """Load YAML file; raises on missing or invalid."""
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def locale_registry_path() -> Path:
    """Path to locale_registry.yaml."""
    return REPO_ROOT / "config" / "localization" / "locale_registry.yaml"


@pytest.fixture(scope="session")
def locale_registry(locale_registry_path: Path) -> dict[str, Any]:
    """Loaded locale_registry.yaml (session-scoped)."""
    return _load_yaml(locale_registry_path)


@pytest.fixture(scope="session")
def content_roots_path() -> Path:
    """Path to content_roots_by_locale.yaml."""
    return REPO_ROOT / "config" / "localization" / "content_roots_by_locale.yaml"


@pytest.fixture(scope="session")
def content_roots(content_roots_path: Path) -> dict[str, Any]:
    """Loaded content_roots_by_locale.yaml (session-scoped)."""
    return _load_yaml(content_roots_path)


@pytest.fixture(scope="session")
def all_locale_ids(locale_registry: dict[str, Any]) -> list[str]:
    """List of all locale IDs from locale_registry.locales (for parametrization)."""
    locales = locale_registry.get("locales") or {}
    return sorted(locales.keys())


@pytest.fixture
def golden_bindings_path(fixtures_dir: Path) -> Path | None:
    """
    Path to golden_test_bindings.yaml, or None if missing.
    Use with pytest.skip() in tests that need it instead of silent return.
    """
    p = fixtures_dir / "bindings" / "golden_test_bindings.yaml"
    return p if p.exists() else None


# #region agent log
def pytest_configure(config: pytest.Config) -> None:
    """Log env at session start (H1: venv, H2: PYTHONPATH)."""
    try:
        py = sys.executable or ""
        path = os.environ.get("PYTHONPATH", "")
        yaml_ok = "ok"
        try:
            import yaml as _  # noqa: F401
        except ImportError:
            yaml_ok = "missing"
        jsonschema_ok = "ok"
        try:
            __import__("jsonschema")
        except ImportError:
            jsonschema_ok = "missing"
        _debug_log("5802b0", "H1", "conftest.py:pytest_configure", "session env", {"python": py, "PYTHONPATH": path, "yaml": yaml_ok, "jsonschema": jsonschema_ok})
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: Any) -> Any:
    """Log each test failure (H3)."""
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and getattr(report, "outcome", None) == "failed":
        try:
            longrepr = str(getattr(report, "longrepr", ""))[:500]
            _debug_log("5802b0", "H3", "conftest.py:pytest_runtest_makereport", "test failed", {"nodeid": item.nodeid, "outcome": report.outcome, "message": longrepr})
        except Exception:
            pass


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Log session totals (H3, H4, H5)."""
    try:
        collected = len(getattr(session, "items", []))
        _debug_log("5802b0", "H4", "conftest.py:pytest_sessionfinish", "session finish", {"exitstatus": exitstatus, "collected": collected})
    except Exception:
        pass
# #endregion
