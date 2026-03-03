"""
Load church YAML by brand_id. Fail fast with clear error when missing or invalid.
Authority: docs/church_docs/README.md. Used by payouts/storefront tools.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = REPO_ROOT / "docs"

# brand_id -> church YAML path (relative to repo root)
CHURCH_BRAND_MAP: dict[str, Path] = {
    "norcal_dharma": DOCS / "norcal_dharma.yaml",
}


def load_church(brand_id: str) -> dict[str, Any]:
    """
    Load church record for brand_id. Fails fast with clear error if missing or invalid.
    Returns the parsed YAML (top-level key 'church' contains the record).
    """
    path = CHURCH_BRAND_MAP.get(brand_id)
    if not path:
        raise ValueError(
            f"Unknown church brand_id: {brand_id!r}. "
            f"Known: {list(CHURCH_BRAND_MAP.keys())}. "
            "Add mapping in phoenix_v4.ops.church_loader.CHURCH_BRAND_MAP and docs/church_docs/README.md."
        )
    if not path.exists():
        raise FileNotFoundError(
            f"Church YAML not found for brand_id={brand_id!r}: {path}. "
            "Ensure docs/norcal_dharma.yaml exists (Cooperative Church Compliance YAML Schema)."
        )
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    except Exception as e:
        raise ValueError(
            f"Church YAML invalid for brand_id={brand_id!r} ({path}): {e}. "
            "Fix YAML syntax or schema."
        ) from e
    if not isinstance(data, dict):
        raise ValueError(
            f"Church YAML must be a mapping for brand_id={brand_id!r} ({path}), got {type(data).__name__}."
        )
    return data


def get_church_display_name(brand_id: str) -> str:
    """
    Get display name (church.short_name) for brand_id. Fails fast if church YAML missing/invalid.
    """
    data = load_church(brand_id)
    church = data.get("church") or {}
    name = church.get("short_name")
    if not name or not isinstance(name, str):
        raise ValueError(
            f"Church YAML for brand_id={brand_id!r} missing or invalid church.short_name. "
            "Cooperative Church Compliance schema requires short_name."
        )
    return str(name).strip()
