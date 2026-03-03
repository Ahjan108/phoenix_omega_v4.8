# 3-Book Stress Test Summary

**Lane:** `nyc_executives × self_worth × (shame + comparison)`  
**Format:** 12 chapters, standard_book, F006  
**Seeds:** book001, book002, book003

---

## 1. Compile status

| Book       | Plan file                 | Seed    | Curve validation |
|-----------|---------------------------|---------|-------------------|
| Book_001  | artifacts/book_001.plan.json | book001 | **PASS**          |
| Book_002  | artifacts/book_002.plan.json | book002 | **PASS** (after full BAND tagging) |
| Book_003  | artifacts/book_003.plan.json | book003 | **PASS** (after full BAND tagging) |

**Pool:** All 40 STORY atoms (20 comparison + 20 shame) now have explicit BAND. Target distribution per engine: 1:1, 2:4, 3:7, 4:5, 5:3. Validator reports `bands=[1, 2, 3, 4, 5]` for both engines.

---

## 2. STORY atom overlap (12 per book)

**Book_001:**  
comparison_RECOGNITION_v05, comparison_MECHANISM_PROOF_v03, comparison_RECOGNITION_v02, comparison_TURNING_POINT_v03, shame_MECHANISM_PROOF_v04, shame_TURNING_POINT_v04, comparison_EMBODIMENT_v01, comparison_EMBODIMENT_v02, shame_RECOGNITION_v04, comparison_MECHANISM_PROOF_v04, shame_MECHANISM_PROOF_v03, shame_RECOGNITION_v03

**Book_002:**  
comparison_TURNING_POINT_v03, comparison_RECOGNITION_v03, comparison_TURNING_POINT_v04, shame_RECOGNITION_v02, comparison_TURNING_POINT_v02, shame_MECHANISM_PROOF_v04, comparison_TURNING_POINT_v05, shame_RECOGNITION_v05, shame_MECHANISM_PROOF_v01, comparison_MECHANISM_PROOF_v02, shame_RECOGNITION_v04, comparison_RECOGNITION_v02

**Book_003:**  
comparison_EMBODIMENT_v05, shame_RECOGNITION_v05, shame_RECOGNITION_v01, shame_TURNING_POINT_v05, shame_EMBODIMENT_v05, comparison_TURNING_POINT_v05, comparison_RECOGNITION_v02, shame_MECHANISM_PROOF_v05, shame_EMBODIMENT_v04, shame_RECOGNITION_v04, shame_EMBODIMENT_v02, shame_MECHANISM_PROOF_v01

**Pairwise overlap (atoms used in both):**

| Pair       | Overlap count | Atoms |
|------------|----------------|-------|
| 001 vs 002 | 4              | comparison_RECOGNITION_v02, comparison_TURNING_POINT_v03, shame_MECHANISM_PROOF_v04, shame_RECOGNITION_v04 |
| 001 vs 003 | 2              | comparison_RECOGNITION_v02, shame_RECOGNITION_v04 |
| 002 vs 003 | 4              | shame_RECOGNITION_v04, comparison_RECOGNITION_v02, shame_MECHANISM_PROOF_v01, comparison_TURNING_POINT_v05 |

**All three books:** 2 atoms appear in every book — comparison_RECOGNITION_v02, shame_RECOGNITION_v04.

---

## 3. BAND curve shape (dominant_band_sequence)

After full pool BAND tagging, all three books pass curve (≥3 distinct bands, no >3 consecutive same). See plan JSONs for per-book `dominant_band_sequence`.

---

## 4. Next steps

- Compile Book_004 and Book_005 (new seeds). If all five pass curve without manual adjustment, inventory stability is proven.
- Then consider second persona (e.g. educators × anxiety × shame) or same persona × different engine.
</think>
Fixing the overlap table and adding BAND curves.
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace