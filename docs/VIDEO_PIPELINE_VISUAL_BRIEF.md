# Video pipeline: visual brief for image bank generation

**Purpose:** Target visuals for hook types and therapeutic content. Use when generating or commissioning image bank assets. Pipeline implementation (visual_intent, motion, caption rules) is in config and VIDEO_PIPELINE_SPEC; this doc is **reference only** for prompt/composition targets.

**Rule:** Hook must be **emotionally legible in &lt;0.5 seconds**. Simple, emotional, clear silhouette, strong contrast. Avoid: complex scenes, multiple characters, wide busy environments.

---

## Hook types (high-retention for Gen Z/Alpha therapeutic shorts)

| Hook type | What viewers see | Pipeline mapping | Motion (renderer) |
|-----------|------------------|------------------|------------------|
| **light_reveal** | Dark/muted frame, light slowly appears | HOOK_VISUAL, warm_window | slow_zoom_in |
| **hands_closeup** | Body detail (hands), no face | CHARACTER_EMOTION, macro, face_visibility none | slow_zoom_in |
| **walking_path** | Path receding into distance | ENVIRONMENT_ATMOSPHERE | slow_zoom_in (forward illusion) |
| **macro_symbol** | Single object: candle, ripple, door, phone, chair | SYMBOLIC_METAPHOR | static or slow_zoom |
| **window_reflection** | Inside/outside, reflection, rain/fog, soft light | HOOK_VISUAL or SYMBOLIC_METAPHOR | static or slow_zoom |
| **big_question** | Large question text, minimal background | INSTRUCTION_BACKGROUND | static |
| **ripple_visual** | Water, breathing, calm expansion | SYMBOLIC_METAPHOR | slow_zoom_out |

Distribution and batch caps: `config/video/hook_selection_rules.yaml` (hook_types, daily_batch_max_share_per_hook).

---

## Composition targets (image bank)

- **Subject count:** ≤ 2 per image; low background detail; negative space required.
- **Faces:** Default partial_or_none — back of head, profile, silhouette, hands. No “person staring at camera.”
- **Caption-safe:** Assets should have a low-detail zone (e.g. bottom 25%) for caption overlay; tag `caption_safe_zone` in image bank schema.
- **Lighting:** Consistent lighting families per video (warm_window, overcast_soft, sunset_warm); avoid mixing color temperature and shadow direction across consecutive shots.
- **Aesthetic:** Contemplative, layered natural environments, soft atmospheric light, hand-painted feeling. No copyrighted studio or brand names in prompts.

---

## Emotion → visual alignment

- Overwhelmed → high angle, small character, constrained frame.
- Relief → eye-level, open environment, calm light.
- Reflection → window, rain/fog, interior–exterior duality.

Use `config/video/emotion_to_camera_overrides.yaml` and visual_intent per segment.

---

## Reference images

When building the bank, use concrete references for: hands (clenched = stress, wrapped around mug = comfort, open palms = relief), window light, paths, single symbolic objects, window reflection with rain/fog, calm water/ripple. Store reference images by hook type and archetype (e.g. under `docs/visual_references/` or in the asset brief) so prompt compiler and human reviewers have a clear target. Do not embed implementation or motion specs here — those stay in config and spec.
