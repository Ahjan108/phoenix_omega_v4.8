# Funnel & Book Copy — Writer Spec

**Purpose:** Single source of truth for who writes what, validity rules, and where copy lives across landing pages, Proof-Loop emails, Teacher Mode author story, and headline/CTA variants. Aligns Nihala (authority/source) and copywriter (shape/test/assignable copy).

**Authority:** This spec. Implementation: `config/freebies/funnel_sections.yaml`, `funnel/burnout_reset/stories/`, `docs/email_sequences/proof_loop_sequence.md`, teacher banks (key turning point story), CTA/headline config.

**For writers new to the system:** Read **§0 System at a glance** and **§0.1 Repo and paths** first, then **§0.2 Role of each email** and **§0.3 Placeholders**. Use **§0.4 Current scope** and **§0.5 Workflow summary** when you need to know exactly which file to edit and in what order.

---

## 0. System at a glance

- **Funnel:** A reader lands on a page (e.g. "burnout reset"), enters name + email + chooses a free practice, then receives a fixed **email sequence** that ends with a book recommendation. The goal is: capture lead → give two quick "wins" (two practices) → build trust with a story → offer the book.
- **Hub:** One funnel "entry point." Each hub has its own URL (e.g. `/burnout-reset`, `/anxiety-reset`), its own hero/problem/solution/CTA copy, and its own story + book. Same structure everywhere; only the copy and topic change.
- **Proof Loop:** The conversion sequence. **1)** Reader gets the first practice (landing + Email 1). **2)** Reader gets a second, different practice (Email 2). **3)** Reader gets a short transformation story (Email 3). **4)** Reader gets the book recommendation (Email 4). **5)** Optional: "more books" (Email 5). Two micro-reliefs before any offer — that's the "proof loop."
- **Reader journey:** Visit hub page → submit form → receive Email 1 (tool link) → Email 2 (second practice link) → Email 3 (story, no pitch) → Email 4 (book) → optionally Email 5 (more books). Your copy appears on the landing (sections 1–6) and inside those emails.

---

## 0.1 Repo and paths

- All paths in this spec are **relative to the project root** (the main repo folder, e.g. `phoenix_omega`). Example: `config/freebies/funnel_sections.yaml` means that file inside the project root.
- You may **edit the YAML and Markdown files directly** (in an editor or on the repo), or **send your copy to whoever maintains the repo**; they will put it in the right key or file. If you're not sure, ask: "Where do I paste the authority paragraph?" → `config/freebies/funnel_sections.yaml` under the hub key, key `authority_narrative`.

---

## 0.2 Role of each email

| Email | When it sends | Purpose (one line) |
|-------|----------------|---------------------|
| **E1** | Right after signup | "Here's your tool" — link to the practice they chose; no story, no book pitch. |
| **E2** | +24h | Second practice (different exercise); short, mechanism-focused; no story. |
| **E3** | +72h | Transformation story (Nihala-sourced only). Builds trust; no offer yet. |
| **E4** | +48h after E3 | Book recommendation — first real offer; "why this book for you." |
| **E5** | +168h (optional) | "More books for this issue" — list of related titles (LTV). |

Do not put story content in E1 or E2; do not put the book pitch in E2 or E3. E4 is the first offer.

---

## 0.3 Placeholders (do not remove)

These tokens are **filled by the system** (exercise name, link, reader's name, etc.). **Do not delete or rewrite them.** Only change the *surrounding* prose.

| Placeholder | Used in | Meaning |
|-------------|--------|--------|
| `{{first_name}}` | Emails, subject lines | Reader's first name (from form). |
| `{{exercise_name}}` | E1, E2 | Name of the first practice they chose (e.g. Cyclic Sighing). |
| `{{tool_link}}` | E1 | URL to that practice. |
| `{{second_exercise_name}}` | E2 | Name of the second practice we send. |
| `{{second_tool_link}}` | E2 | URL to the second practice (includes tracking). |
| `{{story_body}}` | E3 | The story block (Before/Practice/After) from the story bank. |
| `{{book_title}}` | E4, E5 | Title of the recommended book. |
| `{{book_link}}` | E4 | URL to the book (our site, then redirect). |
| `{{more_books}}` | E5 | List of additional books (titles + links). |
| `{{unsubscribe_url}}` | All emails | Link to unsubscribe (compliance). |
| `{{base_url}}` | Email templates | Site base URL. |

If you see `{{...}}` in a template, assume it's system-filled and leave it as-is.

---

## 0.4 Current scope (hubs, topics, personas)

- **Hubs (template families):** `burnout_reset`, `anxiety_reset`. More may be added (e.g. `sleep_reset`, `overthinking_reset`). Each hub has its own block in `funnel_sections.yaml` and its own `story_id` + `book_slug` in `funnel_proof_loop.yaml`.
- **Topics:** `burnout`, `anxiety` (aligned to hubs). Used for story bank filename (`burnout.md`, `anxiety.md`) and book mapping.
- **Personas (form "I work as…"):** `unknown`, `professional`, `healthcare`, `first_responder`, `entrepreneur`, `corporate_manager`, `working_parent`, `other`. Used for segmentation and GHL; persona-specific copy variants can be added where config supports it.

When you're asked to "write for all hubs/topics/personas," you're covering these lists (and any new ones added to config).

---

## 0.5 Workflow summary (step-by-step)

| Asset | Step 1 | Step 2 | Step 3 | Where it's put |
|-------|--------|--------|--------|----------------|
| **Authority narrative** | Nihala drafts paragraph | Copywriter one light edit (clarity, rhythm) | Paste into config | `config/freebies/funnel_sections.yaml` → under hub (e.g. `burnout_reset`) → key `authority_narrative` (see format below). |
| **Email 3 story** | Nihala provides raw (profession, moment, change) | Copywriter shapes to Before/Practice/After, 120–150 words | Nihala approves | `funnel/burnout_reset/stories/<topic>.md` — add or edit a `## story_id` block; ensure `story_id` matches `funnel_proof_loop.yaml`. |
| **Headline / CTA** | Copywriter proposes variants (incl. teaching-language) | Test if needed; Nihala approves | Paste into config | `config/freebies/funnel_sections.yaml` → per hub → `hero_headline`, `hero_subhead`, `cta`. |
| **Problem / Solution / E1 / E2 / E4** | Copywriter drafts per hub or topic | Approval per process | Update doc + templates | `docs/email_sequences/proof_loop_sequence.md` (canonical); funnel `emails/*.html` and/or `funnel_sections.yaml` per hub. |
| **Key turning point (Teacher Mode)** | Book author provides raw story with teacher | Copywriter shapes; author highlights teacher | Editor/author approve | Teacher bank `approved_atoms/` for that teacher; see `specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`. |

---

## 1. Authority narrative (Section 2, landing page)

### What it is

The **single highest-leverage block of copy on the funnel page.** It sits between Hero and Problem (Section 2). It establishes *who this is from* and *why they can be trusted* — in **Nihala's voice**, drawing from **her actual arc**, not a brand voice or a generic expert.

### Who writes it

- **Author:** Nihala only. No copywriter can source this; it must come from her lived experience and positioning.
- **Edit:** One **light copyedit pass** by a copywriter for clarity and rhythm only. No substantive change to meaning or voice.

### Where it lives

- **Config:** `config/freebies/funnel_sections.yaml` → per hub (e.g. `burnout_reset`) → `authority_narrative`.
- **Template:** `funnel/burnout_reset/templates/burnout_reset.html` Section 2: `sections.authority_narrative` (with placeholder comment for Nihala's paragraph).

### Format (exact)

In `funnel_sections.yaml`, under the hub key, add or edit a single string. Example:

```yaml
burnout_reset:
  hero_headline: "Reset your nervous system in 60 seconds"
  hero_subhead: "One breath. No sign-up walls. Use it when you need it."
  authority_narrative: "Your paragraph here. Second sentence. Third. Keep Nihala's voice."
  problem: "Burnout doesn't fix itself with more rest..."
```

The value is one string (one paragraph). No markdown or bullets in the YAML value unless the template renders it.

### Validity

- One paragraph (target length TBD by Nihala; suggest 3–5 sentences).
- First person or close third acceptable; must feel like *her*, not "the brand."
- No generic expert claims; anchor in specific turning points, training, or client work if she chooses.
- Copywriter does **not** draft from scratch; only edits what Nihala provides.

---

## 2. Email 3 — Transformation story (story bank)

### What it is

The **Proof-Loop story** (Email 3): a real or **composite** experience from Nihala's actual work with people. It shows *this practice, in a specific situation, led to a specific change.* It builds trust before the book offer.

### Who writes it

- **Source / raw material:** Nihala. She provides the situation (profession, moment, what changed). She may provide a rough draft.
- **Shape / polish:** Copywriter can tighten, clarify, and fit the **validity spec** below. Copywriter **cannot** invent the situation or the outcome; they can only shape what Nihala sources.

### Where it lives

- **Story bank:** `funnel/burnout_reset/stories/<topic>.md` (e.g. `burnout.md`, `anxiety.md`). Each story block has a heading (e.g. `## burnout_nurse_story`) and is referenced by `story_id` in `config/freebies/funnel_proof_loop.yaml`.
- **Constraint list** stays in the story file so every author (Nihala or copywriter) writes against the same rules.

### Format (exact)

Each story file can have multiple stories. One story = one `## story_id` block. The **story_id** (e.g. `burnout_nurse_story`) must match the `story_id` in `config/freebies/funnel_proof_loop.yaml` for that hub. Structure:

```markdown
# Burnout — transformation story (Email 3)

**Constraint list for authors:** Specific profession, specific moment (time/place), specific physical
detail in practice moment, specific measurable change in after. No fill-in template; write against
these constraints. 120–150 words. Nihala approves before use.

*Stories represent composite experiences from readers and practitioners.*

---

## burnout_nurse_story

**Before:** She had been running on three years of night shifts, the kind where your body stops
asking for sleep and just runs on cortisol until the crash.

**Practice:** She tried the cyclic sigh at the nurses' station between rounds — two inhales through
the nose, one long exhale through the mouth. The first time she felt her shoulders drop she didn't
trust it.

**After:** Within a week she was using it before handoff. Her resting heart rate dropped eight
points. She didn't quit; she didn't have to. She'd found a lever.
```

**Example to open:** `funnel/burnout_reset/stories/burnout.md` in the repo for the full example. The system pulls the body of the `## story_id` block into Email 3; the **Before / Practice / After** labels can be used in the file for structure, and the rendered email may use just the paragraph text. Total word count for the story block (Before + Practice + After): **120–150 words**.

### Validity spec (tight)

| Requirement | Rule |
|-------------|------|
| **Profession** | Specific (e.g. nurse, teacher, founder). No "someone" or "a professional." |
| **Moment** | Specific time/place or situation (e.g. "at the nurses' station between rounds," "before handoff"). |
| **Practice** | One sentence with a **physical detail** (e.g. "two inhales through the nose, one long exhale"; "felt her shoulders drop"). |
| **After** | One sentence with **specific, measurable or observable change** (e.g. "resting heart rate dropped eight points"; "using it before handoff within a week"). |
| **Length** | **120–150 words** for the story block (Before / Practice / After). |
| **Composite** | Composites are allowed. Add disclaimer in the file: *Stories represent composite experiences from readers and practitioners.* Nihala approves before use. |

Copywriter may **not** invent profession, moment, or outcome. If Nihala provides "a nurse, between rounds, heart rate dropped," copywriter can turn that into clear, on-spec prose; they cannot substitute "a CEO in a meeting" or a different result.

---

## 3. Key turning point — Author story (Teacher Mode)

### Teacher Mode in plain language

**Teacher Mode** = books built around a **real teacher's teachings** (a real person's method or lineage). The pipeline does not invent the teacher; it **assembles** content from that teacher's approved material. The **key turning point story** is the **book author's** own story (e.g. Nihala's) about the moment or arc when **they** were changed by **that teacher's** work — so the **author** is the narrator, and the **teacher** is the one being credited and highlighted. Where it goes: in the **teacher's content bank**, in **approved story atoms** for that teacher. Exact steps: see **`specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`** (onboard teacher, plan book, fill gaps, approve atoms).

### What it is

In **Teacher Mode** books, the **book author's** own key turning point story about **meeting the teacher's teachings** — i.e. the moment or arc when the author's life or practice changed because of this teacher. The **author** is the one telling the story; the **teacher** is the one being highlighted.

### Who writes it

- **Book author** (e.g. Nihala when she is the author of the Teacher Mode book) provides the raw story: her turning point with this teacher's work.
- **Copywriter** can shape for clarity and fit into the book's narrative; cannot invent the relationship or the turning point.
- For Teacher Mode, the **author** is always the narrator; the **teacher** is the figure being credited and highlighted in the story.

### Where it lives

- **Teacher bank** for that teacher: under `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/` (or the path your team uses for teacher-scoped content). The "author story" or "key turning point" slot is defined in the Teacher Mode structural spec; the playbook describes how to add and approve atoms. See **`specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`** — sections on onboarding a teacher, planning a Teacher Mode book, and filling gaps (approved_atoms, doctrine). Use **book author** as the voice; for Teacher Mode, **author highlights teacher** in that story.

### Validity

- One clear turning point (or short arc): before the teacher's influence → encounter with the teachings → after.
- Author's voice; no ghostwritten "expert" tone.
- Teacher is named and their contribution is clear; the story is still the *author's* story, not a bio of the teacher.

---

## 4. Headline and A/B variants

### What it is

Hero headline (and optionally subhead) for funnel hubs and related surfaces. The spec may offer **three (or more) options**; none are assumed tested against **Nihala's actual audience voice** or her teaching language. The goal is to pressure-test which framing converts for spiritual/therapeutic audiences.

### Who owns it

- **Copywriter** with experience in **spiritual / therapeutic / self-help** audiences runs the pressure-test: e.g. "For People Who Give Too Much" vs. something closer to **Nihala's teaching language** (e.g. nervous-system, burnout, rest, boundaries as she actually talks about them).
- **Nihala** approves final variants and the teaching-language version; she may supply preferred phrases or a short brief.

### Where it lives

- **Config:** `config/freebies/funnel_sections.yaml` → per hub → `hero_headline`, `hero_subhead`. A/B variants can be stored as `hero_headline_variants` (list) and selected by test or rotation logic.
- **Spec:** Document the **current variants** and the **testing protocol** (e.g. which variant is control, what "Nihala's teaching language" means in 2–3 example headlines).

### Validity

- At least one variant must be grounded in **Nihala's teaching language** (not only generic self-help).
- Copywriter's job: propose alternatives, run or support A/B test design, and document what "lands" for the audience. Final choice: Nihala or product/marketing lead with her input.

### Current variants and test protocol

- **Document in this spec (or in `funnel_sections.yaml` comments)** the **three (or more) headline options** currently in play, e.g.:
  - Option A: "For People Who Give Too Much" (or whatever is live).
  - Option B: Teaching-language variant (e.g. "When Your Nervous System Won't Turn Off").
  - Option C: Benefit-led or other variant.
- **Pressure-test:** A copywriter who understands spiritual/therapeutic audiences should evaluate whether the generic option (e.g. "For People Who Give Too Much") actually lands, or whether a headline closer to Nihala's teaching language converts better. Test protocol: define control, variant(s), metric (e.g. submit rate), and sample size; run and document before locking a winner.

---

## 5. Assignable copy (all template families, topics, personas)

### What it is

Everything else that can be **fully assigned to a copywriter** (with briefs and approval, but not Nihala-only sourcing):

- **Burnout (and other topic) explanation** — Problem/Solution block on landing (e.g. `funnel_sections.yaml` → `problem`, `solution`).
- **Email 1** — Immediate "your tool is here" body and subject (see `docs/email_sequences/proof_loop_sequence.md`). Placeholders only; no Nihala-sourced story.
- **Email 2** — Second-practice, science/mechanism content (short; no story). Copywriter drafts; can use approved science one-liners from repo.
- **Email 4** — Book recommendation copy (why this book, for this reader). Copywriter drafts per book/topic; Nihala or editor approves.
- **CTA button text** — e.g. "Yes — I'm ready to start" and alternatives. Lives in `funnel_sections.yaml` → `cta` and in any CTA template config (e.g. `cta_templates.yaml`).

### Scope

- **Template families:** All funnel hubs (e.g. burnout_reset, anxiety_reset) and any future hub templates.
- **Book topics:** All topics in `funnel_proof_loop.yaml` / catalog (burnout, anxiety, etc.).
- **Personas:** All personas used in funnel or book targeting (e.g. professional, healthcare, first_responder); persona-specific variants where config supports it.

### Where it lives

| Copy type | Primary location | Notes |
|-----------|------------------|--------|
| Problem / Solution | `config/freebies/funnel_sections.yaml` (per hub) | Optional: pull from marketing/consumer_language later. |
| Email 1–2–4 body/subject | `docs/email_sequences/proof_loop_sequence.md`; funnel `emails/*.html` | Canonical copy in doc; templates in repo. |
| Email 2 science | Same + optional `config/freebies/` or `audio_scripts` | Short, mechanism-focused; no story. |
| Book rec (Email 4) | Per-book or per-topic; can live in `freebie_to_book_map` or a book_copy layer | Copywriter drafts; approval per book/topic. |
| CTA button | `config/freebies/funnel_sections.yaml` → `cta`; `cta_templates.yaml` if used | One default per hub; variants if A/B. |

### Validity

- **Consistent voice** with the rest of the funnel (and with Nihala's authority narrative once set).
- **No invented stories or outcomes** in Email 1, 2, or 4 — only in Email 3 (and there only from Nihala-sourced material).
- **Placeholders** in templates (`{{exercise_name}}`, `{{book_title}}`, etc.) must remain; copywriter fills the *surrounding* prose and any default strings in config.

---

## 6. Summary — Who writes what

| Asset | Primary writer | Copywriter role | Approval |
|-------|----------------|------------------|----------|
| Authority narrative (Section 2) | Nihala | One light edit (clarity, rhythm) | Nihala |
| Email 3 story | Nihala (source/raw) | Shape to validity spec; no new sourcing | Nihala |
| Key turning point (Teacher Mode) | Book author (e.g. Nihala) | Shape; author highlights teacher | Author + editor |
| Headline A/B variants | Copywriter (propose + test) | Propose Nihala-teaching-language variant; run test | Nihala / lead |
| Problem, Solution, Email 1/2/4, CTA | Copywriter | Full draft for all families/topics/personas | Per process |

---

## 7. References

- **Funnel / Proof Loop:** `docs/email_sequences/proof_loop_sequence.md`, `funnel/burnout_reset/`, `config/freebies/funnel_sections.yaml`, `config/freebies/funnel_proof_loop.yaml`.
- **Story bank:** `funnel/burnout_reset/stories/*.md`; constraint list in each file. **Example to open:** `funnel/burnout_reset/stories/burnout.md`.
- **Landing copy (per hub):** `config/freebies/funnel_sections.yaml` — **Example to open** for hero, problem, solution, CTA, authority_narrative.
- **Teacher Mode:** `specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`, teacher banks, `approved_atoms/`, doctrine.
- **Freebie system:** `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md`, `config/freebies/`.

---

## 8. Quick reference — key files (all paths from project root)

| What you're editing | File path |
|--------------------|-----------|
| Authority narrative, hero, problem, solution, CTA (per hub) | `config/freebies/funnel_sections.yaml` |
| Email 3 story (per topic) | `funnel/burnout_reset/stories/burnout.md`, `anxiety.md`, etc. |
| Canonical email copy (E1–E5 body/subject) | `docs/email_sequences/proof_loop_sequence.md` |
| Which story_id and book per hub | `config/freebies/funnel_proof_loop.yaml` |
| Teacher Mode author story / key turning point | Teacher bank `approved_atoms/`; process in `specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md` |
