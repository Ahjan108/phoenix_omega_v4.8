# Pearl News — Publish to WordPress

Articles can be posted to the Pearl News WordPress site (BlogSite theme) via the **WordPress REST API** using Basic Auth with an Application Password.

## Credentials (environment variables only)

Set these in your environment or in a local `.env` file (do **not** commit `.env` or the app password):

| Variable | Description |
|----------|-------------|
| `WORDPRESS_SITE_URL` | Site base URL, e.g. `https://pearlnewsuna.org` (no trailing slash). |
| `WORDPRESS_USERNAME` | WordPress username for the application (e.g. the user that owns the Application Password). |
| `WORDPRESS_APP_PASSWORD` | Application password from **WP Admin → Users → Your Profile → Application Passwords**. Generate a new one; use the generated string (spaces are stripped automatically). |

**Security:** Never commit the app password. The repo already ignores `.env` and `.env.local`. See [docs/pearl_news_wordpress_env.example](../docs/pearl_news_wordpress_env.example) for placeholder variable names.

## Posting a story

From repo root:

```bash
# Post from article JSON (e.g. pipeline draft)
python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_001.json

# Save as draft (default)
python scripts/pearl_news_post_to_wp.py --article draft.json --status draft

# Publish immediately
python scripts/pearl_news_post_to_wp.py --article draft.json --status publish

# Inline title and content
python scripts/pearl_news_post_to_wp.py --title "Your Headline" --content "<p>Body HTML...</p>"

# Dry run (check env and payload only)
python scripts/pearl_news_post_to_wp.py --article draft.json --dry-run
```

## Article JSON format

When using `--article path/to/file.json`, the file may contain:

- **title** or **headline** — post title (required)
- **content**, **body**, or **text** — post body, HTML or plain (required)
- **slug** — optional URL slug
- **categories** or **category_ids** — list of WordPress category IDs
- **tags** or **tag_ids** — list of WordPress tag IDs
- **featured_image** — object for main/WordPress featured image with attribution: `{ "url": "https://...", "credit": "UN News", "source_url": "https://...", "caption": "optional" }`. The image is uploaded to the Media Library and set as the post thumbnail; credit/source are stored in the media caption.
- **featured_image_url** — alternative: image URL only (no attribution). Used if `featured_image` is not set.

At least one image per article is recommended (as WordPress featured image). When using feed-derived articles, use the first entry from the feed item’s `images` array (from `feed_ingest`) so attribution is preserved.

The script appends the Pearl News legal disclaimer to the content by default (see `legal_boundary.yaml`). Use `--no-disclaimer` to omit it.

## Scheduling and bulk

- Run the script from **cron**, **GitHub Actions**, or your pipeline after QC passes. See [docs/PEARL_NEWS_GITHUB_SCHEDULING.md](../docs/PEARL_NEWS_GITHUB_SCHEDULING.md) for running the pipeline on a schedule in GitHub (e.g. when your laptop is off).
- For staggered publishing (e.g. 5–10/day), run a job that selects QC-passed drafts and posts with `--status publish` on a schedule.
- Test with `--status draft` first; then publish from WP Admin or switch to `--status publish` when ready.

## Dependencies

- `requests` — install with `pip install requests`.
