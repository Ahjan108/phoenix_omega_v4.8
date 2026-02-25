"""
Tests for Phase 13-C — Deterministic Constraint Solver Wave Optimizer (DWO-CS).
Covers: solve with caps satisfied, determinism (same inputs -> same selection), infeasible.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _make_candidate(cid: str, topic: str = "anxiety", persona: str = "gen_z", arc: str = "arc1", band: str = "3-3-4", **kw) -> dict:
    d = {
        "candidate_id": cid,
        "candidate_sort_key": cid,
        "tuple_id": f"{persona}|{topic}|E1|F006",
        "brand_id": "phoenix",
        "persona_id": persona,
        "topic_id": topic,
        "engine_id": "E1",
        "arc_id": arc,
        "slot_sig": "sig1",
        "band_sig": band,
        "variation_signature": "V1",
        "teacher_mode": False,
        "teacher_id": None,
        "risk": "GREEN",
        "volatility": 0.5,
        "age_days": 5,
    }
    d.update(kw)
    return d


class TestWaveOptimizerSolver(unittest.TestCase):
    def test_solves_wave_with_caps_satisfied(self):
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        # 25 candidates with distinct wave_fingerprint (slot_sig/arc/band/var vary), target 10
        candidates = []
        for i in range(25):
            candidates.append(_make_candidate(
                f"book_{i:03d}",
                topic=f"topic_{i % 5}",
                persona=f"persona_{i % 4}",
                arc=f"arc_{i % 6}",
                band=f"{2 + (i % 3)}-{3 + (i % 2)}-4",
                slot_sig=f"slot_{i}",  # distinct so wave_fingerprint distinct
                variation_signature=f"V{i % 4}",  # 4 values so cap 3 allows 12, need 10
                engine_id=f"E{i % 3}",  # 3 engines so cap 8 allows 10
            ))
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {
                    "weekly_caps": {
                        "max_same_topic": 6,
                        "max_same_persona": 8,
                        "max_same_topic_persona_pair": 3,
                        "max_same_arc_id": 5,
                        "max_same_engine_id": 8,
                        "max_same_band_sig": 4,
                        "max_same_slot_sig": 4,
                        "max_same_variation_signature": 3,
                        "max_same_wave_fingerprint": 2,
                        "max_teacher_mode_books": 30,
                        "max_same_teacher_id": 10,
                    },
                },
                "objective": {"weights": {"topic_diversity": 25, "persona_diversity": 20, "arc_diversity": 20, "band_diversity": 15, "volatility_preference": 10, "freshness_preference": 5, "yellow_risk_penalty": 5}, "volatility_bins": {"low": 0.35, "high": 0.55}},
            },
        }
        selected, blocking, status = solve(candidates, 10, config, [], set())
        self.assertEqual(status, "SOLVED")
        self.assertEqual(len(selected), 10)
        self.assertIsNone(blocking)

    def test_determinism_same_inputs_twice(self):
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        candidates = [_make_candidate(f"b_{i}", topic="t1", persona="p1", arc=f"a_{i}") for i in range(15)]
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {"weekly_caps": {"max_same_topic": 10, "max_same_persona": 10, "max_same_arc_id": 3, "max_same_engine_id": 20, "max_same_band_sig": 10, "max_same_slot_sig": 10, "max_same_variation_signature": 10, "max_same_wave_fingerprint": 2, "max_teacher_mode_books": 30, "max_same_teacher_id": 10}},
                "objective": {"weights": {}, "volatility_bins": {}},
            },
        }
        sel1, _, st1 = solve(candidates, 5, config, [], set())
        sel2, _, st2 = solve(candidates, 5, config, [], set())
        self.assertEqual(st1, "SOLVED")
        self.assertEqual(st2, "SOLVED")
        ids1 = [c["candidate_id"] for c in sel1]
        ids2 = [c["candidate_id"] for c in sel2]
        self.assertEqual(ids1, ids2)

    def test_infeasible_insufficient_eligible(self):
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        candidates = [_make_candidate(f"b_{i}", risk="GREEN") for i in range(5)]
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {"weekly_caps": {}},
            },
        }
        selected, blocking, status = solve(candidates, 10, config, [], set())
        self.assertEqual(status, "INFEASIBLE")
        self.assertIsNotNone(blocking)
        self.assertTrue(any(b.get("code") == "INSUFFICIENT_ELIGIBLE_CANDIDATES" for b in blocking))

    def test_infeasible_eligible_but_caps_impossible(self):
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        # 10 candidates all same topic; cap max_same_topic = 2; target 5 -> we can only take 2 from that topic, so we need 3 more but we have no other topics
        candidates = [_make_candidate(f"b_{i}", topic="only_topic", persona="p1", arc=f"a_{i}") for i in range(10)]
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {
                    "weekly_caps": {
                        "max_same_topic": 2,
                        "max_same_persona": 10,
                        "max_same_arc_id": 10,
                        "max_same_engine_id": 10,
                        "max_same_band_sig": 10,
                        "max_same_slot_sig": 10,
                        "max_same_variation_signature": 10,
                        "max_same_wave_fingerprint": 10,
                        "max_teacher_mode_books": 30,
                        "max_same_teacher_id": 10,
                    },
                },
                "objective": {"weights": {}, "volatility_bins": {}},
            },
        }
        selected, blocking, status = solve(candidates, 5, config, [], set())
        self.assertEqual(status, "INFEASIBLE")
        self.assertLessEqual(len(selected), 2)

    def test_cross_brand_convergent_no_arc_overlap(self):
        """When CBDI marks (brand_a, brand_b) convergent, selection must not use same arc_id in both brands."""
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        # Brand A and B both have candidates with arc_x; convergent pair (A, B) -> at most one of A or B can use arc_x
        candidates = [
            _make_candidate("a1", brand_id="brand_a", arc="arc_x", topic="t1", persona="p1"),
            _make_candidate("a2", brand_id="brand_a", arc="arc_y", topic="t2", persona="p1"),
            _make_candidate("b1", brand_id="brand_b", arc="arc_x", topic="t1", persona="p2"),
            _make_candidate("b2", brand_id="brand_b", arc="arc_z", topic="t2", persona="p2"),
        ]
        for c in candidates:
            c.setdefault("slot_sig", c["candidate_id"])
            c.setdefault("variation_signature", "V1")
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {"weekly_caps": {"max_same_topic": 10, "max_same_persona": 10, "max_same_arc_id": 2, "max_same_engine_id": 10, "max_same_band_sig": 10, "max_same_slot_sig": 10, "max_same_variation_signature": 10, "max_same_wave_fingerprint": 10, "max_teacher_mode_books": 30, "max_same_teacher_id": 10}},
                "objective": {"weights": {}, "volatility_bins": {}},
            },
        }
        convergent_pairs = [("brand_a", "brand_b")]
        # Target 3: we can take a1(a,arc_x), a2(a,arc_y), b2(b,arc_z) but not both a1 and b1 (same arc_x)
        selected, _, status = solve(candidates, 3, config, convergent_pairs, set())
        self.assertEqual(status, "SOLVED")
        arcs_by_brand = {}
        for c in selected:
            b = c.get("brand_id", "")
            a = c.get("arc_id", "")
            arcs_by_brand.setdefault(b, set()).add(a)
        # arc_x must not appear in both brand_a and brand_b
        self.assertFalse(
            "arc_x" in (arcs_by_brand.get("brand_a") or set()) and "arc_x" in (arcs_by_brand.get("brand_b") or set()),
            "convergent pair must not share same arc_id",
        )

    def test_drift_critical_brand_new_arc_cap(self):
        """When brand is drift-critical, at most max_new_arcs_per_brand_when_critical with is_new_arc=True."""
        from phoenix_v4.ops.wave_optimizer_constraint_solver import solve
        candidates = [
            _make_candidate("c1", brand_id="drift_brand", arc="old_arc", topic="t1", persona="p1", is_new_arc=False),
            _make_candidate("c2", brand_id="drift_brand", arc="new_1", topic="t2", persona="p1", is_new_arc=True),
            _make_candidate("c3", brand_id="drift_brand", arc="new_2", topic="t1", persona="p2", is_new_arc=True),
            _make_candidate("c4", brand_id="drift_brand", arc="new_3", topic="t2", persona="p2", is_new_arc=True),
        ]
        for c in candidates:
            c.setdefault("slot_sig", c["candidate_id"])
            c.setdefault("variation_signature", "V1")
        config = {
            "wave_optimizer": {
                "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                "hard_constraints": {
                    "weekly_caps": {"max_same_topic": 10, "max_same_persona": 10, "max_same_arc_id": 10, "max_same_engine_id": 10, "max_same_band_sig": 10, "max_same_slot_sig": 10, "max_same_variation_signature": 10, "max_same_wave_fingerprint": 10, "max_teacher_mode_books": 30, "max_same_teacher_id": 10},
                    "brand_identity": {"max_new_arcs_per_brand_when_critical": 2},
                },
                "objective": {"weights": {}, "volatility_bins": {}},
            },
        }
        drift_critical_brands = {"drift_brand"}
        # Target 3: cap 2 new arcs + 1 old = 3 max
        selected, _, status = solve(candidates, 3, config, [], drift_critical_brands)
        self.assertEqual(status, "SOLVED")
        new_arc_count = sum(1 for c in selected if c.get("brand_id") == "drift_brand" and c.get("is_new_arc"))
        self.assertLessEqual(new_arc_count, 2, "drift-critical brand must respect new_arc cap")


class TestRunAndCLI(unittest.TestCase):
    def test_run_produces_solution_or_infeasible(self):
        from phoenix_v4.ops.wave_optimizer_constraint_solver import run
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            candidates_path = tmp_path / "candidates.json"
            candidates_path.write_text(json.dumps([
                _make_candidate(f"b_{i}", topic=f"t_{i % 4}", persona=f"p_{i % 3}", arc=f"a_{i % 5}")
                for i in range(30)
            ]))
            ops_dir = tmp_path / "ops"
            ops_dir.mkdir()
            config = {
                "wave_optimizer": {
                    "eligibility": {"exclude_risks": ["BLOCKER", "RED"], "allow_yellow": True},
                    "hard_constraints": {"weekly_caps": {"max_same_topic": 10, "max_same_persona": 10, "max_same_arc_id": 5, "max_same_engine_id": 20, "max_same_band_sig": 10, "max_same_slot_sig": 10, "max_same_variation_signature": 10, "max_same_wave_fingerprint": 5, "max_teacher_mode_books": 30, "max_same_teacher_id": 10}},
                    "objective": {"weights": {}, "volatility_bins": {}},
                },
            }
            result = run("2026-W10", 10, candidates_path, ops_dir, config)
            self.assertIn(result["status"], ("SOLVED", "INFEASIBLE"))
            self.assertEqual(result["wave_id"], "2026-W10")
            self.assertEqual(result["target_size"], 10)
            if result["status"] == "SOLVED":
                self.assertEqual(len(result["selected"]), 10)


if __name__ == "__main__":
    unittest.main()
