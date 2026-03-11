# Pearl News — Publish to WordPress

Articles can be posted to the Pearl News WordPress site (BlogSite theme) via the **WordPress REST API** using Basic Auth with an Application Password.

## Credentials (env first, local file fallback)

Preferred: set these in your environment (or local `.env`, never committed):

| Variable | Description |
|----------|-------------|
| `WORDPRESS_SITE_URL` | Site base URL, e.g. `https://pearlnewsuna.org` (no trailing slash). |
| `WORDPRESS_USERNAME` | WordPress username for the application (e.g. `admin` for pearlnewsuna.org). |
| `WORDPRESS_APP_PASSWORD` | Application password from **WP Admin → Users → Your Profile → Application Passwords**. For this repo, the GitHub app password is in **docs/wordpress_github_info.rtf** (last row). Spaces are stripped automatically. |

Local fallback for dev machines:
- `WORDPRESS_CREDENTIALS_FILE=/absolute/path/to/wordpress_credentials.rtf`, or
- repo-root `wordpress_credentials.rtf` (auto-detected if env vars are missing).

Expected entries in that file:
- `WORDPRESS_SITE_URL=...`
- `WORDPRESS_USERNAME=...`
- `WORDPRESS_APP_PASSWORD=...`

**Security:** Never commit the app password. Keep `wordpress_credentials.rtf` local-only.

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
- **author** — WordPress user ID for byline. Current pipeline uses a fixed default author unless overridden at publish time.
- **categories** or **category_ids** — list of WordPress category IDs
- **tags** or **tag_ids** — list of WordPress tag IDs
- **featured_image** — object for main/WordPress featured image with attribution: `{ "url": "https://...", "credit": "UN News", "source_url": "https://...", "caption": "optional" }`. Uploaded to Media and set as post thumbnail.
- **featured_image_url** — image URL only (no attribution). Used if `featured_image` is not set.
- **featured_image_path** — path relative to repo root (e.g. `pearl_news/del_intake_pics/global_update.png`). Used when a local fallback image is attached in the article payload.

When the RSS article has no image, the pipeline may attach a local fallback image from **pearl_news/del_intake_pics/** or use the feed image if present. Placeholder assignment is now controlled in pipeline code rather than `site.yaml`.

The legal disclaimer is on the site About page; it is not appended to each article.

## Scheduling and bulk

- Run the script from **cron**, **GitHub Actions**, or your pipeline after QC passes. See [docs/PEARL_NEWS_GITHUB_SCHEDULING.md](../docs/PEARL_NEWS_GITHUB_SCHEDULING.md) for running the pipeline on a schedule in GitHub (e.g. when your laptop is off).
- For staggered publishing (e.g. 5–10/day), run a job that selects QC-passed drafts and posts with `--status publish` on a schedule.
- Test with `--status draft` first; then publish from WP Admin or switch to `--status publish` when ready.

## Dependencies

- `requests` — install with `pip install requests`.

## Troubleshooting (post not working)

1. **Credentials** — Run with `--dry-run` to confirm env vars are set:  
   `python scripts/pearl_news_post_to_wp.py --article path/to/article.json --dry-run`  
   You must set `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, and `WORDPRESS_APP_PASSWORD` (Application Password from WP, not your normal login password).

2. **REST API** — Ensure the site has the REST API enabled (default on WordPress). Test: open `https://yoursite.com/wp-json/wp/v2/posts` in a browser; you should see JSON (or an auth prompt).

3. **Application Password** — In WP Admin go to **Users → Profile → Application Passwords**, create a new app password, and use that exact string as `WORDPRESS_APP_PASSWORD`. Spaces in the value are OK (the script strips them).

4. **401 / 403** — Wrong username, wrong app password, or the user lacks permission to create posts. Confirm the user has Editor or Administrator role.

5. **Errors** — The script prints the WordPress API error code and message when a request fails; use that to fix config or permissions.
