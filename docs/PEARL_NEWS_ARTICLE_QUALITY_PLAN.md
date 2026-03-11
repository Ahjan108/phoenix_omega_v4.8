# Pearl News Article Quality — Gap Analysis & Remediation Plan

**Purpose:** Ensure every produced article follows our deep research, Writer Spec, chat/specs, and plans. This document analyzes what is off, what is missing, and how to fix it.

**Authority:** Complements [PEARL_NEWS_WRITER_SPEC.md](PEARL_NEWS_WRITER_SPEC.md), [DOCS_INDEX.md](DOCS_INDEX.md) § Pearl News, [continue_gen_research3.md](research/continue_gen_research3.md), and [PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md](research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md).

---

## 1. What the documentation and plans require

### 1.1 Writer Spec (PEARL_NEWS_WRITER_SPEC.md)

- **4-layer blend:** News, Youth, Teacher/Spiritual, SDG — interpenetrating, not stacked.
- **Voice:** Precision over sentiment; behavior over emotion; short sentences; no rhetorical questions; neutral but not flat.
- **Lede:** Specific (place, number, person, action); present-tense; shows gap/tension; does not announce the article.
- **Youth specificity (§7):** At least one anchor: number with source, named geography, named age band, named cohort, or concrete behavior. **Contradiction test** encouraged. Generic phrases like "Young people are increasingly affected by…" **always fail**.
- **Teacher layer:** Frame/practice/recontextualization — not validation, not devotional. No teacher names in news articles (Commentary exception). Woven in, not a separate block.
- **SDG:** Accurate (match sdg_news_topic_mapping), woven in, not a conclusion device.
- **Forward look:** Specific institution/initiative/deadline; timeframe; no hope/value conclusion.
- **Quality gates (writing layer):** Fact check traceable; youth specificity (anchors); SDG/UN accurate; no promotional tone; no UN endorsement.
- **What we never write:** Generic youth impact, validating teacher quotes, inaccurate SDG, devotional language, rhetorical questions, unsubstantiated "historic/landmark," "we," hope as conclusion.
- **Expansion prompt (§12):** Must reference the spec (lede specificity, youth §7, teacher rules, forward look, never invent facts). `expansion_system.txt` should be updated to reference specificity standard, teacher integration, forward look.

### 1.2 Deep research (continue_gen_research3.md, PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md)

- **Three layers:** Generational Psychology, Life Problems & Aspirations (with **Contradiction Audit**), Event Impact (with **Persona Switching**).
- **Outputs:** YAML in `artifacts/research/` (psychology/, pain_points/, world_events/) with provenance.
- **Concepts:** Vibration points, invisible scripts, Social Trivialization, contradiction audit, persona switching (e.g. Gen Z high-income vs Gen Alpha conflict zone).
- **Research KB:** `artifacts/research/kb/` exists (index.json, entries.jsonl) and is used by expansion when available; topics align to classifier (mental_health, climate, education, peace_conflict, economy_work, inequality, partnerships).

### 1.3 DOCS_INDEX and operational docs

- **Expansion prompt** implements Writer Spec craft rules; used with `--expand`.
- **Generational research** is a separate plane: run_research.py → artifacts/research/; optional feed ingest workflow. No automatic wiring from research runs → article pipeline.
- **Scheduled runs:** Default is **no expand** (PEARL_NEWS_EXPAND: "false") for reliability. Manual/low-volume = expand.

### 1.4 Governance and architecture

- **Editorial standards, governance page, corrections, conflict of interest** are in pearl_news/governance/ and must be published.
- **Architecture spec** is a placeholder; it does not describe how research, atoms, and expansion connect.

---

## 2. What is off — implementation vs documentation

### 2.1 Article assembler uses forbidden generic text as default

**Location:** `pearl_news/pipeline/article_assembler.py` (youth_impact slot).

When no atom exists at `atoms/youth_impact/<topic>.md`, the assembler returns:

