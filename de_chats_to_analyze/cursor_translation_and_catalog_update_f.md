# Translation and catalog update for Italian
_Exported on 3/5/2026 at 17:54:49 GMT+8 from Cursor (2.5.25)_

---

**User**

@docs/DOCS_INDEX.md translate/prompt via Qwen github pipline cli  for all system languages. add itallian to EU cataloge.

---

**Cursor**


Reading DOCS_INDEX in sections and locating translation/EU/locale config.



Searching for the locale registry, EU catalogue definition, and translation/Qwen pipeline docs:



Reading the locale registry and content roots to add Italian and locate the "Document all" section for translations.



Checking the translation workflow and where to add the Qwen CLI section:



Implementing the plan: adding Italian to the EU catalogue and adding translate/prompt docs for the Qwen pipeline.



Adding a short Italian (it-IT) subsection to the marketing plan and creating the Qwen pipeline CLI doc.



Updating DOCS_INDEX to add the new doc and the "Translate / prompt via Qwen GitHub pipeline CLI" subsection:



Summary of what was done:

### 1. **Translate / prompt via Qwen GitHub pipeline CLI for all system languages**

- **New doc:** [docs/TRANSLATE_QWEN_PIPELINE_CLI.md](docs/TRANSLATE_QWEN_PIPELINE_CLI.md)
  - Lists all **13 system languages** (locales) and states that translation/prompt runs apply to all of them.
  - Describes how to run the pipeline from **phoenix_omega** (translation scripts, Pearl News pipeline) and from **Qwen/Qwen-Agent** forks (with a pointer to [PEARL_NEWS_GITHUB_SCHEDULING.md](docs/PEARL_NEWS_GITHUB_SCHEDULING.md) §3).
  - Clarifies translate vs prompt and points to `locale_registry.yaml`, content roots, and EU catalogue.

- **DOCS_INDEX.md** updates:
  - New subsection **“Translate / prompt via Qwen GitHub pipeline CLI (all system languages)”** under “Translation, validation & multilingual” with a link to the new doc and to Pearl News scheduling.
  - New doc added to the Translation “Docs” table and to the “Document all — complete inventory” table.
  - All references to “12 locales” in that section updated to **13 locales** (including it-IT).
  - it-IT added to the “Coverage by locale” table and to the locale personas inventory line.

### 2. **Italian (it-IT) added to EU catalogue**

- **config/localization/locale_registry.yaml**
  - New **it-IT** locale (Italian, Italy): language, script, TTS (ElevenLabs + Google it-IT-Neural2-A), storefronts (Google Play, Findaway, Apple Books, Kobo, Spotify).
  - **it-IT** added to `locale_groups.european` and `locale_groups.all_locales`.

- **config/localization/content_roots_by_locale.yaml**
  - New **it-IT** entry: `atoms/it-IT`, translation source en-US, Phase 4 rollout, TTS notes, quality_contracts dir.

- **docs/LOCALE_CATALOG_MARKETING_PLAN.md**
  - Status line updated to **13 locales** and “EU catalogue includes de-DE, es-ES, fr-FR, **it-IT**, hu-HU”.
  - **it-IT** row added to the “Catalog Size Progression by Phase” table (Phase 4, 14 pilot books, 2 brands).
  - New subsection **“it-IT (Italian): Italy Market (EU catalogue)”**: invisible script, cultural context, search keywords, title philosophy, platforms, Phase 4 timeline, TTS.
  - New **“it-IT Go-Live Checklist (EU catalogue)”** (content, technical, distribution, launch status).
  - Marketing positioning section updated to “thirteen locales (including EU: de-DE, es-ES, fr-FR, it-IT, hu-HU)”.

Translation/prompt for all system languages is now documented and wired through DOCS_INDEX, and Italian is fully included in the EU catalogue and locale config.

---

**User**

more robbust itellegent testing 

---

**Cursor**


Implementing more robust, intelligent testing: adding sanity/intelligence tests, expanding conftest and pytest config, and documenting the approach.



All nine tests passed. Making the timeout option optional so pytest doesn't fail when pytest-timeout isn't installed:



Summary of what was added for **more robust, intelligent testing**:

### 1. **Pytest config** (`pytest.ini`)
- **Default timeout:** `timeout = 120` (seconds per test) to avoid CI hanging (uses `pytest-timeout`).
- **New markers:** `sanity` (fast sanity checks) and `intelligent` (data-driven / parametrized over configs and locales).
- Reference to `ROBUST_INTELLIGENT_TESTING.md`.

### 2. **Dependencies** (`requirements-test.txt`)
- **pytest-timeout>=2.0** so the timeout option is applied in CI.

### 3. **Shared fixtures** (`tests/conftest.py`)
- **Session-scoped:** `locale_registry_path`, `locale_registry`, `content_roots_path`, `content_roots`, `all_locale_ids`.
- **Helper:** `_load_yaml()` for loading YAML in tests.
- Enables parametrized and data-driven tests over all locales without reloading config every time.

### 4. **New test module** (`tests/test_robust_intelligent.py`) — 9 tests
- **Registry ↔ content roots:** Every locale in `locale_registry` has an entry in `content_roots_by_locale` (and vice versa).
- **Required fields:** Each locale has required keys in both registry and content roots (data-driven over all locales).
- **EU catalogue:** `locale_groups.european` includes de-DE, es-ES, fr-FR, it-IT, hu-HU.
- **Uniqueness:** No duplicate locale IDs in registry or in `all_locales`.
- **Groups vs registry:** Every ID in `locale_groups.all_locales` exists in `locales`.
- **Critical YAMLs:** `locale_registry`, `content_roots`, `format_registry` load without error.
- **Marketing config:** `consumer_language_by_topic` has expected structure when present.
- **TTS vs locale ID:** Each locale’s `tts_locale_code` matches its locale ID.

All of these are marked `sanity` and/or `intelligent` and run in the fast CI set (`-m "not slow"`). They completed in ~0.11s in a local run.

### 5. **Doc** (`docs/ROBUST_INTELLIGENT_TESTING.md`)
- Goals (robust, intelligent, fast, bounded).
- Marker usage and example commands (`-m sanity`, `-m "sanity or intelligent"`).
- Inventory of robust/intelligent tests and of conftest fixtures.
- Timeout behavior and how to add more sanity/intelligent tests.
- Links to FULL_REPO_TEST_SUITE_PLAN, DOCS_INDEX, conftest, pytest.ini.

### 6. **DOCS_INDEX updates**
- “How to run” table: added rows for `-m sanity` and `-m "sanity or intelligent"`.
- Test infrastructure: `pytest-timeout`, new markers, locale fixtures, link to ROBUST_INTELLIGENT_TESTING.
- Pytest markers table: `sanity` and `intelligent`.
- Full test file inventory: `test_robust_intelligent.py`.
- Document-all inventory: `ROBUST_INTELLIGENT_TESTING.md`.

**Note:** The fast suite run had **235 passed** (including all 9 new tests) and **1 failed**: `test_template_selector.py::TestTopicToTemplate::test_peace_conflict_to_interfaith`. That failure is pre-existing (template selector expectation for `peace_conflict` → `interfaith_dialogue_report` vs `hard_news_spiritual_response`) and is not caused by these changes.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Updating DOCS_INDEX to add a Video pipeline (document all) subsection and add every `scripts/video` script to the complete inventory.


