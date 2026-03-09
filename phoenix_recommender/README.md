# Phoenix Recommender v1.0 — Rules-Based Book Recommendation Engine

A production-quality, catalog-facing recommendation system that decides which books Phoenix should create next.

## Overview

Phoenix Recommender v1 is a **rules-based, Phase 1 recommender** that:

1. Generates all valid book candidates from cross-product of personas × topics × teachers × languages × formats × cities
2. Applies hard gates to prune invalid combinations early
3. Builds feature vectors for each candidate (market demand, coverage gaps, teacher fit, etc.)
4. Scores candidates using weighted feature formula
5. Applies constraints (per-cycle limits, language floors, diversity minimums)
6. Generates ranked recommendations with exploit/explore split
7. Outputs JSON and Markdown reports for human review

### Key Characteristics

- **Config-driven**: All weights, constraints, and mappings live in YAML (not hardcoded)
- **Canonical-data validated**: All IDs validated against canonical personas, topics, teacher atoms
- **Reason codes**: Every recommendation includes human-readable justification
- **Hard gates first**: Invalid candidates rejected early (teacher coverage, language-city affinity, etc.)
- **Graceful degradation**: Missing data directories return neutral (0.5) scores, not errors

## Architecture

```
candidate_generator.py   → Generates valid candidates (handles topic mapping)
    ↓
feature_builder.py       → Builds feature vectors per candidate
    ↓
scoring_model.py         → Weighted scoring with reason codes
    ↓
ranker.py                → Applies constraints & exploit/explore split
    ↓
recommendation_report.py → JSON + Markdown output
    ↓
cli.py                   → CLI interface & orchestration
```

## Data Flow

### Hard Gates (Candidate Generation)

Applied early to prune invalid combinations:

1. **teacher_topic_coverage**: Teacher must have atoms for the topic
   - Loads from `pearl_news/atoms/teacher_quotes_practices/topic_*.yaml`
   - Uses `config/recommender/topic_mapping.yaml` to map canonical topics → pearl_news atom topics

2. **language_city_affinity**: Language-city pairs must be reasonable
   - e.g., `ja-JP` only pairs with `tokyo`, `zh-CN` only with `shanghai`
   - Prevents nonsensical recommendations (English teacher in Tokyo, etc.)

### Feature Scoring

Eight positive features (weights sum to 1.0):
- `market_demand` (0.25): Relevance to current market signals
- `coverage_gap` (0.20): Opportunity (1.0 if catalog missing, decreases with saturation)
- `performance_lift` (0.20): Expected engagement improvement
- `teacher_fit` (0.10): Teacher atoms available for topic
- `city_relevance` (0.10): Audience density in geographic overlay
- `seasonality` (0.05): Seasonal demand alignment
- `strategic_priority` (0.05): Quarterly objective fit
- `brand_need` (0.05): Brand-specific format/topic gaps

Three penalty features (subtracted from score):
- `duplication_risk` (0.15): Semantic similarity to catalog
- `saturation_penalty` (0.10): Topic oversaturation in current cycle
- `policy_risk` (0.10): Content/policy violations

Formula: `score = Σ(weight × feature) − Σ(penalty × feature)`, clamped to [0, 1]

### Constraint Application

Applied after scoring:

1. **Per-cycle limits**:
   - Max 5 recommendations per brand
   - Max 8 recommendations per topic
   - Max 6 recommendations per teacher

2. **Language floors**:
   - English: 30% minimum
   - Mandarin (zh-CN): 15% minimum
   - Japanese (ja-JP): 10% minimum
   - Korean (ko-KR): 10% minimum

3. **Diversity minimums**:
   - 5 unique personas
   - 8 unique topics
   - 4 unique teachers

4. **Exploit/explore split**:
   - Exploit slots (80%): Highest scores (low uncertainty, proven demand)
   - Explore slots (20%): Moderate scores with high potential (discovery, underserved segments)

## Configuration Files

### `/config/recommender/scoring_weights.yaml`

Defines weights and penalties for the scoring formula. All weights should sum to 1.0 for interpretability.

```yaml
weights:
  market_demand: 0.25
  coverage_gap: 0.20
  ...
penalties:
  duplication_risk: 0.15
  ...
```

### `/config/recommender/constraints.yaml`

Defines per-cycle limits, language floors, and diversity minimums.

```yaml
per_cycle:
  max_per_brand: 5
  max_per_topic: 8
  max_per_teacher: 6
language_floors:
  en: 0.30
  zh-CN: 0.15
  ...
```

### `/config/recommender/hard_gates.yaml`

Defines validation gates applied during candidate generation. All marked `fatal: true` will reject invalid candidates.

```yaml
gates:
  - id: teacher_topic_coverage
    fatal: true
  - id: language_city_affinity
    # Note: implemented in candidate_generator.py, not declarative yet
```

### `/config/recommender/topic_mapping.yaml`

Maps canonical topics (from `config/catalog_planning/canonical_topics.yaml`) to pearl_news atom topics (from `pearl_news/atoms/teacher_quotes_practices/topic_*.yaml`).

For v1, only mapped topics are used; unmapped topics generate no candidates.

```yaml
mappings:
  anxiety: mental_health      # canonical → pearl_news atom topic
  boundaries: mental_health
  ...
available_atom_topics:
  - climate
  - economy_work
  - education
  ...
```

## Module Reference

### candidate_generator.py

**Functions:**
- `load_canonical_personas()`: Read from `config/catalog_planning/canonical_personas.yaml`
- `load_canonical_topics()`: Read from `config/catalog_planning/canonical_topics.yaml`
- `load_topic_mapping()`: Read from `config/recommender/topic_mapping.yaml` (cached)
- `load_teachers_for_topic(topic)`: Read teachers from mapped atom topic YAML
- `generate_candidates()`: Generate cross-product with hard gates applied
- `generate_candidate_id(...)`: Deterministic hash of candidate components

**Output:** List of candidate dicts with:
```python
{
    "candidate_id": "abc123def456",
    "persona": "gen_z_professionals",
    "topic": "anxiety",
    "teacher": "ahjan",
    "language": "en",
    "format": "core",
    "city_overlay": "nyc",
    "gate_results": {
        "teacher_topic_coverage": True,
        "language_city_affinity": True,
    }
}
```

### feature_builder.py

**Functions:**
- `build_feature_vector(candidate)`: Returns dict mapping feature_name → score [0, 1]
- Individual feature builders:
  - `build_market_demand_feature()`: Signal freshness (v1: stub → 0.5)
  - `build_coverage_gap_feature()`: Catalog saturation (v1: 1.0 if no catalog, 0.5 if catalog exists)
  - `build_performance_feature()`: Engagement lift (v1: stub → 0.5)
  - `build_teacher_fit_feature()`: Teacher atoms for topic (1.0 if yes, 0.3 if no)
  - `build_city_relevance_feature()`: Geographic demand (v1: stub → 0.5)
  - `build_seasonality_feature()`: Seasonal alignment (v1: stub → 0.5)
  - `build_strategic_priority_feature()`: Quarterly focus (v1: stub → 0.5)
  - `build_brand_need_feature()`: Brand gaps (v1: stub → 0.5)
  - Penalty builders (duplication_risk, saturation_penalty, policy_risk)

### scoring_model.py

**Functions:**
- `load_scoring_config()`: Load weights and penalties from YAML
- `compute_score(features, weights, penalties)`: Returns (score, breakdown)
  - breakdown: dict showing each component's contribution
- `extract_reason_codes(features, breakdown)`: Identify high-value components (threshold: 0.07)
- `score_candidate(candidate, features)`: Wrapper returning {score, breakdown, reason_codes}

**Reason codes** (auto-generated):
- `high_demand`, `coverage_gap`, `performance_lift`, `strong_teacher_fit`
- `city_relevant`, `seasonal_demand`, `strategic_priority`, `brand_need`
- `duplication_risk_risk`, `saturation_penalty_risk`, `policy_risk_risk`

### ranker.py

**Functions:**
- `load_constraints_config()`: Load from `config/recommender/constraints.yaml`
- `apply_per_cycle_limits()`: Filter by brand/topic/teacher counts
- `apply_language_floors()`: Log warnings if language ratios below minimums
- `apply_diversity_constraints()`: Check persona/topic/teacher coverage (log warnings)
- `apply_explore_exploit_split()`: Tag with slot_type and position
- `rank_candidates(scored_candidates, top_n)`: Main orchestrator

**Output:** Ranked candidates with:
```python
{
    ...scored_candidate fields...,
    "position": 1,
    "slot_type": "exploit",  # or "explore"
    "_diversity_metrics": {
        "unique_personas": 8,
        "unique_topics": 12,
        "unique_teachers": 6,
    }
}
```

### recommendation_report.py

**Functions:**
- `generate_json_report()`: Write `artifacts/recommendations/ranked.json`
- `generate_markdown_report()`: Write `artifacts/recommendations/summary.md`
- `generate_reports(ranked_candidates, output_dir)`: Wrapper returning (json_path, markdown_path)

**JSON schema** (`ranked.json`):
```json
{
  "metadata": {
    "generated_at": "ISO timestamp",
    "total_candidates_scored": N,
    "recommender_version": "1.0.0"
  },
  "candidates": [
    {
      "position": 1,
      "candidate_id": "...",
      "persona": "...",
      "topic": "...",
      "teacher": "...",
      "language": "...",
      "format": "...",
      "city_overlay": "...",
      "score": 0.75,
      "reason_codes": ["high_demand", "coverage_gap"],
      "slot_type": "exploit"
    }
  ]
}
```

**Markdown schema** (`summary.md`):
- Header with timestamp and summary counts
- Diversity metrics
- Ranked candidates table (rank, ID, persona, topic, teacher, language, format, city, score, reasons, slot)
- Exploration strategy section (why each explore slot was chosen)

## CLI Usage

### Basic Recommendation Run

```bash
cd /sessions/busy-vibrant-maxwell/mnt/phoenix_omega
python3 -m phoenix_recommender --top 50
```

Outputs:
- `artifacts/recommendations/ranked.json` (full data)
- `artifacts/recommendations/summary.md` (human-readable)

### Dry-Run Mode (Generate Candidates Only)

```bash
python3 -m phoenix_recommender --dry-run
```

Shows candidate generation summary, exits before scoring.

### Explain a Candidate

```bash
python3 -m phoenix_recommender --top 50 --explain fbe52a0a7c95
```

Shows full breakdown of one candidate's score, including:
- Basic info (persona, topic, teacher, language, format, city)
- Final score and reason codes
- Detailed breakdown (each feature value, weight/penalty, contribution)

### Advanced Options

```bash
python3 -m phoenix_recommender \
  --top 100 \
  --explore-ratio 0.25 \
  --out /custom/output/dir \
  --brands phoenix_v4,pearl_prime
```

- `--top N`: Return top N recommendations (default 50)
- `--explore-ratio`: Override explore/exploit split (default from config)
- `--out DIR`: Custom output directory
- `--brands`: Filter by brands (comma-separated, optional for v1)
- `--dry-run`: Candidate generation only
- `--explain CANDIDATE_ID`: Full breakdown for one candidate

## Running Directly from Python

```python
from phoenix_recommender.candidate_generator import generate_candidates
from phoenix_recommender.feature_builder import build_feature_vector
from phoenix_recommender.scoring_model import score_candidate
from phoenix_recommender.ranker import rank_candidates
from phoenix_recommender.recommendation_report import generate_reports

# Generate candidates
candidates = generate_candidates()  # 10,800 for v1

# Score all
scored = []
for candidate in candidates:
    features = build_feature_vector(candidate)
    result = score_candidate(candidate, features)
    scored_candidate = candidate.copy()
    scored_candidate.update(result)
    scored.append(scored_candidate)

# Rank
ranked = rank_candidates(scored, top_n=50)

# Report
json_path, md_path = generate_reports(ranked)
```

## v1 Limitations & Future Work

### Feature Scoring (Stubs for v1)

The following features return neutral (0.5) pending data:

- **market_demand**: Waiting for `signals/research/` data pipeline
  - TODO: Implement freshness-weighted relevance scoring

- **performance_lift**: Stub pending performance analytics
  - TODO: Score by learner engagement, completion, satisfaction for similar persona/topic combos

- **city_relevance**: Stub pending market research
  - TODO: Score by geographic audience density, language prevalence, regional demand signals

- **seasonality**: Stub pending calendar/event data
  - TODO: Score by seasonal patterns, school/work cycle relevance, event alignment

- **strategic_priority**: Stub pending quarterly planning
  - TODO: Score by OKR alignment, persona investment strategy, topic expansion priorities

- **brand_need**: Stub pending brand registry
  - TODO: Score by brand format availability, catalog gaps per brand, brand-specific topic focus

### Hard Gates

Currently implemented in code:
- `teacher_topic_coverage`: Via topic_mapping and atom YAML inspection
- `language_city_affinity`: Via hardcoded mappings in candidate_generator.py

Future: Consider moving to declarative YAML (hard_gates.yaml) with pluggable validators.

### Topic Mapping (v1)

v1 uses manual `config/recommender/topic_mapping.yaml` to bridge canonical topics → pearl_news atom topics.

Future: Once catalog/signals topology stabilizes, could auto-detect mappings or use semantic similarity.

### Language/City Affinity

v1 uses hardcoded mappings (e.g., ja-JP → tokyo, zh-CN → shanghai).

Future:
- Move to config file
- Add intermediate geographic overlays (e.g., Singapore for both zh-SG and en)
- Consider cultural/dialect nuances (zh-HK vs zh-SG vs zh-CN)

### Diversity Constraints

v1 applies minimums but logs only (non-fatal).

Future: Could add soft constraints that rerank to improve diversity without rejecting high-scoring candidates.

### Duplication Detection

v1 returns 0.0 (no duplication risk).

TODO: Implement semantic similarity scoring against existing catalog once available.

### Constraint Solver

v1 applies constraints sequentially (limits → language floors → diversity → split).

Future: Consider ILP (integer linear programming) solver for simultaneous multi-constraint optimization.

## Testing

### Unit Tests (Not Yet Implemented)

Each module should have a `pytest` test suite covering:
- Feature calculations with edge cases
- Scoring formula correctness
- Constraint application
- Report generation

### Integration Tests

End-to-end pipeline validation:
```bash
python3 -m pytest tests/integration/test_full_pipeline.py
```

### Manual Testing

```bash
# Candidate generation
python3 -m phoenix_recommender.candidate_generator

# Feature building
python3 -m phoenix_recommender.feature_builder

# Scoring
python3 -m phoenix_recommender.scoring_model

# Ranking
python3 -m phoenix_recommender.ranker

# Full pipeline
python3 -m phoenix_recommender --top 25
```

## Performance Notes

### Generation Phase (Candidate Generation)

For v1 parameters (10 personas × 15 topics × up to 6 teachers × 7 languages × 3 formats × ~3 cities per language):

Theoretical max: 10 × 15 × 6 × 7 × 3 × 3 = **56,700 candidates**

Actual (with hard gates): ~**10,800 candidates** (after teacher topic coverage + language/city filtering)

### Scoring Phase

Scoring 10,800 candidates on a modern machine: ~5-10 seconds (vectorization possible for v2)

### Ranking Phase

Constraint application + split: <1 second

### Memory

Full pipeline: ~200-300 MB (mostly candidate dicts in memory)

## Production Deployment

### Environment Setup

```bash
cd /sessions/busy-vibrant-maxwell/mnt/phoenix_omega
pip install pyyaml
```

### CI/CD Integration

Recommend adding to nightly pipeline:

```bash
python3 -m phoenix_recommender --top 50 --out artifacts/recommendations/
# Email summary.md to team
```

### Monitoring

Track over time:
- Top-N score distribution
- Diversity metrics (unique personas/topics/teachers in recommendations)
- Constraint violation frequency (language floor misses, diversity shortfalls)
- Exploit/explore split (do explore slots get picked? A/B test impact)

### Updating Recommendations

To regenerate recommendations:

```bash
# Manually (immediate)
python3 -m phoenix_recommender --top 50 --out artifacts/recommendations/

# Or update config and re-run:
vim config/recommender/scoring_weights.yaml  # adjust weights
python3 -m phoenix_recommender --top 50
```

No database, no cache invalidation — fully config-driven.

## Contributing

To extend the recommender:

1. **Add a feature**:
   - Implement `build_my_feature_feature()` in `feature_builder.py`
   - Add entry to `load_scoring_config()` weights or penalties
   - Test with `scoring_model.py` example

2. **Change scoring formula**:
   - Edit `config/recommender/scoring_weights.yaml`
   - Run full pipeline and compare ranked outputs

3. **Add a constraint**:
   - Implement in `ranker.py` apply_* function
   - Add config section to `config/recommender/constraints.yaml`
   - Test with ranker.py example

4. **New hard gate**:
   - Implement validation function in `candidate_generator.py`
   - Apply in `generate_candidates()` loop
   - Document in hard_gates.yaml (eventually)

## Version History

**v1.0.0** (2026-03-07)
- Initial release
- Rules-based scoring with weighted features
- Constraint application (per-cycle, language floors, diversity)
- Exploit/explore split
- JSON + Markdown reports
- CLI with explain mode
- Topic mapping bridge (canonical → pearl_news)
- Multiple feature stubs pending data availability