- *"Young people are increasingly affected by global events in this area. Gen Z and Gen Alpha seek clarity and constructive responses aligned with sustainable development and well-being (SDG …)."*
- Plus two more generic paragraphs.

**Writer Spec §7 and §11:** These sentences are **explicitly forbidden** ("Generic youth impact … always fail"; "Young people are increasingly affected…"). So the **default production path** (no youth atom per topic) **outputs text that violates the spec**.

**Impact:** Without `--expand`, every article that misses a youth_impact atom is built from this placeholder. With `--expand`, the LLM is asked to improve a draft that already contains forbidden prose; behavior may improve but the starting point is wrong.

### 2.2 Quality gate “youth_impact_specificity” does not enforce specificity

**Location:** `pearl_news/pipeline/quality_gates.py`.

The gate passes if the article text contains **any** of: `"young people"`, `"gen z"`, `"gen alpha"`, `"youth"`, `"sdg"`.

**Writer Spec §7 & §10:** Specificity requires at least one **anchor**: number with source, named geography, age band, cohort, or concrete behavior. The current heuristic does **not** check for numbers, place names, or behaviors. The **forbidden generic placeholder** therefore **passes** the gate.

**Impact:** Articles that are purely generic can be marked qc_passed and published.

### 2.3 Forward look and teacher placeholders are generic

**Location:** `pearl_news/pipeline/article_assembler.py`.

- **forward_look** (and solutions/next_steps): Fixed placeholder — *"Constructive next steps and dialogue continue to shape…"* with no specific institution, deadline, or decision point. **Writer Spec §9** requires a specific forward look; this violates it.
- **teacher_quotes_practices:** When no teacher atom is found, placeholder uses *"A teacher from the United Spiritual Leaders Forum offers perspective…"* and generic reflection. **Writer Spec §6** forbids generic teacher validation; this is exactly that.

**Impact:** Non-expanded articles (and weak expansions) end with generic hope and generic teacher language.

### 2.4 Expansion prompt does not cite the Writer Spec

**Location:** `pearl_news/prompts/expansion_system.txt`.

The prompt contains solid rules (lede, youth anchors, contradiction test, teacher attribution, forward look, “what we never write”) but **does not reference** `PEARL_NEWS_WRITER_SPEC.md` or section numbers. Writer Spec §12 says the expansion prompt **must reference this spec** and that it **should be updated** to reference the specificity standard, teacher integration rules, and forward look standard.

**Impact:** Maintainers and future LLM context may not tie prompt rules to the single source of truth; drift between spec and prompt is easier.

### 2.5 Research plane is not wired into article production

**Locations:** `scripts/research/run_research.py`, `artifacts/research/`, `pearl_news/pipeline/llm_expand.py`, `pearl_news/pipeline/article_assembler.py`.

- **Deep research:** continue_gen_research3 and PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE describe a full research pipeline (psychology, pain_points, event_impact, contradiction audit, persona switching). Outputs go to `artifacts/research/<layer>/`.
- **Research KB:** Expansion uses `pearl_news.research_kb.retrieval.get_research_excerpt(topic, language)`, which reads from `artifacts/research/kb/` or falls back to hardcoded `_RESEARCH_SNIPPETS` in llm_expand.py. The KB has 15 entries (by_topic, by_cohort); it is not clearly documented that run_research.py outputs are **ingested into the KB** (e.g. via kb_append.py or a similar step). So research runs may not automatically update the excerpts expansion sees.
- **Assembler:** Does not take research or KB as input. Youth/teacher/SDG slots come only from atoms or placeholders. So **pre-article assembly** never uses deep research; only expansion (when run) gets a research excerpt.

**Impact:** Deep research exists on paper and in scripts but is not a guaranteed, documented part of the article pipeline. Many articles may be produced without any research-backed youth or teacher content.

### 2.6 Architecture spec is empty

**Location:** `docs/PEARL_NEWS_ARCHITECTURE_SPEC.md`.

The file is a short placeholder. It does not describe:

- How feeds → classifier → template → assembler → (optional) expansion → gates → output connect.
- Where research (run_research, KB) fits.
- Where Writer Spec and governance apply (assembler, expansion, gates).

**Impact:** No single architectural source of truth for “how an article is made and where each doc applies.”

### 2.7 Scheduled runs produce non–Writer-Spec-compliant drafts by default

**Location:** Docs (PEARL_NEWS_OPTION_B_RUNBOOK, PEARL_NEWS_GITHUB_SCHEDULING).

Scheduled workflow uses **no expand** by design (reliability). So the majority of automated runs produce:

- RSS summary + **generic youth placeholder** + **generic teacher placeholder** + **generic SDG paragraph** + **generic forward look**.

That combination fails Writer Spec on youth specificity, teacher layer, forward look, and “what we never write.”

**Impact:** If those drafts are ever published without human rewrite or expansion, they will not meet the documented standard.

---

## 3. What is missing — checklist

| # | Gap | Doc / plan that requires it |
|---|-----|-----------------------------|
| 1 | **No specificity check in quality gates** | Writer Spec §7, §10 — anchor (number, geography, behavior, cohort, age band). |
| 2 | **Assembler default youth text is forbidden** | Writer Spec §7, §11 — generic youth impact disallowed. |
| 3 | **Assembler forward look is generic** | Writer Spec §9 — specific institution/deadline required. |
| 4 | **Assembler teacher fallback is validating/generic** | Writer Spec §6 — no validation; distinct frame required. |
| 5 | **Expansion prompt does not cite Writer Spec** | Writer Spec §12 — expansion prompt must reference spec. |
| 6 | **No documented path from run_research → KB → expansion** | continue_gen_research3, CONTINUOUS_RESEARCH_PLAN — research should feed intelligence into articles. |
| 7 | **Assembler does not consume research/KB** | Deep research docs — article content should be informed by research. |
| 8 | **Architecture spec is placeholder** | DOCS_INDEX, scheduling docs — need one place that describes pipeline + research + spec application. |
| 9 | **GO/NO-GO does not require Writer Spec / research compliance** | Implicit — “articles are very bad” implies production should enforce spec. |
| 10 | **No per-template slot validation against Writer Spec** | Writer Spec §5 — each template has specific slot requirements (e.g. Hard News vs Youth Feature); gates don’t check template-specific rules. |

---

## 4. Remediation plan — how to do it right

### Phase A — Stop emitting forbidden content (high priority)

1. **Remove or replace generic youth placeholder in assembler**
   - **Option A (recommended):** Replace the current youth_impact placeholder with a **short, neutral stub** that states no youth-specific content was available and **does not** use the phrases “Young people are increasingly affected…” or “Gen Z and Gen Alpha seek clarity…”. E.g. *“Youth impact for this topic will be added when topic-specific research or atoms are available.”* Then rely on expansion (or manual edit) to fill from research/KB. This keeps pipeline running but avoids publishing forbidden prose.
   - **Option B:** Require a youth_impact atom or research excerpt for the topic before assembly outputs a full article; otherwise output a draft that is explicitly marked “incomplete – youth section missing” and fail or skip publish path.
   - **Owner:** pearl_news/pipeline/article_assembler.py. **Verify:** No article_*.json contains “Young people are increasingly affected by global events” from assembler.

2. **Tighten youth_impact_specificity gate**
   - Change the gate so it **fails** when the youth-related content contains **only** generic phrases (e.g. “young people are increasingly affected”, “youth around the world”, “the next generation faces”) and **passes** only when at least one of: a number with context (e.g. digits + “%”, “survey”, “report”), a named place (country/region/city), a named age band or cohort (e.g. “Gen Z”, “adolescents 12–17”), or a concrete behavior (e.g. “attend”, “drop”, “report”). Implementation can be heuristic (regex + blocklist of forbidden phrases) or call a small LLM/classifier; document in `quality_gates.py` and Writer Spec §10.
   - **Owner:** pearl_news/pipeline/quality_gates.py. **Verify:** Current generic placeholder fails; an article with one number + one place passes.

3. **Replace generic forward look and teacher placeholders**
   - **Forward look:** Replace the fixed “Constructive next steps…” block with a short stub, e.g. *“Forward look: to be completed with a specific initiative or deadline when available.”* So we never publish the current generic hope language. Expansion prompt already asks for a specific institution/deadline; ensure expansion always runs for publish path or that humans fill this.
   - **Teacher:** Replace generic “A teacher from the Forum offers perspective…” with a neutral stub that does not validate the news (e.g. *“Teacher perspective for this topic will be added when topic- and tradition-aligned content is available.”*) so that un-expanded drafts are not promotional/validating.
   - **Owner:** pearl_news/pipeline/article_assembler.py. **Verify:** No draft uses “Constructive next steps and dialogue continue” or “A teacher from the United Spiritual Leaders Forum offers perspective” as the only content in those slots.

### Phase B — Align expansion and spec (high priority)

4. **Reference Writer Spec in expansion prompt**
   - In `pearl_news/prompts/expansion_system.txt`, add at the top (or after the first paragraph) an explicit reference: e.g. *“This expansion follows [PEARL_NEWS_WRITER_SPEC.md]: §4 Lede, §5 Per-Template, §6 Teacher layer, §7 Youth specificity, §8 SDG, §9 Forward look, §11 What we never write.”* Optionally paste the one-sentence rule for lede, youth anchor, teacher, forward look. This satisfies Writer Spec §12 and reduces drift.
   - **Owner:** pearl_news/prompts/expansion_system.txt. **Verify:** Grep for PEARL_NEWS_WRITER_SPEC or §7/§9 in expansion_system.txt.

5. **Ensure expansion prompt and spec match**
   - Cross-check expansion_system.txt against Writer Spec §4–§9 and §11: lede (specific, no “In a world where”), youth (anchor + contradiction test), teacher (three distinct insights, named, no generic validation), SDG (number + title, concrete threat/advancement), forward look (specific event/deadline, no hope conclusion). Add any missing rules (e.g. “no rhetorical questions”) and remove any that conflict. Document in prompts/README.md that expansion_system.txt is the operationalization of the Writer Spec for expansion.
   - **Owner:** pearl_news/prompts/expansion_system.txt, pearl_news/prompts/README.md.

### Phase C — Wire research into the pipeline (medium priority)

6. **Document research → KB → expansion path**
   - Add a short section to CONTINUOUS_RESEARCH_PLAN.md or a new doc (e.g. PEARL_NEWS_RESEARCH_TO_ARTICLES.md): how run_research.py (or equivalent) outputs are turned into KB entries (e.g. scripts/research/kb_append.py), how get_research_excerpt maps topic/language to those entries, and how expansion uses the excerpt. Include a one-line “research run → kb_append → expansion sees it” flow.
   - **Owner:** docs/research/CONTINUOUS_RESEARCH_PLAN.md or docs/PEARL_NEWS_RESEARCH_TO_ARTICLES.md. **Verify:** A new contributor can follow the doc to run research and see it in expansion.

7. **Optionally feed research into assembler**
   - If we want **pre-expansion** drafts to already contain research-backed youth sentences (e.g. one paragraph from KB per topic), extend article_assembler to accept an optional “research excerpt” or “youth_snippet” per item (e.g. from get_research_excerpt) and inject it into the youth_impact slot when no atom exists, instead of or in addition to a stub. This requires a clear contract: excerpt is factual, cited, and non-generic. Document in architecture spec.
   - **Owner:** pearl_news/pipeline/article_assembler.py, pipeline entrypoint (run_article_pipeline.py). **Verify:** Running pipeline with research KB populated yields youth_impact content that passes the new specificity gate.

### Phase D — Governance and architecture (medium priority)

