"""
Freebie renderer: single entry point for HTML/PDF freebie generation.
Loads templates from SOURCE_OF_TRUTH/freebies/templates (or config/freebies/templates),
injects metadata (topic, persona, slug, CTA), writes to artifacts/freebies/YYYY-MM-DD/,
appends per-file rows to artifact index. Optional PDF via WeasyPrint.

Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §8.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_ROOT_SOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "freebies" / "templates"
TEMPLATES_ROOT_CONFIG = REPO_ROOT / "config" / "freebies" / "templates"
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"
ARTIFACTS_FREEBIES = REPO_ROOT / "artifacts" / "freebies"


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}


def _resolve_template_root() -> Path:
    if TEMPLATES_ROOT_SOT.exists():
        return TEMPLATES_ROOT_SOT
    return TEMPLATES_ROOT_CONFIG


def load_template(file_template: str) -> str:
    """Load template content by filename. Look in SOT then config."""
    root = _resolve_template_root()
    path = root / file_template
    if not path.exists():
        raise FileNotFoundError(f"Freebie template not found: {path}")
    return path.read_text(encoding="utf-8")


def _render_cta(cta_template_id: str, topic: str, freebie_name: str, slug: str) -> str:
    cta_path = CONFIG_FREEBIES / "cta_templates.yaml"
    templates = _load_yaml(cta_path)
    t = templates.get(cta_template_id) or templates.get("tool_forward") or {}
    script = (t.get("script") or "").strip()
    return script.format(
        topic=topic.replace("_", " ").title(),
        freebie_name=freebie_name.replace("_", " ").title(),
        slug=slug,
    )


def inject_metadata(
    content: str,
    book_metadata: dict[str, Any],
    freebie_config: dict[str, Any],
    cta_text: str,
) -> str:
    """Replace {{placeholders}} with metadata. Includes author placeholders when author_assets present (Writer Spec §23)."""
    topic = (book_metadata.get("topic") or "").replace("_", " ").title()
    persona = (book_metadata.get("persona") or "").replace("_", " ").title()
    slug = book_metadata.get("slug") or ""
    freebie_name = (freebie_config.get("freebie_id") or "").replace("_", " ").title()
    title = book_metadata.get("title") or f"{freebie_name} — {topic}"

    replacements: dict[str, str] = {
        "{{topic}}": topic,
        "{{persona}}": persona,
        "{{slug}}": slug,
        "{{cta_text}}": cta_text,
        "{{freebie_name}}": freebie_name,
        "{{title}}": title,
    }
    # Author placeholders (Writer Spec §23) when author_assets in book_metadata
    author_assets = book_metadata.get("author_assets") or {}
    replacements["{{author_pen_name}}"] = author_assets.get("pen_name") or ""
    replacements["{{author_bio}}"] = author_assets.get("bio") or ""
    replacements["{{author_why_this_book}}"] = author_assets.get("why_this_book") or ""
    pre_intro = author_assets.get("audiobook_pre_intro") or {}
    if isinstance(pre_intro, dict):
        replacements["{{author_audiobook_pre_intro}}"] = "\n\n".join(
            v for k, v in sorted(pre_intro.items()) if isinstance(v, str) and v.strip()
        )
    else:
        replacements["{{author_audiobook_pre_intro}}"] = str(pre_intro) if pre_intro else ""

    out = content
    for k, v in replacements.items():
        out = out.replace(k, str(v))
    return out


def _md_to_html(md_content: str, title: str) -> str:
    """Wrap markdown in minimal HTML. No markdown parsing; body is pre-rendered or raw."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40em; margin: 2em auto; padding: 0 1em; line-height: 1.5; }}
    .cta {{ margin-top: 1.5em; padding: 1em; background: #f5f5f5; border-radius: 6px; }}
  </style>
</head>
<body>
<pre style="white-space: pre-wrap;">{md_content}</pre>
</body>
</html>"""


def _write_artifact(content: str, ext: str, slug: str, freebie_id: str) -> Path:
    """Write content to artifacts/freebies/YYYY-MM-DD/{slug}_{freebie_id}.{ext}. Return path."""
    ARTIFACTS_FREEBIES.mkdir(parents=True, exist_ok=True)
    date_dir = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = ARTIFACTS_FREEBIES / date_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_slug = (slug or "freebie").replace("/", "-")[:80]
    safe_id = (freebie_id or "freebie").replace("/", "-")[:40]
    name = f"{safe_slug}_{safe_id}.{ext}"
    path = out_dir / name
    path.write_text(content, encoding="utf-8")
    return path


def _append_artifact_index(row: dict[str, Any]) -> None:
    """Append one row to artifacts/freebies/artifacts_index.jsonl (per-file artifact log)."""
    index_path = ARTIFACTS_FREEBIES / "artifacts_index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def html_to_pdf(html_path: Path) -> Optional[Path]:
    """Convert HTML file to PDF using WeasyPrint. Returns PDF path or None if unavailable."""
    try:
        from weasyprint import HTML
        pdf_path = html_path.with_suffix(".pdf")
        HTML(filename=str(html_path)).write_pdf(pdf_path)
        return pdf_path
    except Exception:
        return None


def render_freebie(
    freebie_config: dict[str, Any],
    book_metadata: dict[str, Any],
    output_format: str = "html",
    *,
    templates_root: Optional[Path] = None,
    cta_templates_path: Optional[Path] = None,
    output_dir_override: Optional[Path] = None,
) -> Path:
    """
    Single entry point for freebie generation.

    Args:
        freebie_config: from registry (freebie_id, type, file_template, cta_style, ...).
        book_metadata: persona, topic, slug, cta_template_id, book_id, optional title.
        output_format: 'html' or 'pdf'.

    Returns:
        Path to generated file (HTML or PDF). Appends artifact row to artifacts_index.jsonl.
    """
    freebie_id = freebie_config.get("freebie_id") or ""
    file_template = freebie_config.get("file_template") or ""
    cta_style = freebie_config.get("cta_style") or "tool_forward"
    topic = book_metadata.get("topic") or ""
    persona = book_metadata.get("persona") or ""
    slug = book_metadata.get("slug") or ""
    cta_template_id = book_metadata.get("cta_template_id") or cta_style

    # Redirect: if freebie maps to landing, emit redirect HTML only (no template)
    to_landing = _load_yaml(CONFIG_FREEBIES / "freebie_to_landing.yaml")
    landing_id = (to_landing.get(freebie_id) or "").strip()
    if landing_id:
        kebab = landing_id.strip().lower().replace("_", "-")
        redirect_path = f"../../breathwork/lp-{kebab}.html"
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0;url={redirect_path}">
  <title>Redirect — Free Tool</title>
</head>
<body>
  <p>Redirecting… <a href="{redirect_path}">Click here</a> if not redirected.</p>
</body>
</html>"""
    else:
        if not file_template:
            raise ValueError(f"Freebie {freebie_id} has no file_template and no redirect.")
        raw = load_template(file_template)
        freebie_name = (freebie_id or "").replace("_", " ").title()
        cta_text = _render_cta(cta_template_id, topic, freebie_name, slug)
        content = inject_metadata(raw, book_metadata, freebie_config, cta_text)
        if file_template.endswith(".md"):
            title = book_metadata.get("title") or f"{freebie_name} — {topic}"
            content = _md_to_html(content, title)

    # Write HTML
    ext = "html"
    if output_dir_override is not None:
        ARTIFACTS_FREEBIES.mkdir(parents=True, exist_ok=True)
        out_dir = output_dir_override
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_slug = (slug or "freebie").replace("/", "-")[:80]
        safe_id = (freebie_id or "freebie").replace("/", "-")[:40]
        html_path = out_dir / f"{safe_slug}_{safe_id}.html"
        html_path.write_text(content, encoding="utf-8")
    else:
        html_path = _write_artifact(content, ext, slug, freebie_id)

    result_path = html_path
    if output_format == "pdf":
        pdf_path = html_to_pdf(html_path)
        if pdf_path is not None:
            result_path = pdf_path
            ext = "pdf"
        # else keep HTML path and ext

    # Artifact index row (per-file)
    file_hash = hashlib.sha256(result_path.read_bytes() if result_path.exists() else b"").hexdigest()[:16]
    row = {
        "freebie_id": freebie_id,
        "book_id": book_metadata.get("book_id") or "",
        "persona": persona,
        "topic": topic,
        "type": freebie_config.get("type") or "",
        "format": ext,
        "file_path": str(result_path),
        "slug": slug,
        "cta": cta_style,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hash": f"sha256:{file_hash}",
    }
    _append_artifact_index(row)

    return result_path


def _resolve_asset_from_store(
    store_root: Path,
    format_key: str,
    topic_id: str,
    persona_id: str,
    freebie_id: str,
) -> Optional[Path]:
    """Resolve pre-created asset path; try topic/persona then default/persona. Returns path if exists."""
    ext = "html" if format_key == "html" else "pdf" if format_key == "pdf" else "epub" if format_key == "epub" else "mp3"
    for topic in (topic_id, "default"):
        p = store_root / format_key / topic / persona_id / f"{freebie_id}.{ext}"
        if p.exists():
            return p
    return None


def generate_freebies_for_book(
    compiled_book: Any,
    book_spec: dict[str, Any],
    *,
    registry_path: Optional[Path] = None,
    include_pdf: bool = False,
    output_dir_override: Optional[Path] = None,
    formats: Optional[list[str]] = None,
    skip_audio: bool = False,
    asset_store_root: Optional[Path] = None,
    publish_dir: Optional[Path] = None,
) -> list[Path]:
    """
    Generate freebie artifacts (HTML, PDF, EPUB, MP3 as applicable).
    If asset_store_root is set, copy from store when available; else render from template.
    If publish_dir is set, copy each artifact to publish_dir/{slug}/ for public/free.
    """
    registry_path = registry_path or (CONFIG_FREEBIES / "freebie_registry.yaml")
    reg = _load_yaml(registry_path)
    freebies_map = reg.get("freebies") or {}

    # Use freebie fields from compiled_book (set by planner in run_pipeline)
    if isinstance(compiled_book, dict):
        bundle = compiled_book.get("freebie_bundle") or []
        bundle_with_formats = compiled_book.get("freebie_bundle_with_formats") or []
        cta_template_id = compiled_book.get("cta_template_id") or "tool_forward"
        freebie_slug = compiled_book.get("freebie_slug") or ""
        book_id = compiled_book.get("plan_hash") or compiled_book.get("book_id") or ""
    else:
        bundle = getattr(compiled_book, "freebie_bundle", None) or []
        bundle_with_formats = getattr(compiled_book, "freebie_bundle_with_formats", None) or []
        cta_template_id = getattr(compiled_book, "cta_template_id", None) or "tool_forward"
        freebie_slug = getattr(compiled_book, "freebie_slug", None) or ""
        book_id = getattr(compiled_book, "plan_hash", None) or ""

    topic_id = book_spec.get("topic_id") or book_spec.get("topic") or ""
    persona_id = book_spec.get("persona_id") or book_spec.get("persona") or ""

    if not formats:
        formats = ["html"]
        if include_pdf:
            formats.append("pdf")
    if skip_audio:
        formats = [f for f in formats if f != "mp3"]

    book_metadata = {
        "topic": topic_id,
        "persona": persona_id,
        "slug": freebie_slug,
        "cta_template_id": cta_template_id,
        "book_id": book_id,
        "title": book_spec.get("title") or "",
    }
    if isinstance(compiled_book, dict) and compiled_book.get("author_assets"):
        book_metadata["author_assets"] = compiled_book["author_assets"]

    paths: list[Path] = []
    for freebie_id in bundle or []:
        freebie_config = freebies_map.get(freebie_id)
        if not freebie_config:
            continue
        if not isinstance(freebie_config, dict):
            freebie_config = {"freebie_id": freebie_id, "file_template": "", "cta_style": cta_template_id, "type": ""}
        else:
            freebie_config = dict(freebie_config)
        freebie_config.setdefault("freebie_id", freebie_id)
        freebie_formats = [f for item in bundle_with_formats if item.get("freebie_id") == freebie_id for f in item.get("formats") or ["html"]]
        if not freebie_formats:
            freebie_formats = list(freebie_config.get("output_formats") or ["html"])

        for fmt in freebie_formats:
            if fmt not in formats:
                continue
            if asset_store_root:
                store_path = _resolve_asset_from_store(asset_store_root, fmt, topic_id, persona_id, freebie_id)
                if store_path and store_path.exists():
                    out_dir = output_dir_override or (ARTIFACTS_FREEBIES / datetime.now(timezone.utc).strftime("%Y-%m-%d"))
                    out_dir.mkdir(parents=True, exist_ok=True)
                    ext = store_path.suffix
                    dest = out_dir / f"{freebie_slug}_{freebie_id}{ext}"
                    dest.write_bytes(store_path.read_bytes())
                    paths.append(dest)
                    if publish_dir:
                        pub_dir = publish_dir / freebie_slug
                        pub_dir.mkdir(parents=True, exist_ok=True)
                        (pub_dir / f"{freebie_id}{ext}").write_bytes(store_path.read_bytes())
                    continue
            if fmt == "html":
                p = render_freebie(freebie_config, book_metadata, "html", output_dir_override=output_dir_override)
                paths.append(p)
                if publish_dir:
                    pub_dir = publish_dir / freebie_slug
                    pub_dir.mkdir(parents=True, exist_ok=True)
                    (pub_dir / f"{freebie_id}.html").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            elif fmt == "pdf":
                store_path = _resolve_asset_from_store(asset_store_root, "pdf", topic_id, persona_id, freebie_id) if asset_store_root else None
                if not store_path or not store_path.exists():
                    p = render_freebie(freebie_config, book_metadata, "pdf", output_dir_override=output_dir_override)
                    paths.append(p)
                    if publish_dir:
                        pub_dir = publish_dir / freebie_slug
                        pub_dir.mkdir(parents=True, exist_ok=True)
                        (pub_dir / f"{freebie_id}.pdf").write_bytes(p.read_bytes())
                else:
                    out_dir = output_dir_override or (ARTIFACTS_FREEBIES / datetime.now(timezone.utc).strftime("%Y-%m-%d"))
                    out_dir.mkdir(parents=True, exist_ok=True)
                    dest = out_dir / f"{freebie_slug}_{freebie_id}.pdf"
                    dest.write_bytes(store_path.read_bytes())
                    paths.append(dest)
                    if publish_dir:
                        pub_dir = publish_dir / freebie_slug
                        pub_dir.mkdir(parents=True, exist_ok=True)
                        (pub_dir / f"{freebie_id}.pdf").write_bytes(store_path.read_bytes())

    return paths


def main() -> int:
    """CLI: generate freebies from a compiled plan JSON."""
    import argparse
    ap = argparse.ArgumentParser(description="Render freebie HTML (and optional PDF) from plan JSON")
    ap.add_argument("plan", help="Path to compiled plan JSON (has freebie_bundle, cta_template_id, freebie_slug)")
    ap.add_argument("--pdf", action="store_true", help="Also generate PDF (requires weasyprint)")
    ap.add_argument("--out-dir", default=None, help="Override output directory (default: artifacts/freebies/YYYY-MM-DD)")
    args = ap.parse_args()
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=__import__("sys").stderr)
        return 1
    with open(plan_path, encoding="utf-8") as f:
        out = json.load(f)
    book_spec = {
        "topic_id": out.get("topic_id") or "",
        "persona_id": out.get("persona_id") or "",
        "topic": out.get("topic_id") or "",
        "persona": out.get("persona_id") or "",
    }
    out_dir = Path(args.out_dir) if args.out_dir else None
    paths = generate_freebies_for_book(out, book_spec, include_pdf=args.pdf, output_dir_override=out_dir)
    print(f"Generated {len(paths)} file(s):")
    for p in paths:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
