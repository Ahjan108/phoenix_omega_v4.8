# Teacher-topic overlays (explainer & youth-feature)

Overlays are **deep-merged** onto the base teacher-topic pack when `template_id` is `explainer_context` or `youth_feature`. They add or override only type-specific slots; they must not remove identity, persona, or topic_fit.

- **Schema and slot mapping:** [PEARL_NEWS_EXPLAINER_YOUTH_FEATURE_OVERLAY_SPEC.md](../../../docs/PEARL_NEWS_EXPLAINER_YOUTH_FEATURE_OVERLAY_SPEC.md) (Dev 10)
- **Explainer overlays:** `explainer_context/<teacher_id>__<topic>.yaml`
- **Youth-feature overlays:** `youth_feature/<teacher_id>__<topic>.yaml`

Not live until hard news is proven (Wave 2). Loaded by `load_teacher_topic_pack(repo_root, teacher_id, topic, template_id)` when `template_id` is set.