8. **Fill in Pearl News Architecture Spec**
   - In docs/PEARL_NEWS_ARCHITECTURE_SPEC.md, add: (1) Pipeline stages (ingest → classify → select template → assemble → optional expand → quality gates → output). (2) Where Writer Spec applies (assembler placeholders, expansion prompt, quality gates). (3) Where research fits (research runs → KB → expansion; optional: assembler). (4) References to PEARL_NEWS_WRITER_SPEC, `quality_gates.py`, editorial_firewall.yaml, and research docs. Keep it to 1–2 pages so DOCS_INDEX and runbooks can point to it.
   - **Owner:** docs/PEARL_NEWS_ARCHITECTURE_SPEC.md. **Verify:** DOCS_INDEX Pearl News section links to it; scheduling/runbook docs reference it.

9. **Add a “Writer Spec / research compliance” gate or checklist**
   - Either: (a) Add a GO/NO-GO or pre-publish checklist item: “All published articles are expanded or manually edited to meet Writer Spec §4–§9 and §11; no generic youth/teacher/forward look placeholders.” Or (b) Add a sixth quality gate that fails if the article body contains any of a blocklist of forbidden phrases from Writer Spec §11 (e.g. “Young people are increasingly affected”, “Now more than ever”, “In these uncertain times”) and passes only when none are present. Document in PEARL_NEWS_GO_NO_GO_CHECKLIST.md or PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md.
   - **Owner:** docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md and/or pearl_news/pipeline/quality_gates.py. **Verify:** Checklist or gate is run before publish; evidence is recorded.

### Phase E — Optional improvements (lower priority)

10. **Per-template slot checks**
    - Writer Spec §5 defines different slot requirements per template (e.g. Hard News vs Youth Feature). Consider adding template_id-aware checks (e.g. “youth feature must have a narrative opening”) as separate gates or as part of expansion validation. Document in `quality_gates.py` and Writer Spec §10.
11. **Old chat specs / “cursor” conversations**
    - You asked to ensure we follow “chat old specs conversations about writing news articles.” I did not find a single dedicated “news article writing” chat spec in the repo; the authority for article writing is PEARL_NEWS_WRITER_SPEC.md and the expansion prompt. If you have specific chat transcripts or specs (e.g. in agent-transcripts or elsewhere), add them to DOCS_INDEX under Pearl News and ensure expansion prompt or a “Pearl News writing” runbook references them so those conversations are incorporated.
12. **Regular audit**
    - Add a quarterly or pre-release audit: sample N articles from artifacts/pearl_news/drafts, check against Writer Spec §4–§9 and §11, and log failures. Use the results to tune gates and prompts.

---

## 5. Summary table

| Issue | Root cause | Fix (see section above) |
|-------|------------|---------------------------|
| Articles “very bad” | Default assembler output is generic and forbidden by spec; gates don’t enforce specificity; expansion often not run | A1–A3, B4–B5 |
| Research not in articles | Research runs and KB not documented as part of article flow; assembler doesn’t use research | C6–C7 |
| Spec not followed | Expansion prompt doesn’t cite spec; GO/NO-GO doesn’t require spec compliance | B4–B5, D9 |
| No single architecture | Architecture spec is placeholder | D8 |
| Generic placeholders pass QC | youth_impact_specificity gate only checks for keywords | A2 |

Implementing **Phase A** and **Phase B** will remove the worst mismatches (forbidden text, weak gates, spec not referenced) and set the baseline for “articles follow the Writer Spec.” **Phase C** ties in deep research explicitly. **Phase D** makes architecture and compliance visible and auditable.

---

## 6. Regular audit (Phase E12)

**Recommendation:** Quarterly or pre-release, sample N articles from `artifacts/pearl_news/drafts/`, check against Writer Spec §4–§9 and §11 (lede specificity, youth anchors, teacher integration, forward look, no forbidden phrases). Log failures and use results to tune quality gates and expansion prompt. Document runs in a short audit log (e.g. `artifacts/pearl_news/evaluation/audit_YYYY-MM.md`) or in the Evidence section of the GO/NO-GO checklist.
