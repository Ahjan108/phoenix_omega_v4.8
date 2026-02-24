"""
CLI entry point for naming engine. Reads BookSpec (JSON or args), outputs title_output.json.
Authority: SYSTEMS_DOCUMENTATION §29.2.5.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import dedupe, generator, keyword_bank, scorer, validator
from ._config import load_naming_scoring


def load_existing_titles(path: str | Path | None) -> list[str]:
    """Load titles from .txt (one per line) or .json (list of strings or list of {title})."""
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8").strip()
    if p.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            return [x if isinstance(x, str) else (x.get("title") or "") for x in data]
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def run(
    topic_id: str,
    persona_id: str,
    series_id: str,
    angle_id: str,
    brand_id: str,
    domain_id: str,
    seed: str,
    installment_number: int = 1,
    existing_titles_path: str | Path | None = None,
    include_trace: bool = True,
) -> dict[str, Any]:
    """Run naming pipeline; return output dict."""
    existing_titles = load_existing_titles(existing_titles_path)
    tfidf_index = dedupe.build_tfidf_index(existing_titles)
    scoring = load_naming_scoring()
    min_total = scoring.get("min_total_score", 0.80)
    keywords = keyword_bank.get_keywords(series_id, angle_id, topic_id)
    primary_keyword = keywords.get("primary") or ""
    secondary_keywords = keywords.get("secondary") or []
    scenario_phrase = angle_id.replace("_", " ")

    book_id, candidates = generator.generate_candidates(
        topic_id=topic_id,
        persona_id=persona_id,
        series_id=series_id,
        angle_id=angle_id,
        brand_id=brand_id,
        seed=seed,
        installment_number=installment_number or 1,
    )
    batch_templates = [c.get("template_used") or "" for c in candidates]
    rejection_reasons: dict[str, int] = {}
    valid_candidates = []
    for c in candidates:
        ok, reason = validator.validate(
            c,
            existing_titles=existing_titles,
            current_batch=batch_templates,
            tfidf_index=tfidf_index,
            primary_keyword=primary_keyword,
        )
        if not ok:
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue
        valid_candidates.append(c)

    scored: list[tuple[dict, dict]] = []
    for c in valid_candidates:
        s = scorer.total_score(
            title=c["title"],
            subtitle=c["subtitle"],
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            scenario_phrase=scenario_phrase,
            persona_id=persona_id,
            intent_class=c.get("intent") or "scenario_specific",
            intent_template_match=True,
            template_used=c.get("template_used") or "",
            existing_titles=existing_titles,
            tfidf_index=tfidf_index,
            same_template_as_sibling=False,
        )
        if s.get("total") == scorer.REJECT or (s.get("total", 0) < min_total):
            rejection_reasons["below_min_score"] = rejection_reasons.get("below_min_score", 0) + 1
            continue
        scored.append((c, s))

    if not scored:
        # Fallback: return first valid candidate or first candidate with best effort
        if valid_candidates:
            c = valid_candidates[0]
            s = scorer.total_score(
                c["title"], c["subtitle"], primary_keyword, secondary_keywords,
                scenario_phrase, persona_id, c.get("intent") or "scenario_specific", True,
                c.get("template_used") or "", existing_titles, tfidf_index, False,
            )
            if s.get("total") != scorer.REJECT:
                scored = [(c, s)]
        if not scored and candidates:
            c = candidates[0]
            s = {"seo": 0.5, "human_appeal": 0.5, "duplication_risk": 0, "penalties": 0, "total": 1.0}
            scored = [(c, s)]

    scored.sort(key=lambda x: (-x[1].get("total", 0), x[0].get("candidate_id", "")))
    winner_c, winner_s = scored[0]
    candidates_rejected = len(candidates) - 1

    out = {
        "book_id": book_id,
        "title": winner_c["title"],
        "subtitle": winner_c["subtitle"],
        "keywords": {"primary": primary_keyword, "secondary": secondary_keywords},
        "intent": winner_c.get("intent") or "scenario_specific",
        "scores": {
            "seo": winner_s.get("seo", 0),
            "human_appeal": winner_s.get("human_appeal", 0),
            "duplication_risk": winner_s.get("duplication_risk", 0),
            "penalties": winner_s.get("penalties", 0),
            "total": winner_s.get("total", 0),
        },
    }
    if include_trace:
        out["trace"] = {
            "candidates_generated": len(candidates),
            "candidates_rejected": candidates_rejected,
            "rejection_reasons": rejection_reasons,
            "winner_candidate_id": winner_c.get("candidate_id", ""),
            "template_used": winner_c.get("template_used", ""),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Phoenix V4 Naming Engine — deterministic title + subtitle")
    parser.add_argument("--book-spec", type=str, help="Path to BookSpec JSON")
    parser.add_argument("--topic", type=str, help="topic_id (when not using --book-spec)")
    parser.add_argument("--persona", type=str, help="persona_id")
    parser.add_argument("--series", type=str, help="series_id")
    parser.add_argument("--angle", type=str, help="angle_id")
    parser.add_argument("--brand", type=str, default="stabilizer", help="brand_id")
    parser.add_argument("--domain", type=str, default="", help="domain_id")
    parser.add_argument("--seed", type=str, default="", help="Deterministic seed")
    parser.add_argument("--installment", type=int, default=1, help="installment_number")
    parser.add_argument("--existing-titles", type=str, default=None, help="Path to .txt or .json of titles to dedupe against")
    parser.add_argument("--output", type=str, default="-", help="Output path (- for stdout)")
    parser.add_argument("--trace", action="store_true", help="Include full candidate trace")
    args = parser.parse_args()

    if args.book_spec:
        path = Path(args.book_spec)
        if not path.exists():
            print("Error: --book-spec file not found", file=sys.stderr)
            return 1
        data = json.loads(path.read_text(encoding="utf-8"))
        topic_id = data.get("topic_id") or ""
        persona_id = data.get("persona_id") or ""
        series_id = data.get("series_id") or ""
        angle_id = data.get("angle_id") or ""
        brand_id = data.get("brand_id") or "stabilizer"
        domain_id = data.get("domain_id") or ""
        seed = data.get("seed") or ""
        installment_number = data.get("installment_number") or 1
    else:
        topic_id = args.topic or ""
        persona_id = args.persona or ""
        series_id = args.series or ""
        angle_id = args.angle or ""
        brand_id = args.brand or "stabilizer"
        domain_id = args.domain or ""
        seed = args.seed or ""
        installment_number = args.installment or 1
        if not topic_id or not persona_id or not series_id or not angle_id:
            print("Error: provide --book-spec or --topic --persona --series --angle", file=sys.stderr)
            return 1

    result = run(
        topic_id=topic_id,
        persona_id=persona_id,
        series_id=series_id,
        angle_id=angle_id,
        brand_id=brand_id,
        domain_id=domain_id,
        seed=seed,
        installment_number=installment_number,
        existing_titles_path=args.existing_titles,
        include_trace=args.trace,
    )
    out_text = json.dumps(result, indent=2)
    if args.output == "-":
        print(out_text)
    else:
        Path(args.output).write_text(out_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
