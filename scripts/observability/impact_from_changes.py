#!/usr/bin/env python3
"""
Compute impact summary from change_events.jsonl using system registry.
Output: artifacts/observability/impact_<timestamp>.json
Authority: docs/CHANGE_OBSERVATION_AND_IMPACT_SPEC.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_registry(repo_root: Path) -> dict:
    import yaml
    reg_path = repo_root / "config" / "governance" / "system_registry.yaml"
    if not reg_path.exists():
        return {"systems": {}}
    return yaml.safe_load(reg_path.read_text()) or {"systems": {}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Change events → impact summary")
    ap.add_argument("--events", default=None, help="Change events JSONL (default: artifacts/observability/change_events.jsonl)")
    ap.add_argument("--out", default=None, help="Output JSON path")
    args = ap.parse_args()

    events_path = Path(args.events) if args.events else REPO_ROOT / "artifacts" / "observability" / "change_events.jsonl"
    if not events_path.exists():
        print(f"No events file at {events_path}", file=sys.stderr)
        return 1

    registry = _load_registry(REPO_ROOT)
    systems = registry.get("systems") or {}

    events = []
    for line in events_path.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    affected_systems = set()
    for ev in events:
        for sid in ev.get("system_ids") or []:
            if sid != "_unregistered":
                affected_systems.add(sid)

    downstream = []
    related = set()
    for sid in affected_systems:
        meta = systems.get(sid) or {}
        for d in meta.get("downstream") or []:
            downstream.append({"system": sid, "downstream": d})
        for r in meta.get("related_systems") or []:
            related.add(r)

    summary = {
        "affected_systems": sorted(affected_systems),
        "downstream_signals_workflows": downstream,
        "related_systems": sorted(related),
        "event_count": len(events),
        "run_at": datetime.utcnow().isoformat() + "Z",
    }

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "observability" / f"impact_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Wrote impact summary to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
