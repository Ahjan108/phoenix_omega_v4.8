# Locale & Territory Strategy
## Phoenix V4 | Multi-Market Expansion

---

## IMPORTANT NOTE: CHINESE SCRIPT CLARIFICATION

Before building anything, one thing to confirm:

**Mainland China uses SIMPLIFIED Chinese (zh-CN)** — not Traditional.
**Traditional Chinese is used in Taiwan (zh-TW) and Hong Kong (zh-HK).**

If you said "Traditional Mainland Chinese," this likely means one of:
- **zh-CN (Simplified)** for Mainland China distribution
- **zh-TW (Traditional)** for Taiwan only

These are different scripts, different TTS voices, different storefronts, and different invisible scripts. They cannot be mixed. Confirm which markets you intend before building Chinese-locale atoms.

---

## ARCHITECTURE DECISION: ONE BRAND = ONE LOCALE

**Rule:** Every brand is locked to one locale and one territory. No brand spans multiple locales.

```
sleep_repair       → en-US, territory: US
sleep_repair_tw    → zh-TW, territory: TW
sleep_repair_jp    → ja-JP, territory: JP
sleep_repair_de    → de-DE, territory: DE
```

**Why:** Positioning is not translation. The invisible script for a burned-out Taiwan software engineer is different from a burned-out NYC executive — different cultural context, different search language, different hook phrasing. One brand trying to serve both will serve neither well.

---

## ROLLOUT PHASES

### Phase 1 — Taiwan (zh-TW) | 6 Pilot Brands
Months 1–3 alongside en-US Wave 1.

| Brand | zh-TW Name | Key Hook |
|---|---|---|
| `sleep_repair_tw` | 睡眠修復 | 停止嘗試入睡 |
| `stabilizer_tw` | 壓力穩定器 | 神經系統問題，不是能力問題 |
| `panic_first_aid_tw` | 恐慌急救 | 5分鐘內平息恐慌 |
| `gen_z_grounding_tw` | Z世代落地 | 社群媒體比較文化的解藥 |
| `grief_companion_tw` | 悲傷陪伴 | 悲傷需要見證者，不需要修復 |
| `inner_security_tw` | 內在安全感 | 每個關係問題都是神經系統問題 |

**Taiwan-specific invisible scripts:**
- Academic pressure (大考, 聯考) → gen_z angle
- Tech sector overwork (竹科 burnout) → stabilizer angle
- Filial duty vs personal needs → grief, identity angles
- IG/social comparison culture → gen_z, confidence angles

### Phase 2 — Japan (ja-JP) | 6 Pilot Brands
Months 4–6.

**Japan-specific framing rules:**
- NEVER say "mental health" (精神的健康) in titles — high stigma
- USE "nervous system" (神経系), "wellbeing" (ウェルビーイング), "self-care" (セルフケア)
- Politeness register (丁寧語) required throughout narration
- Karoshi (過労死) culture makes burnout brands highest-priority

### Phase 3 — Korea (ko-KR) | 4 Pilot Brands
Months 5–7.

**Korea-specific framing rules:**
- 번아웃 (burnout) is high-awareness, high-search
- 빨리빨리 culture = micro sessions (15–30 min) may outperform deep dives
- Academic/exam pressure (수능) → gen_z angle very strong
- K-beauty wellness crossover → metabolic, longevity brands have audience

### Phase 4 — European Locales | 2–3 Brands Each
Months 7–12.

| Locale | Priority Brands | Key Notes |
|---|---|---|
| `de-DE` | stabilizer_de, sleep_repair_de, adhd_anchor_de | Science framing required. Audible.de significant. |
| `fr-FR` | sleep_repair_fr, stabilizer_fr, contemplative_wisdom_fr | Philosophical framing accepted. Strong audiobook market. |
| `hu-HU` | stabilizer_hu, sleep_repair_hu | ElevenLabs only — no Google Neural2 hu-HU. Smaller market, low competition. |
| `es-US` | stabilizer_es_us, gen_z_grounding_es_us | US Hispanic market. Largest non-English US opportunity. |
| `es-ES` | stabilizer_es_es | Spain. Castilian Spanish. Separate from es-US. |

### Phase 5 — Mainland China (zh-CN) + Singapore (zh-SG)
Months 10–18. Handle separately — different distribution infrastructure.

**zh-CN specific issues:**
- Google Play NOT available in mainland China
- Findaway does NOT distribute to mainland China
- Requires local platform integrations: Ximalaya, NetEase Cloud Music, WeChat Read, Dedao
- Content review requirements differ significantly
- Build local distribution pipeline before producing zh-CN content

**zh-SG note:**
- English dominates Singapore commerce — evaluate whether en-US or zh-SG is higher ROI
- Chinese-speaking Singapore audience is smaller than assumed

---

## PERSONA MATCHING TO LOCALE

Each locale brand must reference personas tagged for that locale. Do not use en-US personas in zh-TW brands.

**Taiwan personas to define (in unified_personas.txt):**
```
anxious_insomniac_tw      - 28–45, tech sector, Taipei/Hsinchu
burned_out_professional_tw - 28–45, 竹科 worker, 996-adjacent hours
gen_z_tw                  - 18–26, IG-native, university student or early career
bereaved_adult_tw         - 30–65, filial piety context
anxious_attacher_tw       - 22–40, relationship anxiety
healthcare_worker_tw      - nurses, 偏鄉 (rural) and urban hospital
```

**Japan personas to define:**
```
anxious_insomniac_jp      - 30–50, 社畜 (salaryman culture)
burned_out_professional_jp - 28–45, karoshi-adjacent
gen_z_jp                  - 18–26, 引きこもり risk, academic pressure
```

---

## WHAT "ALL TOPICS IN A LOCALE" MEANS IN PRACTICE

The plan is **not** "one brand covers all topics in Taiwan." The plan mirrors the en-US structure:

```
en-US:  24 brands × 42 books = 1,008 US titles
zh-TW:  6 pilot brands × 7 books = 42 TW titles (Phase 1)
        → expand to 24 brands × 42 books = 1,008 TW titles (long-term)
ja-JP:  6 pilot brands × 7 books = 42 JP titles (Phase 2)
```

Each locale eventually gets its own full 24-brand catalog. Pilot phases test locale separation, storefront routing, and TTS quality before full scale.

---

## DISTRIBUTION ROUTING RULES (enforced by CI gate #49)

| Book locale | Allowed storefronts | Blocked from |
|---|---|---|
| en-US | US Google Play, US Findaway, US Apple Books | TW, JP, HK, all non-US |
| zh-TW | TW Google Play, TW Apple Books, TW Spotify | US, HK, CN |
| zh-HK | HK Google Play, HK Apple Books | US, TW, CN |
| zh-CN | Local CN platforms (Ximalaya etc.) | Google Play, Findaway, US |
| ja-JP | JP Google Play, JP Apple Books, Audible JP, Kobo JP | US |
| ko-KR | KR Google Play, KR Apple Books, Naver, Kakao | US |
| de-DE | DE Google Play, DE Findaway, Audible DE | US |
| hu-HU | HU Google Play, HU Findaway | US, must use ElevenLabs TTS |

---

## NEW CI GATE #49

**locale_territory_consistency** — runs before any distribution step.

Checks:
- locale is valid key in locale_registry.yaml
- territory matches locale's expected territory
- zh-TW not routed to US storefronts
- en-US not routed to TW/JP/etc storefronts
- hu-HU books flagged for ElevenLabs (no Google Neural2 hu-HU)
- zh-CN not submitted to Findaway or Google Play

Failure = hard block. No distribution until resolved.
