#!/usr/bin/env python3
"""
Generate asset manifest from planned books (catalog mode) or canonical topics×personas (canonical mode).
Output: one JSONL row per (topic, persona, freebie_id, format) for asset creation.
Authority: V4 Freebies + Immersion Ecosystem plan §2.2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _mock_format_plan(chapter_count: int = 8) -> dict:
    return {"chapter_count": chapter_count}


def _mock_compiled(chapter_count: int = 8, has_exercise: bool = True) -> dict:
    # One EXERCISE in first chapter so somatic rule can attach
    row = ["EXERCISE", "STORY", "TEACHING"] if has_exercise else ["STORY", "TEACHING"]
    rows = [row] + [["STORY", "TEACHING"]] * (chapter_count - 1)
    return {"chapter_slot_sequence": rows}


def _mock_arc(engine: str) -> object:
    class Arc:
        def __init__(self, e: str):
            self.engine = e
            self.emotional_curve = [3] * 8
            self.emotional_temperature_sequence = ["warm"] * 8
    return Arc(engine)


def _first_engine_for_topic(topic_id: str, bindings: dict) -> str:
    b = bindings.get(topic_id)
    if isinstance(b, dict):
        engines = b.get("allowed_engines") or []
        if engines:
            return engines[0]
    return "shame"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan freebie assets → manifest.jsonl")
    ap.add_argument("--catalog", type=Path, default=None, help="YAML catalog of books (topic_id, persona_id, arc_path?)")
    ap.add_argument("--topics", type=Path, default=None, help="Canonical topics YAML (used with --personas for canonical mode)")
    ap.add_argument("--personas", type=Path, default=None, help="Canonical personas YAML")
    ap.add_argument("--out", type=Path, default=None, help="Output manifest path (default: artifacts/asset_planning/manifest.jsonl)")
    args = ap.parse_args()

    if yaml is None:
        print("Required: pip install pyyaml", file=sys.stderr)
        return 1

    from phoenix_v4.planning.freebie_planner import plan_freebies, get_freebie_bundle_with_formats

    config_freebies = REPO_ROOT / "config" / "freebies"
    registry_path = config_freebies / "freebie_registry.yaml"
    rules_path = config_freebies / "freebie_selection_rules.yaml"
    reg = load_yaml(registry_path)
    freebies_map = reg.get("freebies") or {}
    bindings = load_yaml(REPO_ROOT / "config" / "topic_engine_bindings.yaml")

    manifest_rows: list[dict] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add_rows(topic_id: str, persona_id: str, bundle_with_formats: list[dict]) -> None:
        for item in bundle_with_formats:
            fid = item.get("freebie_id") or ""
            for fmt in item.get("formats") or ["html"]:
                key = (topic_id, persona_id, fid, fmt)
                if key not in seen:
                    seen.add(key)
                    manifest_rows.append({
                        "topic": topic_id,
                        "persona": persona_id,
                        "freebie_id": fid,
                        "format": fmt,
                    })

    if args.catalog and args.catalog.exists():
        catalog = load_yaml(args.catalog)
        books = catalog.get("books") or catalog.get("plans") or []
        if isinstance(catalog.get("topic_id"), str):
            books = [catalog]
        for book in books:
            topic_id = (book.get("topic_id") or book.get("topic") or "").strip()
            persona_id = (book.get("persona_id") or book.get("persona") or "").strip()
            if not topic_id or not persona_id:
                continue
            arc_path = book.get("arc_path") or book.get("arc")
            if arc_path:
                from phoenix_v4.planning.arc_loader import load_arc
                arc = load_arc(Path(arc_path))
                engine = getattr(arc, "engine", "shame")
                chapter_count = getattr(arc, "chapter_count", 8)
            else:
                engine = _first_engine_for_topic(topic_id, bindings)
                arc = _mock_arc(engine)
                chapter_count = 8
            format_plan = _mock_format_plan(chapter_count)
            compiled = _mock_compiled(chapter_count, True)
            book_spec = {"topic_id": topic_id, "persona_id": persona_id}
            bundle, _, _ = plan_freebies(book_spec, format_plan, compiled, arc, registry_path=registry_path, rules_path=rules_path)
            with_formats = get_freebie_bundle_with_formats(bundle, freebies_map, book_spec, format_plan, compiled)
            add_rows(topic_id, persona_id, with_formats)
    else:
        topics_path = args.topics or (REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml")
        personas_path = args.personas or (REPO_ROOT / "config" / "catalog_planning" / "canonical_personas.yaml")
        topics_data = load_yaml(Path(topics_path))
        personas_data = load_yaml(Path(personas_path))
        topics = topics_data.get("topics") or []
        personas = personas_data.get("personas") or []
        if not topics or not personas:
            print("Canonical mode requires topics and personas lists in YAML files.", file=sys.stderr)
            return 1
        for topic_id in topics:
            for persona_id in personas:
                engine = _first_engine_for_topic(topic_id, bindings)
                arc = _mock_arc(engine)
                format_plan = _mock_format_plan(8)
                compiled = _mock_compiled(8, True)
                book_spec = {"topic_id": topic_id, "persona_id": persona_id}
                bundle, _, _ = plan_freebies(book_spec, format_plan, compiled, arc, registry_path=registry_path, rules_path=rules_path)
                with_formats = get_freebie_bundle_with_formats(bundle, freebies_map, book_spec, format_plan, compiled)
                add_rows(topic_id, persona_id, with_formats)

    out_path = args.out or (REPO_ROOT / "artifacts" / "asset_planning" / "manifest.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for row in manifest_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(manifest_rows)} rows to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
