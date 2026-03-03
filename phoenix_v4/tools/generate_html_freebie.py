#!/usr/bin/env python3
"""
Freebie HTML (and companion) generator. Spec: PHOENIX_FREEBIE_SYSTEM_SPEC.md §8.

Inputs: topic, persona, engine, slug, cta_template_id, freebie_name, optional template path,
        optional color_theme (brand). Loads CTA from config/freebies/cta_templates.yaml and
        injects {topic}, {freebie_name}, {slug}. Outputs:
  - /public/free/{slug}/index.html
  - /public/free/{slug}/companion.html (workbook placeholder; print to PDF if needed)

No external dependencies for core generation.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}


def _render_cta(cta_templates: dict, cta_template_id: str, topic: str, freebie_name: str, slug: str) -> str:
    """Inject {topic}, {freebie_name}, {slug} into CTA template script."""
    template = cta_templates.get(cta_template_id) or cta_templates.get("tool_forward") or {}
    script = template.get("script") or ""
    return script.strip().format(
        topic=topic.replace("_", " ").title(),
        freebie_name=freebie_name.replace("_", " ").title(),
        slug=slug,
    )


def _landing_id_to_kebab(s: str) -> str:
    return (s or "").strip().lower().replace("_", "-")


def generate_html_freebie(
    topic: str,
    persona: str,
    engine: str,
    slug: str,
    cta_template_id: str = "tool_forward",
    freebie_name: str = "",
    freebie_id: Optional[str] = None,
    template_path: Optional[Path] = None,
    color_theme: Optional[str] = None,
    output_dir: Optional[Path] = None,
    cta_templates_path: Optional[Path] = None,
) -> Path:
    """
    Generate HTML freebie. If freebie_id maps in freebie_to_landing.yaml, index.html
    redirects to the email-capture landing page (public/breathwork/lp-{id}.html).
    Otherwise writes CTA page. Always writes companion.html (workbook placeholder).
    Returns path to index.html.
    """
    output_dir = output_dir or (REPO_ROOT / "public" / "free" / slug)
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_display = topic.replace("_", " ").title()
    mapping_path = CONFIG_FREEBIES / "freebie_to_landing.yaml"
    to_landing = _load_yaml(mapping_path)
    landing_id = (to_landing.get(freebie_id or "") or "").strip()

    if landing_id:
        # Redirect to breathwork landing page (email capture)
        kebab = _landing_id_to_kebab(landing_id)
        redirect_path = f"../../breathwork/lp-{kebab}.html"
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0;url={redirect_path}">
  <title>Redirect — Free Tool</title>
</head>
<body>
  <p>Redirecting to free tool… <a href="{redirect_path}">Click here</a> if not redirected.</p>
</body>
</html>
"""
    else:
        cta_templates_path = cta_templates_path or (CONFIG_FREEBIES / "cta_templates.yaml")
        cta_templates = _load_yaml(cta_templates_path)
        cta_text = _render_cta(cta_templates, cta_template_id, topic, freebie_name or slug, slug)
        persona_display = persona.replace("_", " ").title()
        theme_attr = f' data-theme="{color_theme}"' if color_theme else ""
        html = f"""<!DOCTYPE html>
<html lang="en"{theme_attr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Freebie — {topic_display} / {persona_display}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40em; margin: 2em auto; padding: 0 1em; line-height: 1.5; }}
    .cta {{ margin-top: 1.5em; padding: 1em; background: #f5f5f5; border-radius: 6px; }}
    .slug {{ font-size: 0.9em; color: #666; }}
  </style>
</head>
<body>
  <h1>Freebie: {topic_display}</h1>
  <p>Topic: {topic_display} | Persona: {persona_display} | Engine: {engine or "—"}</p>
  <p class="slug">Slug: {slug}</p>
  <div class="cta">
    <p>{cta_text}</p>
  </div>
</body>
</html>
"""
    out_file = output_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")

    # Companion (workbook) placeholder — static template; print to PDF if needed
    companion_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Companion — {topic_display}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40em; margin: 2em auto; padding: 0 1em; }}
  </style>
</head>
<body>
  <h1>Companion: {topic_display}</h1>
  <p>Slug: {slug}. Export or print this page to PDF for companion.pdf.</p>
</body>
</html>
"""
    (output_dir / "companion.html").write_text(companion_html, encoding="utf-8")

    return out_file


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate HTML freebie (spec §8)")
    ap.add_argument("--topic", required=True, help="Topic ID")
    ap.add_argument("--persona", required=True, help="Persona ID")
    ap.add_argument("--engine", default="", help="Engine ID")
    ap.add_argument("--slug", required=True, help="Freebie URL slug")
    ap.add_argument("--cta", default="tool_forward", help="CTA template id (e.g. tool_forward)")
    ap.add_argument("--freebie-name", default="", help="Primary freebie name for CTA copy")
    ap.add_argument("--freebie-id", default="", help="Primary freebie_id for redirect mapping (freebie_to_landing.yaml)")
    ap.add_argument("--template", default=None, help="Optional HTML template file (unused if not provided)")
    ap.add_argument("--theme", default=None, help="Color theme (brand)")
    ap.add_argument("--out-dir", default=None, help="Output directory (default: public/free/<slug>)")
    args = ap.parse_args()
    out_dir = Path(args.out_dir) if args.out_dir else None
    generate_html_freebie(
        topic=args.topic,
        persona=args.persona,
        engine=args.engine,
        slug=args.slug,
        cta_template_id=args.cta,
        freebie_name=args.freebie_name or args.slug,
        freebie_id=args.freebie_id or None,
        template_path=Path(args.template) if args.template else None,
        color_theme=args.theme,
        output_dir=out_dir,
    )
    print(f"Wrote {out_dir or REPO_ROOT / 'public' / 'free' / args.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
