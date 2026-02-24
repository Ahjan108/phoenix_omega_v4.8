"""
Unified CI runner for the 5 narrative intelligence gates. Dev Spec §2.9.
Usage:
  python -m tools.ci.run_narrative_gates --plan artifacts/compiled/plan_001.json --atoms-root atoms/ --mode warn
  python -m tools.ci.run_narrative_gates --plan plan.json --mode fail
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo root: tools/ci/ -> repo
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Run narrative gates on a compiled plan.")
    ap.add_argument("--plan", required=True, type=Path, help="Path to compiled plan JSON.")
    ap.add_argument("--atoms-root", type=Path, default=None, help="Atoms root (default: repo/atoms).")
    ap.add_argument("--mode", choices=("warn", "fail"), default="warn", help="warn: log errors but exit 0; fail: exit non-zero on any gate failure.")
    args = ap.parse_args()

    plan_path = args.plan
    if not plan_path.exists():
        print(f"Error: plan file not found: {plan_path}", file=sys.stderr)
        return 2
    atoms_root = args.atoms_root or REPO_ROOT / "atoms"

    with open(plan_path) as f:
        plan = json.load(f)

    # Load atom metadata for plan's persona/topic
    from phoenix_v4.qa.atom_metadata_loader import load_atom_metadata_for_plan
    from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation
    from phoenix_v4.qa.cost_gradient_gate import validate_cost_gradient
    from phoenix_v4.qa.callback_integrity_gate import validate_callback_integrity
    from phoenix_v4.qa.identity_shift_gate import validate_identity_shift
    from phoenix_v4.qa.macro_cadence_gate import validate_macro_cadence

    atom_metadata = load_atom_metadata_for_plan(plan, atoms_root=atoms_root)
    arc = plan.get("arc")  # optional; macro_cadence can use dominant_band_sequence if absent

    gates = [
        ("Mechanism Escalation", lambda: validate_mechanism_escalation(plan, atom_metadata)),
        ("Cost Gradient", lambda: validate_cost_gradient(plan, atom_metadata)),
        ("Callback Integrity", lambda: validate_callback_integrity(plan, atom_metadata)),
        ("Identity Shift", lambda: validate_identity_shift(plan, atom_metadata)),
        ("Macro-Cadence", lambda: validate_macro_cadence(plan, arc=arc)),
    ]
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for name, run in gates:
        result = run()
        for e in result.errors:
            all_errors.append(f"[{name}] {e}")
        for w in result.warnings:
            all_warnings.append(f"[{name}] {w}")

    for w in all_warnings:
        print("WARN:", w)
    for e in all_errors:
        print("ERROR:", e)

    if all_errors:
        print(f"\nTotal: {len(all_errors)} error(s), {len(all_warnings)} warning(s).")
        if args.mode == "fail":
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
