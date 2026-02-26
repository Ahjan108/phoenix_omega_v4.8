from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parent.parent
FREEZE_CONFIG_PATH = REPO_ROOT / "pearl_prime" / "config" / "v4_freeze_modular_formats.yaml"


@dataclass(frozen=True)
class FreezeSettings:
    enabled: bool
    default_output_format: str
    formats: dict[str, dict[str, Any]]


def load_freeze_settings(path: Path | None = None) -> FreezeSettings:
    cfg_path = path or FREEZE_CONFIG_PATH
    if yaml is None or not cfg_path.exists():
        return FreezeSettings(enabled=False, default_output_format="", formats={})
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return FreezeSettings(
        enabled=bool(data.get("v4_freeze_enabled")),
        default_output_format=str(data.get("default_output_format") or ""),
        formats=dict(data.get("output_formats") or {}),
    )


def allowed_output_formats(settings: FreezeSettings) -> list[str]:
    return sorted(settings.formats.keys())


def require_valid_output_format(output_format_id: str, settings: FreezeSettings) -> dict[str, Any]:
    key = (output_format_id or "").strip()
    if key not in settings.formats:
        allowed = ", ".join(allowed_output_formats(settings))
        raise ValueError(f"Unsupported output format '{key}'. Allowed: {allowed}")
    return settings.formats[key]


def apply_output_format_to_plan(
    format_plan: dict[str, Any],
    *,
    output_format_id: str,
    chapter_count: int,
    settings: FreezeSettings,
) -> dict[str, Any]:
    """
    Apply modular output format to Stage-2 plan.
    Arc-First remains authoritative for chapter_count; this function rewrites slot structure and runtime hint.
    """
    fmt = require_valid_output_format(output_format_id, settings)
    slot_template = [str(s).strip().upper() for s in (fmt.get("slot_template") or []) if str(s).strip()]
    if not slot_template:
        raise ValueError(f"Output format '{output_format_id}' has empty slot_template")

    out = dict(format_plan)
    out["format_structural_id"] = f"MOD_{output_format_id}"
    out["format_runtime_id"] = str(fmt.get("runtime_format_id") or out.get("format_runtime_id") or "")
    out["chapter_count"] = int(chapter_count)
    out["target_chapter_count"] = int(chapter_count)
    out["slot_definitions"] = [slot_template[:] for _ in range(int(chapter_count))]
    out["book_size"] = "short" if chapter_count <= 6 else ("medium" if chapter_count <= 10 else "long")
    out["output_format_id"] = output_format_id
    out["output_format_name"] = str(fmt.get("name") or output_format_id)
    twr = fmt.get("target_word_range")
    if isinstance(twr, list) and len(twr) == 2:
        out["target_word_range"] = [int(twr[0]), int(twr[1])]
    return out

