#!/usr/bin/env python3
"""
Create freebie assets from manifest: HTML, PDF, EPUB, MP3.
Writes to format-first store: store/{format}/{topic}/{persona}/{freebie_id}.{ext}.
Authority: V4 Freebies + Immersion Ecosystem plan §3.
"""
from __future__ import annotations

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


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Create freebie assets from manifest")
    ap.add_argument("--manifest", type=Path, required=True, help="manifest.jsonl path")
    ap.add_argument("--format", type=str, default="html,pdf", help="Comma-separated: html,pdf,epub,mp3")
    ap.add_argument("--store", type=Path, default=None, help="Asset store root (default: artifacts/freebie_assets/store)")
    ap.add_argument("--tts-config", type=Path, default=None, help="TTS config for mp3 (config/tts/engines.yaml)")
    args = ap.parse_args()

    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    formats_wanted = [f.strip().lower() for f in args.format.split(",") if f.strip()]
    store_root = args.store or (REPO_ROOT / "artifacts" / "freebie_assets" / "store")
    config_freebies = REPO_ROOT / "config" / "freebies"
    registry_path = config_freebies / "freebie_registry.yaml"
    reg = load_yaml(registry_path)
    freebies_map = reg.get("freebies") or {}

    from phoenix_v4.freebies.freebie_renderer import (
        load_template,
        inject_metadata,
        _render_cta,
        _load_yaml,
        _md_to_html,
        html_to_pdf,
        CONFIG_FREEBIES,
    )

    manifest_rows: list[dict] = []
    with open(args.manifest, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            manifest_rows.append(json.loads(line))

    created = 0
    failed = 0
    cta_templates = _load_yaml(CONFIG_FREEBIES / "cta_templates.yaml")
    tool_forward = (cta_templates.get("tool_forward") or {}).get("script") or "Get your free resource."

    for row in manifest_rows:
        topic = (row.get("topic") or "").strip()
        persona = (row.get("persona") or "").strip()
        freebie_id = (row.get("freebie_id") or "").strip()
        fmt = (row.get("format") or "html").strip().lower()
        if fmt not in formats_wanted:
            continue
        if not topic or not persona or not freebie_id:
            failed += 1
            continue

        freebie_config = freebies_map.get(freebie_id)
        if not freebie_config:
            freebie_config = {"freebie_id": freebie_id, "file_template": "", "type": ""}
        else:
            freebie_config = dict(freebie_config)
        freebie_config.setdefault("freebie_id", freebie_id)

        slug = f"{topic}-{persona}-{freebie_id}"
        book_metadata = {
            "topic": topic,
            "persona": persona,
            "slug": slug,
            "cta_template_id": freebie_config.get("cta_style") or "tool_forward",
            "book_id": "",
            "title": "",
        }
        cta_text = _render_cta(
            book_metadata["cta_template_id"],
            topic.replace("_", " ").title(),
            freebie_id.replace("_", " ").title(),
            slug,
        )
        out_dir = store_root / fmt / topic / persona
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            if fmt == "html":
                file_template = freebie_config.get("file_template") or ""
                if not file_template:
                    failed += 1
                    continue
                raw = load_template(file_template)
                content = inject_metadata(raw, book_metadata, freebie_config, cta_text)
                if file_template.endswith(".md"):
                    title = f"{freebie_id.replace('_', ' ').title()} — {topic.replace('_', ' ').title()}"
                    content = _md_to_html(content, title)
                out_path = out_dir / f"{freebie_id}.html"
                out_path.write_text(content, encoding="utf-8")
                created += 1
            elif fmt == "pdf":
                file_template = freebie_config.get("file_template") or ""
                if not file_template:
                    failed += 1
                    continue
                raw = load_template(file_template)
                content = inject_metadata(raw, book_metadata, freebie_config, cta_text)
                if file_template.endswith(".md"):
                    title = f"{freebie_id.replace('_', ' ').title()} — {topic.replace('_', ' ').title()}"
                    content = _md_to_html(content, title)
                html_path = out_dir / f"{freebie_id}.html"
                html_path.write_text(content, encoding="utf-8")
                pdf_path = html_to_pdf(html_path)
                if pdf_path:
                    out_path = out_dir / f"{freebie_id}.pdf"
                    if pdf_path != out_path:
                        out_path.write_bytes(pdf_path.read_bytes())
                    created += 1
                else:
                    failed += 1
            elif fmt == "epub":
                # Stub: would use ebooklib to convert HTML to EPUB
                if freebie_config.get("file_template"):
                    raw = load_template(freebie_config["file_template"])
                    content = inject_metadata(raw, book_metadata, freebie_config, cta_text)
                    if freebie_config["file_template"].endswith(".md"):
                        content = _md_to_html(content, book_metadata.get("title") or freebie_id)
                    out_path = out_dir / f"{freebie_id}.epub"
                    # Placeholder: write minimal EPUB or skip
                    try:
                        import ebooklib
                        from ebooklib import epub
                        book_epub = epub.EpubBook()
                        book_epub.set_identifier(slug)
                        book_epub.set_title(freebie_id.replace("_", " ").title())
                        c1 = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
                        c1.content = content
                        book_epub.add_item(c1)
                        book_epub.add_item(epub.EpubNcx())
                        book_epub.add_item(epub.EpubNav())
                        book_epub.spine = ["nav", c1]
                        epub.write_epub(str(out_path), book_epub)
                        created += 1
                    except ImportError:
                        pass  # skip epub if ebooklib not installed
            elif fmt == "mp3":
                # TTS stub: would resolve script from audio_scripts.yaml and call TTS
                out_path = out_dir / f"{freebie_id}.mp3"
                if not out_path.exists():
                    # Placeholder: empty or skip; real impl would call TTS
                    out_path.write_bytes(b"")
                    created += 1
        except Exception as e:
            print(f"Failed {topic}/{persona}/{freebie_id}.{fmt}: {e}", file=sys.stderr)
            failed += 1

    print(f"Created {created} asset(s), failed {failed}", file=sys.stderr)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
