# Translate / prompt via Qwen GitHub pipeline CLI — all system languages

**Purpose:** Run translation and prompt workflows for **all system languages** using the Qwen-based GitHub pipeline (scheduled or manual). Single reference for which locales are in scope and how to trigger the pipeline from phoenix_omega or from Qwen/Qwen-Agent forks.

**Authority:** [config/localization/locale_registry.yaml](../config/localization/locale_registry.yaml) is the source of truth for system locales. This doc lists them and points to pipeline/CLI entry points.

**Last updated:** 2026-03-04

---

## 1. System languages (all locales)

All locales below are **system languages** for translation and prompt pipelines. Run translate/prompt for every locale when doing a full pass.

| Locale   | Language              | Region / market   | EU catalogue |
|----------|------------------------|-------------------|--------------|
| en-US    | English                | United States     | —            |
| zh-CN    | Chinese (Simplified)   | Mainland China    | —            |
| zh-TW    | Chinese (Traditional)  | Taiwan            | —            |
| zh-HK    | Chinese (Traditional)   | Hong Kong         | —            |
| zh-SG    | Chinese (Simplified)   | Singapore         | —            |
| ja-JP    | Japanese               | Japan             | —            |
| ko-KR    | Korean                 | South Korea       | —            |
| es-US    | Spanish (US Hispanic)   | US Hispanic       | —            |
| es-ES    | Spanish (Castilian)    | Spain             | ✓            |
| fr-FR    | French                 | France            | ✓            |
| de-DE    | German                 | Germany / DACH    | ✓            |
| **it-IT**| **Italian**            | **Italy**         | **✓**        |
| hu-HU    | Hungarian              | Hungary           | ✓            |

**EU catalogue locales:** de-DE, es-ES, fr-FR, it-IT, hu-HU (see [LOCALE_CATALOG_MARKETING_PLAN.md](./LOCALE_CATALOG_MARKETING_PLAN.md)).

---

## 2. Running the pipeline (phoenix_omega)

- **Translation (atoms/exercises):** Use the translation scripts and CI workflows that target all locales in `locale_registry.yaml`.
  - Scripts: [scripts/translate_atoms_all_locales_cloud.py](../scripts/translate_atoms_all_locales_cloud.py), [scripts/scaffold_locale_atom_stubs.py](../scripts/scaffold_locale_atom_stubs.py), [scripts/validate_translations.py](../scripts/validate_translations.py), [scripts/merge_translation_shards.py](../scripts/merge_translation_shards.py).
  - Workflows: `.github/workflows/translate-atoms-qwen-matrix.yml` (if present), `.github/workflows/locale-gate.yml` (if present).
- **Prompt / article pipeline (Pearl News):** [pearl_news/pipeline/run_article_pipeline.py](../pearl_news/pipeline/run_article_pipeline.py). See [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) for scheduled runs and WordPress posting.

---

## 3. Running from Qwen / Qwen-Agent (GitHub pipeline CLI)

You can run the same pipeline from forks [Ahjan108/Qwen](https://github.com/Ahjan108/Qwen) or [Ahjan108/Qwen-Agent](https://github.com/Ahjan108/Qwen-Agent) so that scheduling or CLI invocation lives there.

**Steps (summary):**

1. Clone the target repo (e.g. Ahjan108/Qwen or Ahjan108/Qwen-Agent).
2. Copy from phoenix_omega: `pearl_news/`, relevant scripts, and tests. Pearl News workflow YAMLs are canonical in Qwen-Agent (not in phoenix_omega).
3. Add repo secrets if posting (e.g. WordPress).
4. Trigger via GitHub Actions (scheduled or `workflow_dispatch`) or run the pipeline CLI locally against the cloned repo.

**Full procedure:** [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) §3 — Running the pipeline in other repos (Qwen / Qwen-Agent).

**Qwen forks and backup:** [QWEN_FORKS_AND_BACKUP.md](./QWEN_FORKS_AND_BACKUP.md).

---

## 4. Translate vs prompt

| Task              | Scope                    | Entry point / CLI |
|-------------------|--------------------------|-------------------|
| **Translate**     | All system languages     | Translation scripts + translate-atoms-qwen-matrix (or equivalent); locale list from `locale_registry.yaml`. |
| **Prompt**        | Article/draft generation | Pearl News pipeline; see PEARL_NEWS_GITHUB_SCHEDULING. |
| **Full pass**     | All 13 locales          | Run translation pipeline for every locale in §1; ensure it-IT (Italian) is included in EU catalogue runs. |

---

## 5. Index

- **Locale registry:** [config/localization/locale_registry.yaml](../config/localization/locale_registry.yaml)
- **Content roots (per locale):** [config/localization/content_roots_by_locale.yaml](../config/localization/content_roots_by_locale.yaml)
- **EU catalogue & marketing:** [LOCALE_CATALOG_MARKETING_PLAN.md](./LOCALE_CATALOG_MARKETING_PLAN.md)
- **Pearl News scheduling (Qwen):** [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md)
- **Translation, validation & multilingual:** [DOCS_INDEX.md](./DOCS_INDEX.md) § Translation, validation & multilingual
- **New language onboarding:** [NEW_LANGUAGE_LOCATION_ONBOARDING.md](./NEW_LANGUAGE_LOCATION_ONBOARDING.md)
