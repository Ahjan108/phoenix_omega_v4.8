#!/usr/bin/env python3
"""
Generate concrete arc YAML from a parameterized template. Dev Spec §3.1.2.
Usage:
  python tools/arc_generator.py --template standard_escalation --persona gen_z_professionals \\
    --topic anxiety --format F002 --chapter-count 30 --engine overwhelm --out config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F002.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    yaml = None  # pip install pyyaml required for arc_generator


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    if yaml is None:
        raise ValueError("PyYAML required. Install with: pip install pyyaml")
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _interp_curve(template: list[int], n: int) -> list[int]:
    """Scale template (length T) to length n via linear interpolation. Returns ints 1-5."""
    if n <= 0:
        return []
    t = len(template)
    if t == 0:
        return [2] * n
    out = []
    for i in range(n):
        pos = (i / max(1, n - 1)) * (t - 1) if n > 1 else 0
        idx_lo = int(pos) % t
        idx_hi = min(idx_lo + 1, t - 1)
        frac = pos - int(pos)
        v = template[idx_lo] * (1 - frac) + template[idx_hi] * frac
        out.append(max(1, min(5, round(v))))
    return out


ALLOWED_EMOTIONAL_ROLES = ("recognition", "destabilization", "reframe", "stabilization", "integration")


def _interp_roles(template: list[str], n: int) -> list[str]:
    """Map template role sequence (length T) to length n. Index by proportional position."""
    if n <= 0 or not template:
        return ["recognition"] * n
    t = len(template)
    out = []
    for i in range(n):
        idx = int((i / n) * t) % t if n > 0 else 0
        out.append(template[idx])
    # First must be recognition, last must be integration (arc_loader validation).
    if out:
        out[0] = "recognition"
        out[-1] = "integration"
    return _enforce_role_schema(out, n)


def _enforce_role_schema(role_seq: list[str], n: int) -> list[str]:
    """Enforce arc_loader rules: max 2 consecutive same role; nc>=6 => at least 4 unique roles."""
    out = list(role_seq)
    # Break runs of 3+ same role (insert reframe or stabilization in middle of run).
    i = 0
    while i < len(out):
        run_len = 1
        while i + run_len < len(out) and out[i + run_len] == out[i]:
            run_len += 1
        if run_len > 2:
            # Replace middle indices with alternate role (avoid changing first/last).
            insert_role = "reframe" if out[i] != "reframe" else "stabilization"
            for j in range(1, run_len - 1):
                idx = i + j
                if 0 < idx < len(out) - 1:
                    out[idx] = insert_role
        i += run_len
    # nc >= 6 must include at least 4 of 5 roles.
    if n >= 6:
        unique = set(out)
        if len(unique) < 4:
            # Add missing roles by replacing some middle destabilizations.
            for r in ALLOWED_EMOTIONAL_ROLES:
                if r in unique or r in ("recognition", "integration"):
                    continue
                for idx in range(1, len(out) - 1):
                    if out[idx] == "destabilization" and out[idx - 1] != r and out[idx + 1] != r:
                        out[idx] = r
                        unique.add(r)
                        break
                if len(unique) >= 4:
                    break
    return out


def _cycle_list(cycle: list[str], n: int) -> list[str]:
    """Repeat cycle to length n."""
    if not cycle or n <= 0:
        return ["didactic"] * n
    return [cycle[i % len(cycle)] for i in range(n)]


def _default_temperature_curve(n: int) -> dict[int, str]:
    """Default cool -> warm -> hot -> warm for cost chapter region."""
    cost_ch = max(1, (3 * n) // 4)
    out = {}
    for i in range(1, n + 1):
        if i <= n // 3:
            out[i] = "cool"
        elif i <= cost_ch:
            out[i] = "warm"
        elif i <= cost_ch + 2:
            out[i] = "hot"
        else:
            out[i] = "warm"
    return out


def _default_chapter_intent(n: int) -> dict[int, str]:
    """Minimal chapter_intent labels for validator."""
    intents = [
        "establish_mask", "expose_cost", "destabilize_strategy", "reveal_hidden_belief",
        "confrontation", "somatic_repair", "relational_shift", "embodied_identity",
        "grounded_reframe",
    ]
    out = {}
    for i in range(1, n + 1):
        out[i] = intents[(i - 1) % len(intents)]
    if n >= 1:
        out[n] = "embodied_identity"
    return out


def generate_arc(
    template_path: Path,
    persona: str,
    topic: str,
    format_id: str,
    chapter_count: int,
    engine: str,
    out_path: Path | None = None,
) -> dict:
    """
    Load template, scale to chapter_count, fill motif from motif_bank by topic, produce arc dict.
    """
    template = _load_yaml(template_path)
    if not template:
        raise ValueError(f"Empty or missing template: {template_path}")

    t_id = template.get("template_id", "unknown")
    curve_t = template.get("emotional_curve_template", [2, 3, 4, 4, 3, 2])
    role_t = template.get("emotional_role_template", ["recognition", "destabilization", "reframe", "stabilization", "integration"])
    cycle = template.get("reflection_strategy_cycle", ["didactic", "socratic", "narrative_embedded"])
    motif_bank = template.get("motif_bank") or {}
    cost_pos = float(template.get("cost_chapter_position", 0.75))
    resolution_type = template.get("resolution_type", "internal_shift_only")

    # Format must be in compatible_formats
    compat = template.get("compatible_formats") or []
    if compat and format_id not in compat:
        raise ValueError(f"Format {format_id} not in template compatible_formats {compat}")

    emotional_curve = _interp_curve(curve_t, chapter_count)
    emotional_role_sequence = _interp_roles(role_t, chapter_count)
    reflection_strategy_sequence = _cycle_list(cycle, chapter_count)
    cost_chapter_index = max(1, min(chapter_count, round(cost_pos * chapter_count)))
    motif = dict(motif_bank.get(topic) or motif_bank.get("default") or {"primary_symbol": "threshold", "tonal_signature": "warm_witness"})
    emotional_temperature_curve = _default_temperature_curve(chapter_count)
    chapter_intent = _default_chapter_intent(chapter_count)

    arc_id = f"{persona}_{topic}_{engine}_{format_id}_gen".replace(" ", "_")
    arc = {
        "arc_id": arc_id,
        "persona": persona,
        "topic": topic,
        "engine": engine,
        "format": format_id,
        "chapter_count": chapter_count,
        "emotional_curve": emotional_curve,
        "emotional_temperature_curve": emotional_temperature_curve,
        "chapter_intent": chapter_intent,
        "emotional_role_sequence": emotional_role_sequence,
        "reflection_strategy_sequence": reflection_strategy_sequence,
        "cost_chapter_index": cost_chapter_index,
        "resolution_type": resolution_type,
        "motif": motif,
    }
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            yaml.dump(arc, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return arc


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate concrete arc from template.")
    ap.add_argument("--template", default="standard_escalation", help="Template ID or path to template YAML.")
    ap.add_argument("--persona", required=True, help="Persona slug.")
    ap.add_argument("--topic", required=True, help="Topic slug.")
    ap.add_argument("--format", "--format-id", dest="format_id", required=True, help="Format ID (e.g. F002).")
    ap.add_argument("--chapter-count", type=int, required=True, help="Number of chapters.")
    ap.add_argument("--engine", default="overwhelm", help="Engine slug (e.g. overwhelm, shame).")
    ap.add_argument("--out", type=Path, default=None, help="Output arc YAML path.")
    args = ap.parse_args()

    templates_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "templates"
    template_path = Path(args.template) if args.template.endswith(".yaml") else templates_dir / f"{args.template}.yaml"
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    out_path = args.out
    if not out_path:
        out_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / f"{args.persona}__{args.topic}__{args.engine}__{args.format_id}.yaml"

    try:
        generate_arc(
            template_path,
            persona=args.persona,
            topic=args.topic,
            format_id=args.format_id,
            chapter_count=args.chapter_count,
            engine=args.engine,
            out_path=out_path,
        )
        print("Wrote", out_path)
        return 0
    except Exception as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
