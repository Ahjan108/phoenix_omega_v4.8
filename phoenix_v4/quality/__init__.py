"""
Standalone creative QA tools. Used manually and in review cycles.
Not part of governance or CI. Directly tied to emotional impact.

- base: Exit code contract (0 PASS, 1 FAIL, 2 WARN) and parse_canonical_blocks() for CANONICAL.txt.
- story_atom_lint: Per-atom lint for CANONICAL.txt; single-blob for other .txt/.md.
- transformation_heatmap: Chapter-level recognition/reframe/challenge/relief/identity signals.
- memorable_line_detector: Highlight-density detection for editorial and marketing.
- marketing_assets_from_lines: Turn memorable-line JSON into quotes, pin captions, hooks, trailer lines, email subjects.
"""
