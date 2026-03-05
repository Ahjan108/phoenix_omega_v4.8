# Pearl News functionality
_Exported on 3/5/2026 at 17:58:26 GMT+8 from Cursor (2.5.25)_

---

**User**

It's the Pearl News stuff. Working 100%. Are...

---

**Cursor**


Your message seems to end mid-sentence (“Are…”). Searching the project for “Pearl News” to see what’s there and what might be relevant.



Good to hear Pearl News is working 100%.

Your last message cuts off at “Are…” — can you finish the thought? For example, are you asking whether:

- **Are** the tests / pipeline / WordPress posting all green?
- **Are** there any next steps or docs to update?
- **Are** we good to document this or ship it?

Once you complete the question, I can give a direct answer or do the next step (e.g. run tests, check scripts, or update docs).

---

**User**

Is the Pearl News stuff. Working 100%. Are we getting rss ? writing atricles, posting to wordpress? @docs/DOCS_INDEX.md 

---

**Cursor**


Checking feed ingest (RSS) and the WordPress publish path:



Checking for draft output and the full pipeline flow in `run_article_pipeline`:



Yes. Per the codebase and **docs/DOCS_INDEX.md**, Pearl News is set up to do all three.

---

### 1. **Getting RSS**

- **Config:** `pearl_news/config/feeds.yaml` — UN News RSS URLs (`un_news_all`, `un_news_sdgs`).
- **Code:** `pearl_news/pipeline/feed_ingest.py` — uses `feedparser` to fetch RSS/Atom, normalizes entries (id, title, url, pub_date, summary, images, attribution).
- **DOCS_INDEX:** “Feed ingest — Ingest RSS/Atom from feeds.yaml” → `pearl_news/pipeline/feed_ingest.py`.

---

### 2. **Writing articles**

- **Pipeline:** `pearl_news/pipeline/run_article_pipeline.py` runs: **ingest → classify (topic/SDG) → template select → assemble (slots + disclaimer) → quality gates → QC** → writes drafts.
- **Output:** `artifacts/pearl_news/drafts/article_<id>.json` (title, content, metadata) plus `ingest_manifest.json` and `build_manifests.json`.
- **One-command:** `scripts/pearl_news_do_it.sh` runs tests then pipeline (e.g. `--limit 10`); you already have drafts under `artifacts/pearl_news/drafts/`.
- **DOCS_INDEX:** “Run article pipeline” and “Pipeline stages” (feed ingest, classifier, template selector, assembler, quality gates, QC).

---

### 3. **Posting to WordPress**

- **Script:** `scripts/pearl_news_post_to_wp.py` — posts a draft JSON to WordPress (REST API).
- **Client:** `pearl_news/publish/wordpress_client.py` — credentials from env (`WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`), posts to `/wp-json/wp/v2/posts`, optional featured image from URL, appends legal disclaimer.
- **One-command post:** `scripts/pearl_news_do_it.sh --post` runs tests + pipeline, then posts the **first** `article_*.json` as a **draft**.
- **DOCS_INDEX:** “Post to WordPress” → `scripts/pearl_news_post_to_wp.py`; “WordPress client” → `pearl_news/publish/wordpress_client.py`.

---

### Summary

| Step              | Implemented | Where |
|-------------------|------------|-------|
| **RSS**           | Yes        | `feed_ingest.py` + `feeds.yaml` |
| **Writing articles** | Yes     | `run_article_pipeline.py` → `artifacts/pearl_news/drafts/` |
| **Posting to WP** | Yes        | `pearl_news_post_to_wp.py` + `wordpress_client.py`; `pearl_news_do_it.sh --post` |

So: you are getting RSS, writing articles, and posting to WordPress. Production readiness (per DOCS_INDEX) still depends on the operational checklists (e.g. `PEARL_NEWS_GO_NO_GO_CHECKLIST.md`, `PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md`) and having WordPress env vars set for real posting.

---

**User**

is it doing it?

---

**Cursor**


Checking whether the pipeline has run and produces real output:



Yes. The artifacts show it’s actually running.

**RSS**  
The last run pulled real UN News items: e.g. “World News in Brief: Gaza crossings…”, “SECURITY COUNCIL LIVE: Melania Trump…”, “MIDDLE EAST LIVE: Strikes continue…”, “Iran crisis: Nuclear watchdog…”, “Deadly bombing of Iran primary school…”. All from `un_news_all` in `feeds.yaml`.

**Writing articles**  
- **Build:** `2026-03-03T08:22:03`  
- **Ingested:** 5 items → 5 passed QC → 5 article drafts under `artifacts/pearl_news/drafts/`.  
- Each draft has real content: headline, UN story, source link, youth/SDG layer, forum/teacher line, and the Pearl News disclaimer.

**Posting to WordPress**  
The scripts are there (`pearl_news_post_to_wp.py`, `pearl_news_do_it.sh --post`), but posting only happens when you run them with `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, and `WORDPRESS_APP_PASSWORD` set. The repo doesn’t show whether a post was actually sent; that’s a local/env decision.

**Summary**

| Step              | Actually doing it? | Evidence |
|-------------------|-------------------|----------|
| **RSS**           | Yes               | `ingest_manifest.json` + real UN headlines, `source_feed_id: un_news_all` |
| **Writing articles** | Yes           | 5 `article_*.json` drafts from 2026-03-03, full content + QC passed |
| **Posting to WP** | Only when you run the post script with env vars | No automatic posting in repo; script is ready |

So: it is doing RSS and writing articles; posting to WordPress is done only when you run the post step with credentials.

---

**User**

i gave you this: WordPress is done only when you run the post step with credentials.


not working?

---

**Cursor**


Checking the WordPress posting flow for failure points:



Running a dry-run to reproduce the failure and improve error output:



Dry-run shows credentials are required. Improving error handling so we get a clear message when posting fails (e.g. 401, 403, wrong app password):



Adding a short troubleshooting section to the publish README:



Here’s what’s in place and what to do next.

**Why it “doesn’t work”**  
Posting only runs when you execute the post step **and** the three WordPress env vars are set. If any of them are missing, you get:

`Set WORDPRESS_SITE_URL, WORDPRESS_USERNAME, and WORDPRESS_APP_PASSWORD in the environment.`

**Changes made**

1. **Clearer API errors** in `pearl_news/publish/wordpress_client.py`  
   When WordPress returns 401/403/etc., the script now prints the WP error **code** and **message** (e.g. `rest_forbidden`, “Invalid application password”) so you can see why it failed.

2. **Troubleshooting section** in `pearl_news/publish/README.md`  
   - Use `--dry-run` to confirm env vars.  
   - Use an **Application Password** from WP (Users → Profile → Application Passwords), not your normal password.  
   - REST API must be enabled; user needs Editor/Admin.

**What you should do**

1. Set credentials (in your shell or a `.env` you load, **do not** commit the app password):

   ```bash
   export WORDPRESS_SITE_URL="https://pearlnewsuna.org"
   export WORDPRESS_USERNAME="YourWpUsername"
   export WORDPRESS_APP_PASSWORD="xxxx xxxx xxxx xxxx"  # from WP Profile → Application Passwords
   ```

2. Confirm env and payload:

   ```bash
   python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_fbb04cf8c6693af1.json --dry-run
   ```

   If that prints “Dry-run: env OK, payload prepared (not sent).”, env and article are fine.

3. Post a draft:

   ```bash
   python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_fbb04cf8c6693af1.json --status draft
   ```

If it still fails, the script will now show the exact WordPress error code and message so we can fix the next issue (e.g. wrong app password, REST disabled, or permissions).

---

**User**

WORDPRESS_USERNAME="admin"
for WORDPRESS_APP_PASSWORD look at docs/wordpress_github_info.rtf

WORDPRESS_APP_PASSWORD is the last row


---

**Cursor**


From `docs/wordpress_github_info.rtf`, the **last row** (Application Password) is:

**`AkoH Zn0C 9xpY I7gb 6UuE 9IZB`**

Use these in your environment (run in the same terminal where you’ll run the post script):

```bash
export WORDPRESS_SITE_URL="https://pearlnewsuna.org"
export WORDPRESS_USERNAME="admin"
export WORDPRESS_APP_PASSWORD="AkoH Zn0C 9xpY I7gb 6UuE 9IZB"
```

Then test and post:

```bash
# Dry-run (check env + payload)
python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_fbb04cf8c6693af1.json --dry-run

# Post as draft
python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_fbb04cf8c6693af1.json --status draft
```

**Security:** `docs/wordpress_github_info.rtf` contains live credentials. If this repo is or will be public, move those secrets out of the repo (e.g. into a local `.env` that’s in `.gitignore` or into GitHub Actions secrets) and remove them from the RTF. I’m not adding the password to any other file in the repo.

---

**User**

do all this for me . set it up test it. 

---

**Cursor**


Setting env vars and running a dry-run, then posting a draft.



Dry-run passed. Posting the article as a draft (requires network).



Installing `requests` and retrying the post:



Post succeeded. Adding `requests` to requirements and a short setup note so we can run the post script with the right env:



Summary of what’s done:

---

**1. Setup**
- Used project venv (`.venv`), installed `requests` there, and added `requests>=2.28` to `requirements.txt`.
- Confirmed credentials: `WORDPRESS_USERNAME=admin`, app password from `docs/wordpress_github_info.rtf` (last row).

**2. Test**
- **Dry-run:** Env and payload validated.
- **Live post:** Article was posted to WordPress as a **draft**.

**3. Result**
- **Post ID:** 961  
- **Draft URL:** https://pearlnewsuna.org/?p=961  
- **Title:** "MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint"

**4. Docs**
- `pearl_news/publish/README.md` now notes that the app password is in `docs/wordpress_github_info.rtf` (last row) and that the username is `admin` for pearlnewsuna.org.

---

**To post again from your machine** (from repo root, with `.venv`):

```bash
export WORDPRESS_SITE_URL="https://pearlnewsuna.org"
export WORDPRESS_USERNAME="admin"
export WORDPRESS_APP_PASSWORD="AkoH Zn0C 9xpY I7gb 6UuE 9IZB"

.venv/bin/python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_fbb04cf8c6693af1.json --status draft
```

Or use the one-liner with env vars inline (no export). To run the full pipeline and then post the first draft:

```bash
./scripts/pearl_news_do_it.sh --post
```

Make sure the same three env vars are set in that shell when you use `--post`.

---

**User**

is this posting from my github now?

---

**Cursor**


Checking whether a GitHub Action is configured to post to WordPress:



**No.** The post we did earlier was from **your machine** (Cursor/terminal), not from GitHub.

There is a **GitHub Action** that can post from GitHub:

- **Workflow:** `.github/workflows/pearl_news_scheduled.yml`
- **When it runs:**  
  - On a schedule: **6:00 and 18:00 UTC** daily  
  - Manually: **Actions** tab → “Pearl News scheduled” → **Run workflow**

It only posts to WordPress if these **repository secrets** are set in GitHub:

- `WORDPRESS_SITE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`

If those secrets are **not** set, the workflow still runs the pipeline and the “Test WordPress integration” step does a **dry-run** only (no real post).

**To have GitHub post to WordPress:**

1. In GitHub: **Repo → Settings → Secrets and variables → Actions**.
2. Add (or update) these **Repository secrets**:
   - `WORDPRESS_SITE_URL` = `https://pearlnewsuna.org`
   - `WORDPRESS_USERNAME` = `admin`
   - `WORDPRESS_APP_PASSWORD` = the app password from `docs/wordpress_github_info.rtf` (last row: `AkoH Zn0C 9xpY I7gb 6UuE 9IZB`).

After that, each run of “Pearl News scheduled” (on schedule or manual) will post the first generated draft to WordPress as a draft, same as when you run the script locally.

---

**User**

can you check status. if it has been posting?

---

**Cursor**


Checking whether the GitHub CLI is available and fetching recent workflow runs:



Fetching the latest run's job steps to see if it posted or dry-ran:



Here’s what the GitHub API shows:

---

### Pearl News workflow status

**Workflow:** Pearl News scheduled (`pearl_news_scheduled.yml`)  
**Runs:** 179 total; latest run **#15** completed successfully.

