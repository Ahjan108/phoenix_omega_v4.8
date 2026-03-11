# Pearl News Feature Audit — Keep / Remove / Consolidate

## KEEP — The Best Stuff

### Editorial Brain (prompts & voice)
| File | Why |
|------|-----|
| `docs/pearl_news_prompts/00_SYSTEM_PROMPT.md` | Core editorial brain — reader psychology, voice DNA, trust architecture, 2-hook lede, term introduction sequence, action-to-teaching bridge |
| `docs/pearl_news_prompts/01–05_PREWRITE_*.md` | 5 enterprise-grade template prewrite prompts with move structures, attribution rules, banned phrases |
| `docs/pearl_news_prompts/06_DEV_INTEGRATION.md` | Developer implementation guide (token caps, LM Studio settings, context passing rules) |
| `pearl_news_genz_prompts_v2.md` | Master canonical voice document — screenshot test, stat test, 1AM test, 15+ banned phrases, all slot specs |
| `pearl_news/prompts/slot_by_slot/` (30+ files) | Production slot prompts — each slot has word count, move structure, banned openers, validation rules |

### Essential Configs
| File | Why |
|------|-----|
| `config/editorial_pillars.yaml` | 5 pillars (Planet, Mind, Work, Peace, Meaning) → topics, SDGs, colors, templates |
| `config/sdg_news_topic_mapping.yaml` | Topic → SDG classification with keyword hints |
| `config/teacher_news_roster.yaml` | 9 teachers → traditions, regions, topics, attribution templates |
| `config/teacher_exercise_bank.yaml` | 150 exercises, 4-tier fallback, policy rank — the exercise content |
| `config/selfhelp_topic_bridge.yaml` | News topic → self-help topic_id bridge for EI V2 |
| `config/editorial_firewall.yaml` | News/commentary separation + sourcing minimums |
| `config/legal_boundary.yaml` | UN affiliation blocklist — critical legal protection |
| `config/article_templates_index.yaml` | 5 template registry |
| `config/template_diversity.yaml` | Anti-repetition: signature tracking, per-week/month caps |
| `freebies/news_freebie_mapping.yaml` | SDG → CTA mode → freebie bundles + micro-actions |

### Article Templates, Atoms, Governance
| File | Why |
|------|-----|
| `article_templates/*.yaml` | 5 template slot definitions |
| `atoms/teacher_quotes_practices/` | Teacher quotes per topic — editorial content |
| `governance/` | Editorial Standards, Corrections, Conflict of Interest, Governance Page — publication credibility |

### Gold Standard Articles
| File | Why |
|------|-----|
| `pearl_news_gold_standard/*_v5.2.html` (4 files) | All v5.2 articles with full design system |
| `pearl_news_gold_standard/TEST_v5_editorial_fixes.html` | The canonical hard news v5 article |
| `pearl_news_gold_standard/WORDPRESS_POST_PLAN.md` | Complete WordPress publishing guide |

### Core Pipeline (lean)
| File | Why |
|------|-----|
| `pipeline/feed_ingest.py` | RSS ingestion — entry point |
| `pipeline/topic_sdg_classifier.py` | Keyword → topic/SDG — simple, essential |
| `pipeline/template_selector.py` | Template balancing — good algorithm |
| `pipeline/article_assembler.py` | Slot resolution with fallbacks — complex but necessary |
| `pipeline/teacher_resolver.py` | Hash-based teacher selection — lean |
| `pipeline/news_action_resolver.py` | Exercise + CTA + freebie selection — core feature |
| `pipeline/run_article_pipeline.py` | Orchestrator — essential |
| `pipeline/llm_expand.py` | LLM expansion — optional but needed for production |

---

## REMOVE — Over-Engineered / Redundant / Duplicate

### Over-Engineered Gates
| File | Why Remove |
|------|-----------|
| `pipeline/article_validator.py` | 12-gate post-expansion validator — redundant with quality_gates.py. Two validation systems doing similar checks. |
| `pipeline/qc_checklist.py` | Trivial 30-line wrapper around quality_gates. Just call quality_gates directly. |
| `config/quality_gates.yaml` | Rules already embedded in system prompt + prewrite prompts. The YAML + Python enforcement is the over-engineering layer. |
| `config/llm_safety.yaml` | Over-cautious: blocks full-article generation until 85% eval pass rate. This gates the pipeline instead of enabling it. |

