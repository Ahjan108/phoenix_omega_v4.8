# Non-launch teacher-topic packs

Packs in this directory are **out of roster** for the current launch wave. They were authored for the launch-first topic set but do not match the live roster in `pearl_news/config/teacher_news_roster.yaml` (each teacher’s `news_topics`).

- **Purpose:** Preserve content for a future wave or roster expansion; do not treat as part of the “launch-first hard-news lane complete” deliverable.
- **Runtime:** The deterministic pack loader only loads from `teachers/`. Packs under `non_launch/` are not used by the pipeline unless explicitly promoted back into `teachers/` after roster or spec change.

## Current contents (Dev 6 roster cleanup)

| Teacher         | Topic        | Reason out of roster |
|----------------|--------------|----------------------|
| pamela_fellows | climate      | Not in pamela_fellows `news_topics` |
| pamela_fellows | economy_work | Not in pamela_fellows `news_topics` |
| omote          | climate      | Not in omote `news_topics` |
| omote          | economy_work | Not in omote `news_topics` |

Roster reference: `pearl_news/config/teacher_news_roster.yaml`.
