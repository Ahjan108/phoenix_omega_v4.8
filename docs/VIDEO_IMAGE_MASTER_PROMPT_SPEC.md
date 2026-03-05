# Video Image Master Prompt Spec

Canonical template and API flow for generating a single test image (master prompt QA). Source: [docs/flux_shnell_research.rtf](flux_shnell_research.rtf), [config/video/brand_style_tokens.yaml](../config/video/brand_style_tokens.yaml), [config/video/prompt_constraints.yaml](../config/video/prompt_constraints.yaml).

## Template structure (research file)

Three-part prompt, then negative block:

1. **Foreground (illustration)** — One sentence: style + subject + composition. Use palette `prompt_name` values from `brand_style_tokens.yaml` for the chosen topic/band (no raw hex in prompt).
2. **Background:** — One sentence: atmospheric abstract gradient, palette names, no sharp edges, ethereal.
3. **Overall lighting:** — One sentence: lighting + mood, end with `9:16, highly detailed but soft.`

Negative block: per-band `never_rules` from `brand_style_tokens.bands.<band>.never_rules` + `prompt_constraints.yaml` shared (no_adoration + shared_negatives).

## Example: anxiety, hands holding tea by window

- **Band:** cool_calm  
- **Topic:** anxiety  
- **Palette prompt_names:** slate blue grey, pale mist blue, pale mist  
- **Never rules (cool_calm):** high contrast, forced brightness, saturated accent on grief/depression  
- **Shared:** no adoration phrases + shared_negatives  

Positive prompt (template filled):

```
A soft hand-painted gouache illustration of a person's hands holding a cup of tea by a window, in slate blue grey, pale mist blue and pale mist, soft brush texture, gentle paper-like grain, centered composition, generous negative space, no faces, contemplative mood.

Background: an atmospheric abstract gradient of slate blue grey, pale mist blue and pale mist, with soft blur, no sharp edges, ethereal haze.

Overall lighting: soft diffused light from the window, quiet and undramatic, subtle volumetric haze, 9:16, highly detailed but soft.
```

Negative prompt (cool_calm never_rules + no_adoration + shared_negatives):

```
high contrast, forced brightness, saturated accent on grief/depression, no dramatic light rays from above, no figure silhouetted against bright sky, no hands reaching upward, no golden hour backlighting on figure, no divine or spiritual glow, no anime style, no full faces, no high contrast comic lines, no busy patterned background, no sharp geometric shapes, no flat vector, no sharp comic lines
```

## API: Cloudflare Workers AI FLUX

- **Endpoint:** `POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-2-dev`
- **Auth:** `Authorization: Bearer {API_TOKEN}`
- **Body:** multipart/form-data: `prompt`, `width`, `height`, optional `steps`, `guidance`, `seed`
- **9:16:** e.g. width=576 height=1024 (or 1080×1920 if supported)
- **Output:** JSON with base64 image (decode and save as PNG/JPEG for QA)

**Credentials:** Set env vars `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` (or `CLOUDFLARE_AI_API_TOKEN`). Or put them in a key file at repo root (same pattern as author cover art / TTS): `cloudflare_workers_ai.txt` or `11.txt` with lines `CLOUDFLARE_ACCOUNT_ID=...` and `CLOUDFLARE_API_TOKEN=...`. Or use a `.env` at repo root.

## Script

[scripts/video/run_flux_generate.py](../scripts/video/run_flux_generate.py) builds the prompt from config, calls the API, writes the image to `image_bank/` or `--out` path.