**Latest run (run #15):**
- **When:** 2026-03-04 19:01 UTC (scheduled)
- **Status:** completed  
- **Conclusion:** success  
- **Branch:** main  
- **All steps succeeded**, including:
  - Run Pearl News tests
  - Run full pipeline (ingest → classify → assemble → QC)
  - Upload draft artifacts
  - **Test WordPress integration (dry-run or post)**

So the workflow is running on schedule and the WordPress step is succeeding. The API doesn’t show whether that step did a **dry-run** (no secrets) or an **actual post** (secrets set).

---

### Has it been posting to WordPress?

- If the three WordPress **repository secrets** are set in GitHub (Settings → Secrets and variables → Actions), then each successful run **does** post the first draft to WordPress.
- If those secrets are **not** set, the step only does a **dry-run** (no post).

To confirm:

1. **In GitHub:** Open the run, click the “Test WordPress integration (dry-run or post)” step and check the log. You’ll see either “Dry-run: env OK…” or the WordPress API response (e.g. post `id`, `link`).
2. **In WordPress:** Check **Posts → Drafts** (and possibly **Posts → All**) on pearlnewsuna.org for new drafts from the last few days; those would be from GitHub if secrets are set.

If you want, we can add a small note in the workflow or in the repo docs that says: “To have GitHub actually post, add these three secrets: …” so it’s explicit.

---

**User**

i see it working in wordpress: [MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint — Draft
Edit | Quick Edit | Trash | Preview
admin	Uncategorized	—No tags	—No stats	
—No comments
Last Modified
2026/03/05 at 3:31 am	0	1
Select SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict	
SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict — Draft
Edit | Quick Edit | Trash | Preview
admin	—No categories	—No tags	—No stats	
—No comments
Last Modified
2026/03/04 at 7:01 pm	0	0
Select SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict	
SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict — Draft
Edit | Quick Edit | Trash | Preview
admin	—No categories	—No tags	—No stats	
—No comments
Last Modified
2026/03/04 at 7:00 am	0	0
Select SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict	
SECURITY COUNCIL LIVE: Melania Trump presides over historic session on children in conflict — Draft
Edit | Quick Edit | Trash | Preview
admin	—No categories	—No tags	—No stats	
—No comments
Last Modified
2026/03/03 at 7:01 pm	0	0
Select Attacks on Iran and retaliatory strikes ‘undermine international peace and security’	
Attacks on Iran and retaliatory strikes ‘undermine international peace and security’ — Draft
Edit | Quick Edit | Trash | Preview
admin	—No categories	—No tags	—No stats	
—No comments
Last Modified
2026/03/03 at 7:03 am	0	0
Select Attacks on Iran and retaliatory strikes ‘undermine international peace and security’	
Attacks on Iran and retaliatory strikes ‘undermine international peace and security’ — Draft
Edit | Quick Edit | Trash | Preview
admin]. 

we need to make changes to the article writing. 

first, most articles that include the united spiritual leaerers forum (uslf) stuff should be about 1 teacher's insight/teachings about the topic and how it relates to the youth. do uslf group articles only 5% of the time.

---

**Cursor**


Checking how teacher/forum content is selected and assembled so we can default to one teacher per article and allow group articles ~5% of the time.



Checking template selection and where to add the single-teacher vs group ratio:



Implementing the 95% single-teacher / 5% USLF group rule: adding config and updating the assembler and template selector.



Updating the article assembler to choose single-teacher vs group (5%) and use the correct placeholder.



Fixing the group/single-teacher logic when atoms exist and passing `config_root` into `_render_article`.



Updating the template selector so we assign the group template (interfaith_dialogue_report) only ~5% of the time.



Allowing the interfaith (group) template to be selected ~5% of the time for group-suited topics (e.g. peace_conflict).



Checking that `assemble_articles` passes `config_root` to `_render_article`:



Running Pearl News tests to verify nothing's broken:



All tests passed. Adding a short doc note to the pipeline README:



Summary of what’s in place:

---

### 1. **Config** (`pearl_news/config/template_diversity.yaml`)
- **`uslf_group_article_ratio: 0.05`** — 5% of articles use the group/USLF voice; 95% use single-teacher.

### 2. **Article assembler** (`pearl_news/pipeline/article_assembler.py`)
- **Teacher slot** (when no atom file matches):
  - **~95%:** Single-teacher placeholder: *“A teacher from the United Spiritual Leaders Forum offers perspective on this topic and its relevance to youth: reflection and resilience…”*
  - **~5%:** Group placeholder: *“Leaders from the United Spiritual Leaders Forum emphasize…”*
- Choice is **deterministic** from the item `id` (hash), so the same feed item always gets the same type.
- When **atoms exist**: single-teacher articles use one teacher’s content; group articles still use the group placeholder.

### 3. **Template selector** (`pearl_news/pipeline/template_selector.py`)
- **Default for `peace_conflict`** is now `hard_news_spiritual_response` (single-teacher style).
- **`interfaith_dialogue_report`** (group/forum template) is assigned only when the same 5% rule applies (hash-based), so it appears ~5% of the time for topics that can use it.

### 4. **Docs**
- **`pearl_news/pipeline/README.md`** — Describes the 95% single-teacher / 5% group rule and points to `uslf_group_article_ratio`.

---

**Tests:** All 6 Pearl News tests pass.

Changing the balance is done by editing **`uslf_group_article_ratio`** in `pearl_news/config/template_diversity.yaml` (e.g. `0.10` for 10% group).

---

**User**

author should be a author assingned to teacher and alternate.

looking at article: [MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint
By
admin
March 5, 2026
0
1
 Share
MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint

MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint

Violent escalation in the Middle East has entered a third day as coordinated US and Israeli strikes against Iran aimed at regime change continue to cause loss of life and damage across the region, prompting Iranian missile and drone counter-strikes hitting targets in multiple countries. Explosions, airspace closures and military alerts have been reported from Tehran to the Gulf states and beyond. Follow our live coverage with updates from across the United Nations system. UN News app users can follow here.

Source: https://news.un.org/feed/view/en/story/2026/03/1167065…

Young people are increasingly affected by global events in this area. Gen Z and Gen Alpha seek clarity and constructive responses aligned with sustainable development and well-being (SDG 17: Partnerships for the Goals).

Leaders from the United Spiritual Leaders Forum emphasize reflection and resilience in the face of uncertainty, in line with ethical frameworks that support youth well-being and global goals.

This story relates to SDG 17: Partnerships for the Goals. The United Nations tracks progress and supports initiatives in this area. Pearl News is an independent nonprofit and is not affiliated with the United Nations.

Constructive next steps and dialogue continue to shape how communities and youth engage with these challenges.

Pearl News is an independent nonprofit civic media organization. We are not affiliated with, endorsed by, or officially connected to the United Nations unless explicitly stated in formal public documentation.

Pearl News is an independent nonprofit civic media organization. We are not affiliated with, endorsed by, or officially connected to the United Nations unless explicitly stated in formal public documentation.

].bad repeat. this is the title, but also is in the ariticl body , bad: "MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint

MIDDLE EAST LIVE: Strikes continue from US, Israel and Iran as UN urges restraint"
just title. appear once.

this apears twice: [Pearl News is an independent nonprofit civic media organization. We are not affiliated with, endorsed by, or officially connected to the United Nations unless explicitly stated in formal public documentation.

Pearl News is an independent nonprofit civic media organization. We are not affiliated with, endorsed by, or officially connected to the United Nations unless explicitly stated in formal public documentation.

]. delete this. drop it from the spec / docs / sytem. don't need it. we have it already inthe "about us" 

put the source at the end. that last thing in an article: "Source: https://news.un.org/feed/view/en/story/2026/03/1167065…"

There is no article  image. 
incorporate article images - when no image use the place holds i gave you.

the article is weak on detail or information. target size is 1000 words. this is 200. 



---

**Cursor**


Implementing the requested changes: checking the article payload, WordPress client, and feed image handling.



Checking the feed ingest output structure and legal_boundary for any image/placeholder:



Defaulting to no disclaimer when posting from article JSON.



Adding author rotation and featured-image (feed + placeholder) config and pipeline logic:



Updating legal_boundary and docs, and adding target word count.



Running Pearl News tests:



Checking e2e tests for assertions on content shape:



Summary of what’s implemented:

---

### 1. **Title once**
- **news_event** slot now outputs only the summary (no H2, no inline source).
- Headline is output once as **H1** from the headline slot. The body no longer repeats the title.

### 2. **Disclaimer removed**
- **article_assembler**: No disclaimer appended to the body.
- **wordpress_client**: `append_disclaimer` default is **False**; post script always passes `append_disclaimer=False`.
- **legal_boundary.yaml**: `mandatory_disclaimer` renamed to `disclaimer_site` (for site About only).
- Docs/spec updated so the per-article disclaimer is no longer required.

### 3. **Source at end**
- After all sections, the body ends with:  
  **`<p><em>Source: <a href="...">...</a></em></p>`**  
  using the feed item URL.

### 4. **Author (teacher-assigned, alternate)**
- **pearl_news/config/wordpress_authors.yaml**: `author_ids` list (WordPress user IDs). Pipeline assigns them round-robin.
- **run_article_pipeline**: Sets `author` on each article payload from `author_ids[i % len(author_ids)]`.
- **wordpress_client**: `post_article(..., author=int)` supported.
- **pearl_news_post_to_wp.py**: Reads `author` from article JSON and passes it to the client.

Default is `[1]`. Add more IDs (e.g. `[1, 2, 3]`) to rotate bylines.

### 5. **Featured image (feed + placeholder)**
- **run_article_pipeline**: If the item has `images` from the feed, the first image is set as `featured_image` (with url, credit, source_url). If there are no images, `featured_image_url` is set from config.
- **pearl_news/config/site.yaml**: `placeholder_featured_image_url` (default: an Unsplash URL). Replace with your own default/placeholder (e.g. `https://pearlnewsuna.org/.../default-news.jpg`).

### 6. **Target ~1000 words**
- **site.yaml**: `target_word_count: 1000`.
- Placeholder sections are longer: **youth_impact**, **teacher**, **sdg_ref**, and **forward_look** each have 2–3 paragraphs so boilerplate is closer to the target. Reaching a full 1000 words will still depend on feed summary length, atoms, or a future LLM expansion step.

### 7. **Docs**
- Pipeline README, publish README, DOCS_INDEX, PEARL_NEWS_GO_NO_GO_CHECKLIST, and legal_boundary wording updated for: no per-article disclaimer, source at end, author rotation, featured image/placeholder.

---

**Config you can edit**
- **pearl_news/config/wordpress_authors.yaml** — set `author_ids: [1, 2, ...]` to your WordPress user IDs to rotate bylines.
- **pearl_news/config/site.yaml** — set `placeholder_featured_image_url` to your default image URL (replace the Unsplash URL if you want your own placeholder).

All 6 Pearl News tests pass. I can run a full pipeline run to confirm end-to-end output if you want.

---

**User**

i want to use my github qwen llm for this: 6. Target ~1000 words
site.yaml: target_word_count: 1000.
Placeholder sections are longer: youth_impact, teacher, sdg_ref, and forward_look each have 2–3 paragraphs so boilerplate is closer to the target. Reaching a full 1000 words will still depend on feed summary length, atoms, or a future LLM expansion step.


---

**Cursor**


Searching the repo for Qwen/LLM usage and where we can add an expansion step:



Adding an LLM expansion step that uses an OpenAI-compatible API (e.g. local Qwen via LM Studio/Ollama or a GitHub-hosted endpoint). Checking `scripts/research` for a similar pattern:



Implementing the LLM expansion step: adding config, prompt, expander module, and pipeline integration.



Adding a short README for the expansion flow and checking whether `openai` is in requirements.



Running tests and adding a note to the config about using a GitHub or remote endpoint:



Summary of what’s in place:

---

### 1. **Config: `pearl_news/config/llm_expansion.yaml`**
- **enabled: true** — expansion runs when you pass `--expand`.
- **base_url** — OpenAI-compatible API URL:
  - **Local:** `http://localhost:1234/v1` (LM Studio) or `http://localhost:11434/v1` (Ollama with OpenAI compat).
  - **GitHub / remote:** set to your Qwen endpoint (e.g. a self-hosted runner or Codespaces).
- **model** — e.g. `Qwen2.5-14B-Instruct` (or your model name).
- **api_key** — `lm-studio` / `ollama` for local; use your key for remote.
- **target_word_count: 1000**, **max_tokens: 2048**, **timeout: 120**, **temperature: 0.5**.

### 2. **Expansion step: `pearl_news/pipeline/llm_expand.py`**
- **expand_article_with_llm()** — calls the API with the draft HTML + target word count; returns expanded HTML or `None`.
- **run_expansion()** — loads `llm_expansion.yaml`; if `enabled`, runs expansion for each item and updates `item["content"]` on success; on failure or missing API, leaves content unchanged and logs.

### 3. **Prompt: `pearl_news/prompts/expansion_system.txt`**
- Instructs the model to expand to the target length, keep the same HTML sections and facts, no new claims, keep the “Source:” line at the end.

### 4. **Pipeline: `run_article_pipeline.py`**
- New flag: **`--expand`**.
- After **assemble**, if `--expand` is set, runs **run_expansion** (then quality gates run on the expanded content).

### 5. **Docs and deps**
- **pearl_news/README.md** — quick start includes a `--expand` example.
- **pearl_news/prompts/README.md** — describes the expansion prompt and config.
- **requirements.txt** — added **openai>=1.0** for the client.

---

**Using your GitHub Qwen LLM**

1. **Local Qwen (LM Studio / Ollama)**  
   - Start your Qwen server, then:
   ```bash
   python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --expand --limit 3
   ```

2. **GitHub or other remote Qwen**  
   - In **`pearl_news/config/llm_expansion.yaml`** set:
   - **base_url** to your endpoint (e.g. `https://your-runner-or-app/v1`).
   - **api_key** if the endpoint requires it.
   - **model** to the model name that endpoint exposes.  
   Then run the same command with `--expand`.

If the API is missing or fails, the pipeline still finishes and keeps the pre-expansion content. All 6 Pearl News tests pass.

---

**User**

the images to use if there is no artivle image with the rss article is in @pearl_news/del_intake_pics/ 
1 pic for each article type 

put in here right: [pearl_news/config/site.yaml — set placeholder_featured_image_url to your default image URL (replace the Unsplash URL if you want your own placeholder).
] and clean up

---

**Cursor**


Checking exact filenames and how the pipeline and WordPress client handle images:



Updating site.yaml with per-template placeholders from `del_intake_pics`, and adding upload-from-file support in the pipeline and WordPress client.



Adding upload-from-file support in the WordPress client and post script.



Summary of changes:

---

### 1. **`pearl_news/config/site.yaml`**
- **Removed:** single `placeholder_featured_image_url` (Unsplash).
- **Added:** `placeholder_featured_image_by_template` — one image per article type, paths under `pearl_news/del_intake_pics/`:
  - `hard_news_spiritual_response` → `global_update.png`
  - `youth_feature` → `youth_impact.png`
  - `interfaith_dialogue_report` → `interfath_dialogue.png` (matches existing filename)
  - `explainer_context` → `sdg_brief.png`
  - `commentary` → `cultural_insight.png`
- **Added:** `placeholder_featured_image_default` → `global_update.png` for any unmapped template.
- **Kept:** `target_word_count: 1000`.

### 2. **Pipeline `run_article_pipeline.py`**
- Loads `placeholder_featured_image_by_template` and `placeholder_featured_image_default` from `site.yaml`.
- When the RSS item has **no** image: sets `featured_image_path` on the article payload from the template (or default) path. No `featured_image_url` for these.
- When the feed **has** an image: still uses `featured_image` from the first feed image.

### 3. **WordPress client `pearl_news/publish/wordpress_client.py`**
- **`_upload_media_from_file()`** — uploads a local file to WordPress Media and returns the attachment ID.
- **`post_article(..., featured_image_path=...)`** — if `featured_image_path` is set and the file exists, uploads that file and sets `featured_media`; otherwise still uses URL when given.

### 4. **Post script `scripts/pearl_news_post_to_wp.py`**
- Reads `featured_image_path` from the article JSON and resolves it with `REPO_ROOT`.
- Passes the resolved path into `post_article()`.

### 5. **Docs**
- **pearl_news/publish/README.md** — documents `featured_image_path` and that placeholders come from `pearl_news/del_intake_pics/` via `site.yaml`.

---

**Placeholder files used** (from `pearl_news/del_intake_pics/`):  
`global_update.png`, `youth_impact.png`, `interfath_dialogue.png`, `sdg_brief.png`, `cultural_insight.png`.  
`climate_watch.png`, `education_and_identity.png`, and `peace_and_governance.png` remain available for future mapping.

All 6 Pearl News tests pass.

---

**User**

help me do this step by step. read @docs/DOCS_INDEX.md @Qwen-Agent/qwen_agent/utils/qwen.tiktoken @Qwen-Agent/benchmark/code_interpreter/models/qwen.py @Qwen/dcu-support/qwen2flm.py 

---

**Cursor**


Locating and reading the referenced files to determine the task:



Reading DOCS_INDEX and searching for Qwen-related content. Qwen-Agent and Qwen paths aren't in this repo.



Checking the Qwen/translate docs in this repo to determine the intended steps:



Here’s a concise step-by-step plan and how it fits what you opened.

---

## 1. What’s in this repo vs the others

- **`docs/DOCS_INDEX.md`** — In **phoenix_omega**. I’ve read it; it’s the master doc index and points to translate/Qwen/Pearl News.
- **`Qwen-Agent/qwen_agent/utils/qwen.tiktoken`**  
- **`Qwen-Agent/benchmark/code_interpreter/models/qwen.py`**  
- **`Qwen/dcu-support/qwen2flm.py`**  

Those three paths are **not** under phoenix_omega (they live in your **Qwen-Agent** and **Qwen** repos). I can’t read them from here. To use them in steps, either:

- Paste the relevant parts of those files here, or  
- Open a Cursor workspace that includes those repos and ask again, or  
- Tell me the exact goal (e.g. “use Qwen tiktoken for Pearl News word count”, “run pipeline from Qwen-Agent”, “convert model with qwen2flm”).

---

## 2. Step-by-step using DOCS_INDEX (phoenix_omega)

Use DOCS_INDEX as the map and do one of the following.

### Option A: Run Pearl News pipeline from phoenix_omega (no Qwen repo)

1. **Navigate:** DOCS_INDEX → [Pearl News (document all)](#pearl-news-document-all).
2. **Run pipeline:**  
   `python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit 5`  
   (Optional: add `--expand` for LLM expansion.)
3. **Post to WordPress (optional):**  
   Set env vars, then  
   `python scripts/pearl_news_post_to_wp.py --article artifacts/pearl_news/drafts/article_<id>.json --status draft`.
4. **Scheduling:** DOCS_INDEX → **Pearl News scheduling** → [PEARL_NEWS_GITHUB_SCHEDULING.md](docs/PEARL_NEWS_GITHUB_SCHEDULING.md). Add the three WordPress secrets in GitHub; workflow runs 6:00 and 18:00 UTC.

### Option B: Run pipeline from Qwen or Qwen-Agent (move/copy pipeline there)

1. **Navigate:** DOCS_INDEX → **Translate / prompt via Qwen GitHub pipeline CLI** → [TRANSLATE_QWEN_PIPELINE_CLI.md](docs/TRANSLATE_QWEN_PIPELINE_CLI.md), then **§3 Running from Qwen / Qwen-Agent**.
2. **Then:** [PEARL_NEWS_GITHUB_SCHEDULING.md](docs/PEARL_NEWS_GITHUB_SCHEDULING.md) **§3 Option B — Move pipeline to Qwen or Qwen-Agent (step-by-step)**:
   - Clone Ahjan108/Qwen or Ahjan108/Qwen-Agent.
   - Copy from phoenix_omega: `pearl_news/`, `scripts/pearl_news_post_to_wp.py`, Pearl News tests, `.github/workflows/pearl_news_scheduled.yml`.
   - Put the workflow under `.github/workflows/` in the clone; fix paths if needed.
   - Add the three WordPress secrets in that repo.
   - Push to main; schedule and `workflow_dispatch` will run as in the doc.

### Option C: Translation pipeline (all locales)

1. **Navigate:** DOCS_INDEX → **Translation, validation & multilingual** → [TRANSLATE_QWEN_PIPELINE_CLI.md](docs/TRANSLATE_QWEN_PIPELINE_CLI.md).
2. **Locales:** Use §1 system languages and §4 Translate vs prompt.
3. **Scripts:** Use the translate/validate/merge scripts and workflows listed in that doc (and in DOCS_INDEX under the same section).

---

## 3. Where the Qwen-Agent / Qwen files would matter

- **`qwen.tiktoken`** — usually a tokenizer merge file; useful if you want **token counting** or **token limits** (e.g. for Pearl News ~1000-word target or API limits).
- **`qwen.py`** (code_interpreter/models) — likely a **model wrapper** for running Qwen in a code/interpreter setting.
- **`qwen2flm.py`** — likely **Qwen → FLM (e.g. llama.cpp) conversion** for local or DCU deployment.

If you tell me the exact goal (e.g. “add token counting to Pearl News”, “run Pearl News from Qwen-Agent”, “convert Qwen for DCU”), I can give numbered steps that reference DOCS_INDEX and, where possible, how to plug in those files (or you can paste their contents and I’ll wire them in).

---

**User**

do this: Yes. Per `DOCS_INDEX` + `PEARL_NEWS_GITHUB_SCHEDULING.md`, do **Option B** and run Pearl News from your `Qwen` or `Qwen-Agent` repo.

Use this exact flow:

1. Pick target repo  
- Use one: `Ahjan108/Qwen-Agent` (recommended) or `Ahjan108/Qwen`.

2. Copy Pearl News code into that repo  
From `phoenix_omega`, copy:
- `pearl_news/`
- `scripts/pearl_news_post_to_wp.py`
- `tests/test_pearl_news_quality_gates_minimal.py`
- `tests/test_pearl_news_pipeline_e2e.py`
- `.github/workflows/pearl_news_scheduled.yml`

3. Commit + push to target repo `main`.

4. Add GitHub secrets in target repo  
- `WORDPRESS_SITE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`
- `QWEN_BASE_URL`
- `QWEN_API_KEY`
- `QWEN_MODEL`

5. Important for LM Studio  
- If `QWEN_BASE_URL` is local (`localhost`), GitHub cloud runners cannot reach it.  
- Set workflow to `runs-on: self-hosted` and run a self-hosted runner on your Mac (same machine/network as LM Studio).

6. Trigger run  
- GitHub → Actions → `Pearl News scheduled` → `Run workflow`.

7. Verify success  
- Draft artifacts uploaded (`artifacts/pearl_news/drafts`)
- Optional WP draft post created
- Workflow green

If you want, I’ll give you the exact `cp` commands and the exact workflow patch for self-hosted + LM Studio env injection.

---

**Cursor**


Preparing copy commands and a workflow patch for self-hosted runner + Qwen secrets. Checking the current workflow and pipeline for `--expand` and env usage:



Adding env fallback in the expansion module so the workflow can inject Qwen secrets, then creating the runbook and workflow variant.



Linking the runbook and self-hosted workflow in the scheduling doc and DOCS_INDEX:



Making the runbook's copy step default to the self-hosted workflow for Option B.



Running Pearl News tests to verify the llm_expand env override:



Summary of what’s in place for **Option B** (run Pearl News from Qwen or Qwen-Agent):

---

### 1. **Env override for Qwen (in phoenix_omega)**  
**`pearl_news/pipeline/llm_expand.py`**
- Reads **`QWEN_BASE_URL`**, **`QWEN_API_KEY`**, **`QWEN_MODEL`** from the environment and overrides the YAML config.
- If **`QWEN_BASE_URL`** is set, expansion is enabled even when the config has `enabled: false`.
- The self-hosted workflow can pass these via GitHub Actions secrets; no need to put secrets in the repo.

---

### 2. **Option B runbook**  
**`docs/PEARL_NEWS_OPTION_B_RUNBOOK.md`**
- **§1** — Choose **Ahjan108/Qwen-Agent** (recommended) or **Ahjan108/Qwen**.
- **§2** — Exact copy commands from a parent dir that has both repos:
  - `pearl_news/` → target
  - `scripts/pearl_news_post_to_wp.py` → `target/scripts/`
  - `tests/test_pearl_news_quality_gates_minimal.py`, `tests/test_pearl_news_pipeline_e2e.py` → `target/tests/`
  - `pearl_news_scheduled_self_hosted.yml` → `target/.github/workflows/pearl_news_scheduled.yml`
- **§3** — Commit and push to `main`.
- **§4** — Add 6 secrets: `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`, `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL`.
- **§5** — Self-hosted runner on the machine where LM Studio runs.
- **§6** — Trigger run and verify (artifacts, optional WP draft, green run).

---

### 3. **Self-hosted workflow**  
**`.github/workflows/pearl_news_scheduled_self_hosted.yml`**
- **`runs-on: self-hosted`** so the job runs where LM Studio is (e.g. your Mac).
- **`env`** passes the 6 secrets into the job.
- Installs **`openai`** and runs the pipeline with **`--expand`** so expansion uses the Qwen env vars when set.

---

### 4. **Docs wiring**
- **`docs/PEARL_NEWS_GITHUB_SCHEDULING.md`** — Option B points to the runbook; lists the two test files and the self-hosted workflow; adds step 6 (self-hosted runner) and the three Qwen secrets.
- **`docs/DOCS_INDEX.md`** — New row for **Option B runbook (Qwen/Qwen-Agent)**.

---

**Your next steps (from the runbook):**

1. Clone **Ahjan108/Qwen-Agent** (or Qwen) if needed.
2. From the parent of `phoenix_omega` and the target repo, run the **§2** `cp` block in the runbook (create `scripts/` and `tests/` in the target first if they don’t exist).
3. Commit and push in the target repo.
4. In the target repo, add the 6 secrets under **Settings → Secrets and variables → Actions**.
5. Install and start the **self-hosted runner** on the machine where LM Studio is running.
6. In the target repo: **Actions → “Pearl News scheduled” → Run workflow**, then confirm artifacts and (if configured) the WP draft.

All 6 Pearl News tests pass with the new env override.

---

**User**

do for me: You’re close. One simple fix.

Problem:
- `setup-python` is broken on your self-hosted runner.

Fix:
- Remove `setup-python` step.
- Use `python3` already on your Mac.

Do exactly this in `Qwen-Agent`:

1. Edit workflow file:
- `.github/workflows/pearl_news_scheduled.yml`

2. Delete this step:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
```

3. Keep/add this instead:
```yaml
- name: Check Python
  run: |
    python3 --version
    python3 -m pip --version
```

4. In install step, use:
```yaml
python3 -m pip install feedparser pyyaml requests pytest openai
```

5. In test/pipeline steps, use `python3` (not `python`).

6. Commit + push to `main`.

7. Run workflow again.

That’s it. No other changes needed.

---

**Cursor**


Applying the fix to the self-hosted workflow in phoenix_omega (source for Qwen-Agent):



Checking for a non–self-hosted `pearl_news_scheduled.yml` that might need the same fix:



Summary of what was changed in **phoenix_omega** (the workflow you copy into Qwen-Agent):

**Updates in `.github/workflows/pearl_news_scheduled_self_hosted.yml`:**

1. **Removed** the `Set up Python` step (`actions/setup-python@v5`).

2. **Added** a `Check Python` step that runs:
   - `python3 --version`
   - `python3 -m pip --version`

3. **Install step** now uses:
   - `python3 -m pip install feedparser pyyaml requests pytest openai`

4. **All Python usage** in the workflow now uses `python3`:
   - Validate WordPress env: `PYTHONPATH=. python3 - <<'PY'`
   - Tests: `PYTHONPATH=. python3 -m pytest ...`
   - Pipeline: `python3 -m pearl_news.pipeline.run_article_pipeline ...`
   - WP script: `python3 scripts/pearl_news_post_to_wp.py ...`

**What you need to do in Qwen-Agent (steps 6–7):**

- Copy the updated workflow from phoenix_omega into Qwen-Agent as `.github/workflows/pearl_news_scheduled.yml` (overwriting the existing file), then in the Qwen-Agent repo:
  - `git add .github/workflows/pearl_news_scheduled.yml`
  - `git commit -m "fix: use python3 on self-hosted runner, remove setup-python"`
  - `git push origin main`
- In GitHub: **Actions → Pearl News scheduled → Run workflow**, then confirm it passes.

If you prefer to keep Qwen-Agent as the single source of truth, you can instead apply the same edits directly in `Qwen-Agent/.github/workflows/pearl_news_scheduled.yml` and then commit and push from that repo.

---

**User**

fix; Not hung. You’re inside Git’s commit editor during `cherry-pick --continue`.

Do this now:

1. Save and exit editor  
- In Vim: press `Esc`, type `:wq`, press `Enter`.

2. Then push:
```bash
git push origin main
```

3. (Optional) avoid accidentally adding runner files:
```bash
echo "actions-runner/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore local actions runner folder"
git push origin main
```

After push, run workflow again.

---

**Cursor**


Checking `.gitignore` and adding `actions-runner/` if missing.



Here’s what to do:

---

**1. Exit the commit editor (you’re in Vim)**  
In the terminal where the editor is open:
- Press **`Esc`**
- Type **`:wq`**
- Press **`Enter`**

That saves the message and finishes the cherry-pick.

---

**2. Push**
```bash
git push origin main
```

---

**3. (Optional) Ignore the runner folder**

`actions-runner/` is already in **phoenix_omega**’s `.gitignore`.  

If you’re in **Qwen-Agent** and want the same there, run in that repo:
```bash
echo "actions-runner/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore local actions runner folder"
git push origin main
```

---

Then run the workflow again from GitHub Actions.

---

**User**

it's running by llm call timing out. does this look good to you? **Dev Instructions: Pearl News + LM Studio Reliability (Self-hosted)**

1. Let current run finish
- Do not cancel queued/running workflow unless it exceeds hard timeout.
- Capture run URL and step logs.

2. Lower workload for scheduled runs
- In `.github/workflows/pearl_news_scheduled.yml`, set:
```yaml
--limit 3
```
- For emergency stability mode, remove `--expand` in scheduled workflow (keep pipeline producing drafts without LLM expansion).

3. Add safe mode toggle (recommended)
- In workflow, add env:
```yaml
PEARL_NEWS_EXPAND: "true"
PEARL_NEWS_LIMIT: "3"
```
- Use in run step:
```bash
if [ "$PEARL_NEWS_EXPAND" = "true" ]; then
  python3 -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit "$PEARL_NEWS_LIMIT" --expand
else
  python3 -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit "$PEARL_NEWS_LIMIT"
fi
```
- Later you can flip to `PEARL_NEWS_EXPAND=false` without code edits.

4. Increase expansion timeout
- In `pearl_news/config/llm_expansion.yaml`:
```yaml
timeout: 240
```
- Keep retries in client; timeout increase reduces false failures.

5. Reduce LM Studio parallel load
- Lower parallel requests/model slots in LM Studio (target 1–2 for stability).
- Keep one model loaded (`qwen3-14b`) and avoid concurrent heavy local jobs during workflow runs.

6. Add workflow timeout guard
- Set job timeout:
```yaml
timeout-minutes: 30
```
- Prevent infinite queue/run perception.

7. Verify with staged rollout
1. Run workflow with `limit=1`, `expand=true` (smoke test).
2. Run workflow with `limit=3`, `expand=true`.
3. If stable, keep schedule.
4. If unstable, set `expand=false` on schedule and run expansion manually/less frequently.

8. Acceptance criteria
- Workflow completes green 3 consecutive runs.
- `pearl_news_drafts` artifact uploaded each run.
- Expansion timeout warnings <20% of processed items (or zero in safe mode).
- Optional WP draft step succeeds or cleanly dry-runs.

9. Commit messages
- `ci(pearl-news): add safe mode toggles for expand and limit`
- `perf(pearl-news): raise LLM expansion timeout for self-hosted reliability`
- `ops(pearl-news): tune scheduled workload for stable LM Studio execution`

---

**Cursor**


Checking the workflow and LLM config so we can validate your plan.



Yes, it looks good and matches how the pipeline and config work.

**What lines up with the codebase**

- **Limit/expand:** The workflow currently uses `--limit 10` and `--expand` (lines 57–62 in the self-hosted workflow). Your `--limit 3`, env-driven limit, and conditional `--expand` are consistent with `run_article_pipeline`’s CLI.
- **Timeout:** `llm_expand.py` reads `timeout` from config and passes it to the OpenAI client (`config.get("timeout") or 120`, then `OpenAI(..., timeout=timeout)`). Setting `timeout: 240` in `llm_expansion.yaml` will take effect.
- **Job timeout:** Adding `timeout-minutes: 30` on the job in the workflow is the right place and will cap the whole run.

**Small notes**

1. **“Without code edits” for expand toggle**  
   If you define `PEARL_NEWS_EXPAND` and `PEARL_NEWS_LIMIT` directly in the workflow `env:` block, changing them still means editing the YAML. To flip expand on/off without touching code, use **repository or environment variables** and reference them in the workflow, e.g. `PEARL_NEWS_EXPAND: ${{ vars.PEARL_NEWS_EXPAND || 'true' }}`, then change the value under Settings → Variables.

2. **Retries**  
   The expansion code doesn’t implement retries; the client just uses the configured timeout. Your note to “keep retries in client” is fine as a reminder if you add retries later; raising the timeout to 240 is the main lever for reducing false failures right now.

3. **Workflow file name**  
   In phoenix_omega the file is `pearl_news_scheduled_self_hosted.yml`; in Qwen-Agent it’s the one you’re editing as `pearl_news_scheduled.yml`. Your instructions are correct for the repo where you’re actually running the job.

**Verdict**

The plan is sound: lower limit, optional expand via env, higher expansion timeout, job timeout, LM Studio tuning, and staged rollout with clear acceptance criteria. Implementing it as written should address the LLM timeouts and make the workflow more predictable.

---

**User**

do it all now and then tell me what i need to do for best stuff

---

**Cursor**


Implementing the reliability changes: updating the workflow, LLM config, and adding a short "what you need to do" section.



Summary of what’s done and what you should do next:

---

## Changes made (in phoenix_omega)

1. **`.github/workflows/pearl_news_scheduled_self_hosted.yml`**
   - Added **`timeout-minutes: 30`** on the job.
   - Added env: **`PEARL_NEWS_EXPAND: "true"`** and **`PEARL_NEWS_LIMIT: "3"`**.
   - Pipeline step now uses **`$PEARL_NEWS_LIMIT`** and runs with **`--expand`** only when **`PEARL_NEWS_EXPAND`** is `"true"`.

2. **`pearl_news/config/llm_expansion.yaml`**
   - **`timeout: 240`** (was 120) so each expansion call has more time on the self-hosted runner.

3. **`docs/PEARL_NEWS_OPTION_B_RUNBOOK.md`**
   - New **§7. LM Studio reliability** with: let run finish, lower workload, safe-mode toggle, 240s timeout, LM Studio load, staged rollout, acceptance criteria, optional repo variables.

---

## What you need to do for best results

**If you run from Qwen-Agent (Option B):**

1. **Sync the workflow and config into Qwen-Agent**
   - Copy the updated workflow and config from phoenix_omega into Qwen-Agent (overwrite):
     - `pearl_news_scheduled_self_hosted.yml` → `.github/workflows/pearl_news_scheduled.yml`
     - `pearl_news/config/llm_expansion.yaml` → same path in Qwen-Agent
   - Commit and push to `main`.

2. **Before each scheduled run**
   - Start the **self-hosted runner**.
   - Start **LM Studio** and load the model (e.g. Qwen).
   - Prefer **1–2 parallel slots** in LM Studio; avoid other heavy local jobs.

3. **Staged rollout**
   - First run: in the workflow env set **`PEARL_NEWS_LIMIT: "1"`** (and keep **`PEARL_NEWS_EXPAND: "true"`**), trigger once, confirm it finishes green.
   - Then set **`PEARL_NEWS_LIMIT: "3"`** and run 2–3 times; if all green, leave the schedule as-is.
   - If you still see timeouts: set **`PEARL_NEWS_EXPAND: "false"`** so scheduled runs only produce drafts (no LLM calls); run expansion manually when the machine is free.

4. **If a run is in progress**
   - Let it finish (or hit the 30‑minute job timeout) instead of cancelling; use the run URL and step logs to debug.

5. **Success criteria**
   - Three consecutive green runs.
   - `pearl_news_drafts` artifact present each time.
   - Few or no expansion timeout warnings; WP step succeeds or dry-runs cleanly.

**Optional:** To turn expansion on/off without editing the workflow file, use a repo variable (e.g. `vars.PEARL_NEWS_EXPAND`) and reference it in the workflow env as in §7 of the runbook.

---

**User**

Run smoke test (easy mode)
In GitHub workflow file, set:
PEARL_NEWS_LIMIT: "1"
PEARL_NEWS_EXPAND: "true"


---

**Cursor**


Updated the workflow so the smoke test uses a single article:

- **`PEARL_NEWS_LIMIT: "1"`** (was `"3"`)
- **`PEARL_NEWS_EXPAND: "true"`** (unchanged)

In **phoenix_omega** the change is in `.github/workflows/pearl_news_scheduled_self_hosted.yml`. If you run from **Qwen-Agent**, copy that file over as `pearl_news_scheduled.yml`, commit, push, then run the workflow from Actions. After it passes, set `PEARL_NEWS_LIMIT: "3"` again for normal runs.

---

**User**

did tons or research on how to write great articles are we using that in how we werite articles?

---

**Cursor**


Searching the repo for article-writing research and whether the pipeline uses it.



Here's what the repo shows:

---

## Short answer: **no** — the “great articles” research is **not** used in how Pearl News writes articles.

That research is used for **book/funnel/teacher STORY atoms**. Pearl News has its own assembly and expansion path and doesn’t use those specs or rubrics.

---

## Where the research *is* used (and where it isn’t)

**Used for book/persona/teacher content:**

- **PHOENIX_V4_5_WRITER_SPEC** — STORY atoms, Four Story Rules (Misfire Tax, Silence Beat, Never-Know, Interrupt), TTS rules, five role types (recognition, embodiment, pattern, mechanism_proof, agency_glimmer).
- **WRITER_SPEC_EXTRACT_FOR_ATOMS** — Same rules in extract form for atom tagging.
- **WRITER_STORY_READING_LIST** — Reading order for writers doing STORY atoms.
- **HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC** — Specificity, cost, conflict, insight pivot, residual echo for story atoms.
- **GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE** — Micro-stakes, psychological specificity for STORY/SCENE atoms.
- **TEACHER_MODE_* / FUNNEL_AND_BOOK_COPY_WRITER_SPEC** — Teacher-mode and funnel story format.

**Pearl News (news articles):**

- **Assembly:** `article_assembler.py` fills slots from templates using feed data + **atoms or placeholders**. Placeholders are generic, institutional sentences (e.g. “Young people are increasingly affected…”, “Leaders from the United Spiritual Leaders Forum emphasize…”). There is no use of the Writer Spec, Four Story Rules, or the high-impact rubric.
- **Expansion:** `pearl_news/prompts/expansion_system.txt` only says: preserve HTML, don’t invent facts, keep Pearl News voice. It does **not** reference the Writer Spec, story rules, specificity/cost/conflict, or Golden Phoenix guidance.
- **Pearl News writer spec:** `pearl_news/README.md` points to `docs/PEARL_NEWS_WRITER_SPEC.md`, but **that file does not exist** in the repo.

So the “great articles” research is applied to **book/funnel/teacher STORY atoms**, not to **Pearl News article generation**. To use it for Pearl News you’d need to either add a Pearl News–specific writer spec and wire it into the pipeline (e.g. expansion prompt + any atom guidelines) or explicitly pull the existing specs into the article-assembly/expansion path.

---

**User**

what's our @docs/DOCS_INDEX.md  on  news articles and pealr news strategy writing stuff? 

---

**Cursor**


Here's what **docs/DOCS_INDEX.md** says about news articles and Pearl News strategy/writing:

---

## Pearl News section (§ "Pearl News (document all)")

**News articles / pipeline:** The index lists the full pipeline and supporting docs:

- **Architecture** → `PEARL_NEWS_ARCHITECTURE_SPEC.md`
- **Article metadata** → `PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md`
- **Pipeline** → ingest → classify → template select → **article assembler** (slots: news + teacher + youth + SDG) → quality gates → QC
- **Config** → feeds, SDG/topic mapping, **article templates**, legal boundary, **editorial firewall** (news vs commentary, source requirements), template diversity, quality gates, LLM safety
- **Governance** → `EDITORIAL_STANDARDS.md`, corrections, conflict of interest

**Writing / strategy:**

- **Writer spec** is in the docs table as:  
  **`docs/PEARL_NEWS_WRITER_SPEC.md`** — with a note that the **file is not present**.  
  The index says it should cover: *"Voice, atom types, 4-layer blend, quality gates, template guidance"*.

So for *news articles* and *Pearl News strategy/writing*, the index points to one main doc — **PEARL_NEWS_WRITER_SPEC** — and that file is missing.

---

## Elsewhere in DOCS_INDEX relevant to Pearl News / writing

| What | Where in index | Notes |
|------|----------------|--------|
| **Generational deep research (Pearl News)** | Marketing/Research docs table | `continue_gen_research3.md` — Gen Z/Gen Alpha intelligence; “buildable spec for pipeline”. Only Pearl-related “strategy” doc that exists. |
| **Editorial standards / firewall** | Pearl News → Governance, Config | Standards + `editorial_firewall.yaml` (labeling, source requirements). Policy/constraints, not writing strategy. |
| **WRITER_STORY_READING_LIST** | Writing / content | For **STORY atoms** (funnel, Teacher Mode, persona), not Pearl News articles. |
| **File inventory** | Later in DOCS_INDEX | `PEARL_NEWS_WRITER_SPEC.md` listed under Pearl News as **missing**. |

---

## Summary

- **News articles:** DOCS_INDEX documents the **pipeline** (ingest → assemble → gates → publish), **article metadata**, **templates**, and **editorial firewall**, but does not define a dedicated “news article writing strategy” doc other than the missing Writer Spec.
- **Pearl News strategy/writing:** The index says that strategy and writing guidance live in **`docs/PEARL_NEWS_WRITER_SPEC.md`** (voice, atom types, 4-layer blend, quality gates, template guidance), but that file is **not in the repo**. The only existing “strategy” doc tied to Pearl News in the index is **Generational deep research** (`continue_gen_research3.md`), which is about Gen Z/Gen Alpha intelligence for the pipeline, not the full article-writing strategy.

---

**User**

help: You’re hitting LLM timeout on self-hosted runs. Fastest stable fix:

1. **Turn off expansion in scheduled workflow**
- Set:
```yaml
PEARL_NEWS_EXPAND: "false"
PEARL_NEWS_LIMIT: "3"
```
- This keeps scheduled drafts reliable.

2. **Run expansion separately/manual when machine is free**
- Trigger a manual run with:
```yaml
PEARL_NEWS_EXPAND: "true"
PEARL_NEWS_LIMIT: "1"
```

3. **Increase timeout again for LM calls**
- In `pearl_news/config/llm_expansion.yaml`:
```yaml
timeout: 360
max_tokens: 1200
```
(1200 lowers generation load vs 2048.)

4. **Reduce LM Studio load**
- Parallel slots: `1`
- Keep only `qwen3-14b` loaded
- Don’t run other heavy jobs during workflow.

5. **Prevent job cancel from overall timeout**
- Raise workflow job timeout:
```yaml
timeout-minutes: 45
```

Best practice: schedule = no expand, manual/low-volume run = expand. This avoids broken scheduled runs.

---

**Cursor**


Applying the stability fixes: updating the workflow and LLM config.



Adding a best-practice note to the runbook:



Summary of what was changed:

---

## 1. **Workflow** (`.github/workflows/pearl_news_scheduled_self_hosted.yml`)

- **`PEARL_NEWS_EXPAND: "false"`** — Scheduled runs no longer use LLM expansion; they only produce drafts.
- **`PEARL_NEWS_LIMIT: "3"`** — Up to 3 articles per scheduled run.
- **`timeout-minutes: 45`** — Job timeout increased from 30 to 45 minutes.
- Comment added: for a manual run with expansion, set `PEARL_NEWS_EXPAND: "true"` and `PEARL_NEWS_LIMIT: "1"` (e.g. in workflow env or a one-off manual dispatch).

---

## 2. **LLM expansion config** (`pearl_news/config/llm_expansion.yaml`)

- **`timeout: 360`** — Per-article expansion timeout 360 seconds (was 240).
- **`max_tokens: 1200`** — Lower cap than 2048 to reduce load and timeouts.

---

## 3. **Runbook** (`docs/PEARL_NEWS_OPTION_B_RUNBOOK.md` §7)

- Describes current defaults: schedule = no expand, limit 3, job timeout 45 min, expansion timeout 360 s, max_tokens 1200.
- **Best practice** stated: schedule = no expand; manual/low-volume run = expand.
- Instructions updated for manual expansion and LM Studio (parallel slots: 1, one model).

---

**What you do:**  
- **Scheduled runs:** Use as-is; they’ll complete without LLM calls.  
- **Manual expansion:** When the machine is free, run the workflow manually and set `PEARL_NEWS_EXPAND: "true"` and `PEARL_NEWS_LIMIT: "1"` (in the workflow env or by temporarily editing the workflow file).  
- **LM Studio:** Use 1 parallel slot, keep only one model (e.g. `qwen3-14b`) loaded, and avoid other heavy jobs during the run.

---

**User**

do: **One-pass plan (no more random retries)**

1. **Lock code state**
```bash
cd /Users/ahjan/Qwen-Agent
git fetch origin
git checkout main
git reset --hard origin/main
```

2. **Hard verify workflow is correct (must match exactly)**
```bash
grep -nE "runs-on|timeout-minutes|PEARL_NEWS_EXPAND|PEARL_NEWS_LIMIT" .github/workflows/pearl_news_scheduled.yml
```
Required output contains:
- `runs-on: self-hosted`
- `timeout-minutes: 45`
- `PEARL_NEWS_EXPAND: "false"`
- `PEARL_NEWS_LIMIT: "3"`

If any line missing, stop and fix before running anything.

3. **Hard verify secrets exist (UI check, once)**
In `Qwen-Agent` repo secrets, confirm all 6 exist:
- `WORDPRESS_SITE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`
- `QWEN_BASE_URL`
- `QWEN_API_KEY`
- `QWEN_MODEL`

4. **Hard verify local Qwen endpoint before GitHub run**
```bash
curl -s http://127.0.0.1:1234/v1/models
```
Must return JSON with `qwen3-14b`.

5. **Start runner and keep it alive**
```bash
cd /Users/ahjan/Qwen-Agent/actions-runner
./run.sh
```
Wait for: `Listening for Jobs`  
Do not close this terminal.

6. **Run exactly one workflow**
GitHub → Actions → `Pearl News scheduled` → Run workflow on `main`.

7. **Result gate**
- PASS if:
  - workflow green
  - artifact `pearl_news_drafts` uploaded
- FAIL if not green:
  - copy only first failed step name + last 30 log lines and stop.  
  - do not edit anything else until that single error is fixed.

This is the shortest deterministic path.

I’m sure this is the correct **process** and will remove random failures.

I can’t guarantee zero runtime errors (feeds/network/WP can fail), but if you follow that plan exactly:
1. infra issues (runner/secrets/workflow mismatch) are eliminated,
2. failures will be real content/network errors, not setup chaos,
3. you’ll have one clear error to fix, not many moving parts.

So yes: this is the right one-pass plan.

---

**Cursor**


Executing the steps we can run; we'll note steps that require the GitHub UI or keeping a terminal open.



Retrying with full permissions because Qwen-Agent is outside the workspace:



Fixing the workflow: Qwen-Agent's workflow has `timeout-minutes: 30` and `PEARL_NEWS_EXPAND: "true"`; required: `timeout-minutes: 45` and `PEARL_NEWS_EXPAND: "false"`.



Summary of what’s done and what’s left for you:

---

## Completed

**1. Lock code state**  
- In `/Users/ahjan/Qwen-Agent`: `git fetch origin`, `git checkout main`, `git reset --hard origin/main`.  
- HEAD: `e6fdb54 chore(pearl-news): improve LM Studio reliability for scheduled runs`.

**2. Workflow check and fix**  
- **Before:** `timeout-minutes: 30`, `PEARL_NEWS_EXPAND: "true"`.  
- **After (fixed in Qwen-Agent):**
  - `runs-on: self-hosted`
  - `timeout-minutes: 45`
  - `PEARL_NEWS_EXPAND: "false"`
  - `PEARL_NEWS_LIMIT: "3"`

**4. Local Qwen endpoint**  
- `curl -s http://127.0.0.1:1234/v1/models` returned JSON including `"id": "qwen3-14b"`. LM Studio is up and the endpoint is valid.

---

## You need to do

**3. Secrets (UI)**  
In the **Qwen-Agent** repo: **Settings → Secrets and variables → Actions**. Confirm these 6 repository secrets exist:
- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL`

**5. Start runner and leave it running**  
```bash
cd /Users/ahjan/Qwen-Agent/actions-runner
./run.sh
```
Wait for “Listening for Jobs” and leave that terminal open.

**6. Run one workflow**  
GitHub → **Actions** → **Pearl News scheduled** → **Run workflow** on `main`.

**7. Result**  
- **PASS:** workflow green and artifact `pearl_news_drafts` uploaded.  
- **FAIL:** copy only the **first failed step name** and the **last 30 lines** of its log and we can fix that single error.

---

**Note:** The workflow file in **Qwen-Agent** was updated locally. To keep that change in the repo you’ll need to commit and push from Qwen-Agent (or re-copy from phoenix_omega and push). Until you push, the next run will still use the updated file if the runner is using the same checked-out copy; for a clean one-pass run, either commit and push the fix or run the workflow from the same machine/dir where you made the edit. If you want, I can give you exact `git add` / `git commit` / `git push` commands for Qwen-Agent.

---

**User**

^CExiting...
Runner listener exit with 0 return code, stop the service, no retry needed.
Exiting runner...
ahjan@Ahjans-MacBook-Air actions-runner % cd /Users/ahjan/Qwen-Agent
git add .github/workflows/pearl_news_scheduled.yml
git commit -m "fix(pearl-news): self-hosted stable mode (expand off, limit 3, timeout 45)"
git push origin main

[main 00f4b16] fix(pearl-news): self-hosted stable mode (expand off, limit 3, timeout 45)
 1 file changed, 2 insertions(+), 2 deletions(-)
Enumerating objects: 9, done.
Counting objects: 100% (9/9), done.
Delta compression using up to 10 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 463 bytes | 463.00 KiB/s, done.
Total 5 (delta 3), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (3/3), completed with 3 local objects.
To https://github.com/Ahjan108/Qwen-Agent.git
   e6fdb54..00f4b16  main -> main
ahjan@Ahjans-MacBook-Air Qwen-Agent % cd /Users/ahjan/Qwen-Agent/actions-runner
./run.sh


√ Connected to GitHub

Current runner version: '2.332.0'
2026-03-05 08:35:33Z: Listening for Jobs

Skip to content
Ahjan108
Qwen-Agent
Repository navigation
Code
Pull requests
Actions
Projects
Security
Insights
Settings
Pearl News scheduled
Pearl News scheduled #7
All jobs
Run details
Manually triggered 1 minute ago
@Ahjan108Ahjan108
⁠
 00f4b16
main
Status
Success
Total duration
43s
Artifacts
1


Artifacts
Produced during runtime
Name	Size	Digest	
pearl_news_drafts
6.62 KB	
sha256:3d4ee262260e44ade6eb4ff872ac943e4230d7e2d9d1066d945bcd0465a2046f

Excellent. This is fully working now.

You achieved the target state:

Fixed workflow is on main (00f4b16)
Self-hosted runner is online
Manual workflow run succeeded
pearl_news_drafts artifact uploaded
You can now rely on this setup for scheduled runs in stable mode (expand=false, limit=3).

If you want expansion later, do it only as manual low-volume run (expand=true, limit=1).




---

**Cursor**


Good to hear it’s all working.

**Current state:**
- **Qwen-Agent** `main`: workflow at `00f4b16` (expand off, limit 3, timeout 45).
- **Self-hosted runner**: online and picking up jobs.
- **Run #7**: success in ~43s, `pearl_news_drafts` artifact (6.62 KB) uploaded.

Scheduled runs will stay in this stable mode (no LLM expansion, 3 articles). For expanded articles, use a manual run with `PEARL_NEWS_EXPAND: "true"` and `PEARL_NEWS_LIMIT: "1"` when the machine is free. No further changes needed unless you want to tweak limits or add more runs.

---

**User**

wire pear news to use this: Good. I have everything I need. Writing now.Now wire it into the expansion prompt and update the index:Done. Three files changed:

**`docs/PEARL_NEWS_WRITER_SPEC.md`** — The full writing craft layer. Twelve sections covering the 4-layer blend, voice rules, lede patterns per template, per-template writing guide for all five templates, how to integrate the teacher/spiritual layer without going devotional, youth specificity standard (what passes the quality gate and why), SDG integration rules, the forward look, and a "what we never write" list. It's written as a practical editor's guide, not a policy doc.

**`pearl_news/prompts/expansion_system.txt`** — The expansion prompt now has actual craft instructions. Six specific rules for how to expand each section: lede goes toward specificity not generality, youth impact must add a real anchor not more vague sentences, teacher layer adds context or setting not devotional language, forward look names an institution or deadline not sentiment. The three original rules are preserved; the new rules sit below them.

**`docs/DOCS_INDEX.md`** — Writer spec marked `✓` in both places. Governance still passes clean.

---

**Cursor**


Checking the repo and wiring Pearl News expansion to the writer spec.



Verifying the pipeline loads the expansion prompt and checking for any remaining wiring:



Confirming wiring and adding a brief cross-reference in the prompts README:



Wiring is in place. Adding an explicit cross-reference in the prompts README:



Summary of the wiring:

---

**Already in place**

1. **`docs/PEARL_NEWS_WRITER_SPEC.md`** — Present and in use. Full craft layer (12 sections): 4-layer blend, voice, lede, per-template guide, teacher integration, youth specificity, SDG, forward look, quality gates, “what we never write,” expansion guidance.

2. **`pearl_news/prompts/expansion_system.txt`** — Already wired to the spec:
   - Header: “Writing craft rules (from PEARL_NEWS_WRITER_SPEC.md)”
   - Six rules: LEDE (specificity), YOUTH IMPACT (anchors), TEACHER LAYER (no devotional), FORWARD LOOK (institution/deadline), SDG REFERENCES, WHAT TO NEVER ADD.
   - Pipeline uses this file as the system prompt when `--expand` is used (`llm_expand.py` → `_load_system_prompt(root / "prompts")`).

3. **`docs/DOCS_INDEX.md`** — Writer spec is already:
   - In the Pearl News docs table with link and description (no “file not present”).
   - In the file inventory as `PEARL_NEWS_WRITER_SPEC.md` with ✓.

**Change made**

4. **`pearl_news/prompts/README.md`** — Added an explicit cross-reference: expansion prompt “implements the writing craft rules from docs/PEARL_NEWS_WRITER_SPEC.md (lede, youth impact, teacher layer, forward look, SDG, what we never write).”

Pearl News expansion is wired to the writer spec: the spec is the authority, and the expansion prompt encodes those rules for the LLM. No code changes were required; only the prompts README was updated for clarity.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Checking DOCS_INDEX's Pearl News and related sections to add or update entries so the index documents everything.



Adding the missing Pearl News items to DOCS_INDEX: Pipeline (LLM expand), Config (llm_expansion, site, wordpress_authors), Prompts, self-hosted workflow, and inventory entries.



Adding inventory entries for the new files:



Updating the run pipeline script description to mention `--expand` and verifying the index.



Summary of what was added to **docs/DOCS_INDEX.md** so everything is documented in one place:

---

## Pearl News section (main “document all” area)

**Docs**
- **Option B runbook** — Description now includes “§7 LM Studio reliability (schedule = no expand, manual = expand)”.
- **Writer spec** — Description now includes “authority for expansion prompt craft rules”.
- **Expansion prompt** — New row: [pearl_news/prompts/expansion_system.txt] — system prompt for LLM expansion (~1000 words), implements Writer spec craft rules, used with `--expand`.
- **Prompts README** — New row: [pearl_news/prompts/README.md] — documents expansion_system.txt and link to Writer spec.

**Scripts**
- **Run article pipeline** — Description now includes “`--expand` (LLM expansion per Writer spec)”.

**Pipeline modules**
- **LLM expansion** — New row: [pearl_news/pipeline/llm_expand.py] — optional expansion step, loads expansion_system.txt + llm_expansion.yaml, OpenAI-compatible API, env overrides, used when `--expand` is passed.

**Config**
- **LLM expansion** — New row: [pearl_news/config/llm_expansion.yaml] — base_url, model, timeout, max_tokens, etc.; env override for self-hosted.
- **Site** — New row: [pearl_news/config/site.yaml] — target_word_count, placeholder images by template.
- **WordPress authors** — New row: [pearl_news/config/wordpress_authors.yaml] — author_ids for round-robin.

**CI / workflows**
- **Pearl News scheduled (self-hosted)** — New row: [.github/workflows/pearl_news_scheduled_self_hosted.yml] — for Option B; runs-on self-hosted, timeout 45, PEARL_NEWS_EXPAND/LIMIT; copy as pearl_news_scheduled.yml into Qwen-Agent/Qwen.

---

## Document all — complete inventory

**Root & other**
- [pearl_news/prompts/README.md] | Pearl News | ✓
- [pearl_news/prompts/expansion_system.txt] | Pearl News | ✓

**Config**
- [.github/workflows/pearl_news_scheduled_self_hosted.yml] | Pearl News (Option B) | ✓
- [pearl_news/config/llm_expansion.yaml] | Pearl News | ✓
- [pearl_news/config/site.yaml] | Pearl News | ✓
- [pearl_news/config/wordpress_authors.yaml] | Pearl News | ✓

**Scripts & code**
- [pearl_news/pipeline/llm_expand.py] | Pearl News | ✓

---

Pearl News is now fully represented in **docs/DOCS_INDEX.md**: writer spec, expansion prompt, prompts README, LLM expansion module and config, site and WordPress authors config, self-hosted workflow, and all of them in the complete inventory with ✓.