### Administrative Tools (not article pipeline)
| File | Why Remove |
|------|-----------|
| `pipeline/teacher_onboarding.py` | 700-line admin CLI for scaffolding teacher atoms. Not part of article generation. Move to separate tools/ if needed later. |
| `pipeline/image_selector.py` | Rule-based image scoring. v5.2 design system handles images via 3-tier fallback in HTML. |
| `config/image_catalog.yaml` | Only useful with image_selector.py. |

### Superseded / Duplicate
| File | Why Remove |
|------|-----------|
| `pearl_news copy/` (entire directory) | Duplicate of pearl_news/ missing newer configs. |
| `config/site.yaml` | Placeholder image paths + word count (550) — absorbed by v5.2 design system and llm_expansion.yaml |
| `config/wordpress_authors.yaml` | Author rotation — handled by WORDPRESS_POST_PLAN.md |
| `config/feeds.yaml` | Only 2 feeds. Inline into run_article_pipeline.py or keep as 1 line. |
| `prompts/prewrite_runtime/` | Check if these duplicate docs/pearl_news_prompts/ prewrite files |

### Gold Standard Iterations (keep only finals)
| File | Why Remove |
|------|-----------|
| `pearl_news_gold_standard/01_commentary_maat_inequality.html` | Pre-v5.2 version |
| `pearl_news_gold_standard/02_hard_news_ahjan_climate.html` | Pre-v5.2 version |
| `pearl_news_gold_standard/03_interfaith_peace_conflict.html` | Pre-v5.2 version |
| `pearl_news_gold_standard/04_explainer_junko_mental_health.html` | Pre-v5.2 version |
| `pearl_news_gold_standard/05_youth_feature_sai_maa_education.html` | Pre-v5.2 version |
| `pearl_news_gold_standard/TEST_improved_hard_news_climate.html` | Iteration — superseded by v5 |
| `pearl_news_gold_standard/TEST_restructured_hard_news_climate.html` | Iteration v1 |
| `pearl_news_gold_standard/TEST_restructured_hard_news_climate_v2.html` | Iteration v2 |
| `pearl_news_gold_standard/TEST_v3_full_design.html` | Iteration v3 |
| `pearl_news_gold_standard/TEST_v4_un_design.html` | Iteration v4 |
| `pearl_news_gold_standard/BEFORE_AFTER_youth_paragraph.md` | Dev comparison doc |
| `pearl_news_gold_standard/DEMO_research_artifact_climate_genz.yaml` | Dev demo |
| `pearl_news_gold_standard/pearl_news_article_template.jsx` | React template — superseded by v5.2 HTML |
| `pearl_news_gold_standard/youth_signal_capture_template.yaml` | Dev template |

---

## SIMPLIFY — Keep But Trim

| File | Action |
|------|--------|
| `pipeline/quality_gates.py` | Keep as ONE validation layer. Remove article_validator.py and qc_checklist.py. |
| `pipeline/run_article_pipeline.py` | Keep but remove multi-language recursion (en-only for now). Simplify repair loops. |
| `pipeline/llm_expand.py` | Keep but remove dual HTTP fallback (just use OpenAI client). |
| `config/llm_expansion.yaml` | Keep — controls LLM expansion settings. |

---

## Summary

**What stays:** The editorial prompts, voice rules, template architecture, teacher/exercise/SDG configs, governance docs, gold standard v5.2 articles, and a lean 8-file pipeline.

**What goes:** Redundant validation layers (article_validator + qc_checklist + quality_gates.yaml + llm_safety.yaml), admin tools (teacher_onboarding, image_selector), the entire `pearl_news copy/` duplicate, superseded gold standard iterations, and loose config files absorbed by v5.2.

**Net result:** Same editorial quality, half the file count, one validation layer instead of three.
