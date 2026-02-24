# Pen-name author assets

**Authority:** Writer Spec §23.3, [docs/authoring/AUTHOR_ASSET_WORKBOOK.md](../docs/authoring/AUTHOR_ASSET_WORKBOOK.md).

When the pipeline runs with `--author <author_id>` (or author resolved from `config/brand_author_assignments.yaml`), it loads author assets from here or from the path in `config/author_registry.yaml` (`assets_path`).

## Directory layout

```
assets/authors/<author_id>/
  bio.yaml
  why_this_book.yaml
  authority_position.yaml
  audiobook_pre_intro.yaml
```

Each file must exist and meet the word ranges and content rules in the AUTHOR_ASSET_WORKBOOK. The pipeline fails (Writer Spec §23.9) if any required asset is missing when `author_id` is set.

## Template placeholders

Downstream templates (e.g. freebie HTML, audiobook scripts) can use:

- `{{author_pen_name}}`
- `{{author_bio}}`
- `{{author_why_this_book}}`
- `{{author_audiobook_pre_intro}}` (all pre-intro blocks joined)

Rendered pre-intro text in Writer Spec §23.4 order is available via:

```python
from phoenix_v4.planning.author_asset_loader import render_audiobook_pre_intro
text = render_audiobook_pre_intro(author_assets, book_title="...", series_name="...", include_series_line=True)
```
