"""
Stage 2 Format Selector.
Deterministic mapping: (topic, persona, installment, series) -> FormatPlan.
Reads config/format_selection/ (format_registry.yaml, selection_rules.yaml).
Same input -> same output always.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FORMAT_SELECTION = REPO_ROOT / "config" / "format_selection"


@dataclass
class FormatPlan:
    """Stage 2 output. Contract: specs/OMEGA_LAYER_CONTRACTS.md. slot_definitions required for Stage 3."""
    format_structural_id: str
    format_runtime_id: str
    tier: str
    blueprint_variant: str
    chapter_count: int
    word_target_range: tuple[int, int]
    slot_definitions: list[list[str]]  # one row per chapter; Stage 3 MUST NOT infer
    book_size: Optional[str] = None  # short | medium | long (planner quotas)
    emotional_curve_profile: Optional[str] = None
    rationale: Optional[dict] = None

    def to_compiler_input(self) -> dict:
        """For Stage 3 handoff."""
        return {
            "format_structural_id": self.format_structural_id,
            "format_runtime_id": self.format_runtime_id,
            "tier": self.tier,
            "blueprint_variant": self.blueprint_variant,
            "chapter_count": self.chapter_count,
            "target_chapter_count": self.chapter_count,
            "word_target_range": list(self.word_target_range),
            "slot_definitions": self.slot_definitions,
            "book_size": self.book_size,
        }


class FormatSelector:
    """Deterministic format selection from topic/persona/installment/series."""

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        rules_path: Optional[Path] = None,
    ):
        registry_path = registry_path or (CONFIG_FORMAT_SELECTION / "format_registry.yaml")
        rules_path = rules_path or (CONFIG_FORMAT_SELECTION / "selection_rules.yaml")
        self._registry = self._load_yaml(registry_path)
        self._rules = self._load_yaml(rules_path)
        self._structural = (self._registry or {}).get("structural_formats", {})
        self._runtime = (self._registry or {}).get("runtime_formats", {})

    @staticmethod
    def _load_yaml(p: Path) -> dict:
        if not p.exists() or yaml is None:
            return {}
        with open(p) as f:
            return yaml.safe_load(f) or {}

    def _topic_complexity(self, topic_id: str) -> str:
        for level, topics in (self._rules.get("topic_complexity") or {}).items():
            if topic_id in topics:
                return level
        return "medium"

    def _base_structural_format(self, topic_id: str, installment_number: Optional[int]) -> str:
        strategy = self._rules.get("installment_strategy") or {}
        complexity = self._topic_complexity(topic_id)
        inst = installment_number or 1
        if inst == 1:
            opener = strategy.get("opener") or {}
            key = f"{complexity}_complexity" if complexity != "medium" else "medium_complexity"
            return opener.get(key) or opener.get("medium_complexity") or "F001"
        if inst in (2, 3):
            deepening = strategy.get("deepening") or {}
            return deepening.get("high_complexity") if complexity == "high" else deepening.get("default", "F002")
        rotation = strategy.get("rotation") or {}
        cycle = rotation.get("cycle") or ["F001", "F002"]
        return cycle[(inst - 1) % len(cycle)]

    def _apply_persona_constraints(self, structural_id: str, persona_id: str) -> str:
        pc = (self._rules.get("persona_constraints") or {}).get(persona_id)
        if not pc:
            return structural_id
        forbidden = pc.get("forbidden_formats") or []
        if structural_id in forbidden:
            # Fallback: first same-tier format not forbidden
            tier = (self._structural.get(structural_id) or {}).get("tier", "A")
            for fid, info in self._structural.items():
                if info.get("tier") == tier and fid not in forbidden:
                    return fid
            return structural_id
        return structural_id

    def _runtime_for_persona_and_structural(
        self, persona_id: str, structural_id: str
    ) -> str:
        pc = (self._rules.get("persona_constraints") or {}).get(persona_id)
        struct_info = self._structural.get(structural_id) or {}
        tier = struct_info.get("tier", "A")
        preferred = (pc or {}).get("preferred_runtime") or struct_info.get("typical_runtime", "standard_book")
        if preferred in self._runtime:
            rt_info = self._runtime[preferred]
            if tier in (rt_info.get("compatible_tiers") or []):
                return preferred
        typical = struct_info.get("typical_runtime", "standard_book")
        if typical in self._runtime:
            return typical
        for rid, rinfo in self._runtime.items():
            if tier in (rinfo.get("compatible_tiers") or []):
                return rid
        return "standard_book"

    def _blueprint_variant(
        self, installment_number: Optional[int], persona_id: str
    ) -> str:
        rot = self._rules.get("blueprint_rotation") or {}
        seq = rot.get("sequence") or ["linear", "wave", "scaffold"]
        cycle_len = rot.get("cycle_length") or 3
        inst = installment_number or 1
        idx = (inst - 1) % min(cycle_len, len(seq))
        base = seq[idx]
        if idx == cycle_len - 1:
            adv = (rot.get("advanced_variants") or {})
            return adv.get(persona_id) or adv.get("default") or base
        return base

    def _chapter_count_and_word_range(
        self, runtime_id: str, structural_id: str, persona_id: str
    ) -> tuple[int, tuple[int, int]]:
        rt = self._runtime.get(runtime_id) or {}
        chapter_count = rt.get("chapter_count_default", 12)
        word_range = tuple(rt.get("word_range", [9000, 11000]))
        pc = (self._rules.get("persona_constraints") or {}).get(persona_id)
        if pc:
            if pc.get("max_chapter_count") is not None and chapter_count > pc["max_chapter_count"]:
                chapter_count = pc["max_chapter_count"]
            if pc.get("min_chapter_count") is not None and chapter_count < pc["min_chapter_count"]:
                chapter_count = pc["min_chapter_count"]
        struct_info = self._structural.get(structural_id) or {}
        ch_range = struct_info.get("chapter_range") or [8, 15]
        chapter_count = max(ch_range[0], min(ch_range[1], chapter_count))
        return chapter_count, word_range

    def select_format(
        self,
        topic_id: str,
        persona_id: str,
        installment_number: Optional[int] = None,
        series_id: Optional[str] = None,
        constraints: Optional[dict] = None,
    ) -> FormatPlan:
        """
        Deterministic: same (topic, persona, installment, series) -> same FormatPlan.
        """
        constraints = constraints or {}
        rationale = []

        base = self._base_structural_format(topic_id, installment_number)
        rationale.append(f"base_structural={base} (topic_complexity={self._topic_complexity(topic_id)}, installment={installment_number or 1})")

        structural_id = self._apply_persona_constraints(base, persona_id)
        if structural_id != base:
            rationale.append(f"persona_constraint: {base} -> {structural_id}")
        if constraints.get("force_structural_format") and constraints["force_structural_format"] in self._structural:
            structural_id = constraints["force_structural_format"]
            rationale.append(f"constraint: force_structural_format={structural_id}")

        runtime_id = self._runtime_for_persona_and_structural(persona_id, structural_id)
        rationale.append(f"runtime={runtime_id}")

        tier = (self._structural.get(structural_id) or {}).get("tier", "A")
        blueprint = self._blueprint_variant(installment_number, persona_id)
        rationale.append(f"blueprint={blueprint}")

        chapter_count, word_range = self._chapter_count_and_word_range(
            runtime_id, structural_id, persona_id
        )

        # Overrides from constraints
        if constraints.get("force_runtime_format") and constraints["force_runtime_format"] in self._runtime:
            runtime_id = constraints["force_runtime_format"]
            rt = self._runtime[runtime_id]
            chapter_count = rt.get("chapter_count_default", chapter_count)
            word_range = tuple(rt.get("word_range", list(word_range)))
        if constraints.get("force_tier") in ("A", "B", "C"):
            tier = constraints["force_tier"]

        # Emotional curve profile from blueprint (simple mapping)
        curve = {"linear": "cool_warm_hot_land", "wave": "spike", "scaffold": "descent", "rupture": "volatile"}.get(blueprint, "cool_warm_hot_land")

        # slot_definitions: from format policy (Canonical §3.0, DEV SPEC 2). Per-format slot_template overrides default.
        struct_info = self._structural.get(structural_id) or {}
        slot_template = struct_info.get("slot_template")
        if slot_template and isinstance(slot_template, list) and slot_template:
            template = list(slot_template)
        else:
            default_slots = (self._registry or {}).get("default_slot_definitions")
            if default_slots and isinstance(default_slots, list) and default_slots:
                first = default_slots[0]
                template = list(first) if isinstance(first, list) else ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
            else:
                template = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
            if not template:
                template = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
        allowed_slots = {"HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION", "COMPRESSION", "PIVOT", "TAKEAWAY", "PERMISSION", "THREAD"}
        for st in template:
            if st not in allowed_slots:
                raise ValueError(f"Unknown slot type in format {structural_id}: {st}. Allowed: {sorted(allowed_slots)}")
        slot_definitions = [list(template) for _ in range(chapter_count)]

        plan = FormatPlan(
            format_structural_id=structural_id,
            format_runtime_id=runtime_id,
            tier=tier,
            blueprint_variant=blueprint,
            chapter_count=chapter_count,
            word_target_range=word_range,
            slot_definitions=slot_definitions,
            book_size=("short" if chapter_count <= 6 else "medium" if chapter_count <= 10 else "long"),
            emotional_curve_profile=curve,
            rationale={
                "rules_fired": rationale,
                "inputs_digest": inputs_digest(topic_id, persona_id, installment_number, series_id),
            },
        )
        self._validate_plan(plan)
        return plan

    def _validate_plan(self, plan: FormatPlan) -> None:
        """Hard fail if invalid."""
        if plan.format_structural_id not in self._structural:
            raise ValueError(f"Unknown structural format: {plan.format_structural_id}")
        if plan.format_runtime_id not in self._runtime:
            raise ValueError(f"Unknown runtime format: {plan.format_runtime_id}")
        struct_tier = (self._structural.get(plan.format_structural_id) or {}).get("tier")
        if struct_tier and plan.tier != struct_tier:
            raise ValueError(f"Tier mismatch: structural {plan.format_structural_id} has tier {struct_tier}, plan has {plan.tier}")
        rt = self._runtime.get(plan.format_runtime_id) or {}
        if plan.tier not in (rt.get("compatible_tiers") or []):
            raise ValueError(f"Runtime {plan.format_runtime_id} not compatible with tier {plan.tier}")
        struct_info = self._structural.get(plan.format_structural_id) or {}
        ch_range = struct_info.get("chapter_range") or [1, 99]
        ch_min, ch_max = ch_range[0], ch_range[1]
        if not (ch_min <= plan.chapter_count <= ch_max):
            raise ValueError(f"chapter_count {plan.chapter_count} outside range [{ch_min},{ch_max}] for {plan.format_structural_id}")
        if plan.blueprint_variant not in ("linear", "wave", "scaffold", "rupture"):
            raise ValueError(f"Invalid blueprint_variant: {plan.blueprint_variant}")


def inputs_digest(topic_id: str, persona_id: str, installment_number: Optional[int], series_id: Optional[str]) -> str:
    """Stable digest for determinism checks."""
    payload = json.dumps(
        {"topic_id": topic_id, "persona_id": persona_id, "installment_number": installment_number, "series_id": series_id},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Stage 2 Format Selector: topic, persona, installment -> FormatPlan")
    parser.add_argument("--topic", required=True, help="Topic ID (e.g. relationship_anxiety)")
    parser.add_argument("--persona", required=True, help="Persona ID (e.g. nyc_exec, gen_z)")
    parser.add_argument("--installment", type=int, default=None, help="Installment number (default 1)")
    parser.add_argument("--series", default=None, help="Series ID (optional)")
    parser.add_argument("--out", default=None, help="Write plan JSON to path")
    parser.add_argument("--config-dir", default=None, help="Override config/format_selection dir")
    args = parser.parse_args()
    config_dir = Path(args.config_dir) if args.config_dir else None
    registry = (config_dir / "format_registry.yaml") if config_dir else None
    rules = (config_dir / "selection_rules.yaml") if config_dir else None
    sel = FormatSelector(registry_path=registry, rules_path=rules)
    plan = sel.select_format(
        topic_id=args.topic,
        persona_id=args.persona,
        installment_number=args.installment,
        series_id=args.series,
    )
    out = {
        "format_structural_id": plan.format_structural_id,
        "format_runtime_id": plan.format_runtime_id,
        "tier": plan.tier,
        "blueprint_variant": plan.blueprint_variant,
        "chapter_count": plan.chapter_count,
        "word_target_range": list(plan.word_target_range),
        "book_size": plan.book_size,
        "emotional_curve_profile": plan.emotional_curve_profile,
        "rationale": plan.rationale,
    }
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Wrote FormatPlan to {args.out}")
    else:
        print(json.dumps(out, indent=2))


def resolve_arc_from_angle(book_spec: Any, default_arc_path: Path) -> Path:
    """
    Angle Integration (V4.7). If book_spec.angle_id is in angle_registry and has arc_path, return it; else default_arc_path.
    Arc-First remains authoritative; angle chooses variant.
    """
    from phoenix_v4.planning.angle_resolver import resolve_arc_path
    angle_id = None
    if hasattr(book_spec, "angle_id"):
        angle_id = getattr(book_spec, "angle_id", None)
    elif isinstance(book_spec, dict):
        angle_id = book_spec.get("angle_id")
    return resolve_arc_path(angle_id, default_arc_path)


if __name__ == "__main__":
    main()
