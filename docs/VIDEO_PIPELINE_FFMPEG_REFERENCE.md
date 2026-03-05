# Video Pipeline — FFmpeg filter and encoding reference

**Purpose:** Filter chain and encoding reference for `run_render.py`. All variation is **render-time only** (no separate mutation stage).  
**Related:** [VIDEO_PIPELINE_SPEC.md](./VIDEO_PIPELINE_SPEC.md) §11 Renderer parameters; `config/video/color_grade_presets.yaml`.

---

## 1. Single-pass filter chain (overview)

One FFmpeg invocation per output video. Order: scale → crop (framing) → zoompan (motion) → eq (per-video color grade) → format → optional drawtext/drawbox for captions.

- **Framing:** `crop` with `crop_zoom`, `crop_offset_x`, `crop_offset_y` (deterministic from `hash(video_id + shot_index)`).
- **Motion:** `zoompan` — `z` and `d` from timeline clip (static, slow_zoom_in, slow_zoom_out).
- **Color:** `eq` — one preset per video from `config/video/color_grade_presets.yaml`.
- **Captions:** `drawtext` (and optionally `drawbox` for safe zone) after eq.

---

## 2. Crop and framing (zoompan input)

Use crop to apply per-clip framing variation before zoompan:

```text
crop=iw*{crop_zoom}:ih*{crop_zoom}:{crop_offset_x}:{crop_offset_y}
```

- **crop_zoom:** e.g. 0.92–1.0 (slightly zoomed = cropped). Derived deterministically from `seed = hash(video_id + shot_index)`.
- **crop_offset_x, crop_offset_y:** Anchor point in source (pixels). Also derived from same seed so builds are reproducible.

Input to crop should be the image scaled to at least the output size (or larger) so the crop region is valid. Typical: scale to a fixed size (e.g. 1200×2133 for 9:16), then crop, then feed to zoompan.

---

## 3. zoompan (motion)

```text
zoompan=z='...':d={frames}:s={width}x{height}
```

- **d:** Number of output frames for this clip (from timeline: `duration_s * fps`).
- **s:** Output size (e.g. `1080x1920` for 9:16).

**z expressions (deterministic per clip):**

- **Static:** `z='1'` (no zoom change).
- **Slow zoom in:** `z='min(zoom+0.0004,1.08)'` (or similar; zoom starts at 1, increases per frame).
- **Slow zoom out:** `z='max(zoom-0.0003,0.92)'`.

Use the timeline clip’s `motion_type` (or equivalent) to choose the expression. Same motion types as in `config/video/motion_policy.yaml` (static majority; slow_zoom / slow_pan).

For pan (if added later): `x`/`y` in zoompan can use expressions like `x='iw/2-(iw/zoom/2)+offset'` with a small deterministic offset.

---

## 4. eq (per-video color grade)

One grade per video (not per shot). Apply after all clips are composed or as the last filter before encoding when rendering a single image per clip then concat.

```text
eq=contrast={c}:brightness={b}:saturation={s}
```

Values from `config/video/color_grade_presets.yaml`:

| Preset  | contrast | brightness | saturation |
|---------|----------|------------|------------|
| neutral | 1.0      | 0.0        | 1.0        |
| warm    | 1.03     | 0.01       | 1.05       |
| cool    | 1.0      | -0.01      | 0.92       |
| sunset  | 1.02     | 0.02       | 1.08       |
| soft    | 0.98     | 0.005      | 0.95       |

Select preset by emotional arc or content_type (see spec §11).

---

## 5. drawtext (captions)

```text
drawtext=fontfile={font_path}:text='{escaped_text}':fontsize={size}:fontcolor=white:x={x}:y={y}:line_spacing=8:shadowcolor=black:shadowx=2:shadowy=2
```

- **x, y:** From caption adapter output (per-format placement). Examples: bottom center `x=(w-text_w)/2`, `y=h*0.82`; top center `y=h*0.12`.
- Escape single quotes in text (e.g. `\'` or use a drawtext-safe escaping helper).
- **line_spacing:** Optional; adjust for multi-line captions.

Caption content and placement come from the pipeline (CaptionAdapter + timeline); the renderer only applies them via drawtext.

---

## 6. drawbox (caption safe zone, optional)

To avoid text over critical content, draw a semi-transparent box or use a “safe zone” to constrain caption placement. Example:

```text
drawbox=x=0:y=h*0.75:w=iw:h=h*0.25:color=black@0.3:t=fill
```

Use only if the pipeline defines a caption safe zone (e.g. `caption_safe_zone` in asset metadata or layout). Prefer positioning captions within the safe region via drawtext x/y rather than drawing a visible box unless required for compliance.

---

## 7. Encoding

- **Video:** `-c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p`
- **Do not use** `-preset ultrafast` for production (caption/text edges degrade).
- **Framerate:** From timeline `fps` (e.g. 30).
- **Duration:** From timeline clip duration or total timeline duration.

---

## 8. Example (single image clip, 9:16)

```bash
ffmpeg -y -loop 1 -i input.jpg \
  -filter_complex "
    scale=1200:2133,
    crop=iw*0.96:ih*0.96:24:40,
    zoompan=z='1':d=90:s=1080x1920,
    eq=contrast=1.03:brightness=0.01:saturation=1.05,
    format=yuv420p
  " \
  -t 3 -r 30 -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p \
  out.mp4
```

For multiple clips: render each clip to a segment (or use concat demuxer), then concat segments. Apply the **eq** preset once per video (e.g. on the concatenated stream or by applying the same eq in each segment for consistency).

---

## 9. Deterministic parameters (summary)

| Parameter set   | Source |
|----------------|--------|
| crop_zoom, crop_offset_x, crop_offset_y | `seed = hash(video_id + shot_index)`; map to ranges (e.g. zoom 0.92–1.0, offsets within margin). |
| zoompan z expression | Timeline clip `motion_type` (static / slow_zoom_in / slow_zoom_out). |
| eq (c, b, s)   | `config/video/color_grade_presets.yaml`; preset chosen by emotional_arc or content_type. |
| drawtext x, y  | CaptionAdapter + aspect-ratio preset (e.g. `config/video/aspect_ratio_presets.yaml`). |

This keeps builds reproducible and avoids a separate mutation stage; all variation is applied at render time in `run_render.py`.
