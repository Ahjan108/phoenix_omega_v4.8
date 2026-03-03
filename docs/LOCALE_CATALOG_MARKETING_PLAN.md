# 100% Locale Catalog Marketing Plan

**Purpose:** Comprehensive, actionable plan for Phoenix V4 multi-locale audiobook expansion. Defines catalog scope per locale, marketing positioning across all twelve markets, distribution requirements, and locale-specific go-live readiness criteria.

**Audience:** Ops, marketing, content, distribution, and localization teams.

**Authority:** Extends [TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) (US title philosophy) and [locale_strategy.md](../del_location_plan/locale_strategy.md) (rollout phases). References [locale_registry.yaml](../config/localization/locale_registry.yaml) (technical definitions) and [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) (invisible script research).

**Last updated:** 2026-03-03

**Status:** Complete plan for all 12 locales (en-US, zh-CN, zh-TW, zh-HK, zh-SG, ja-JP, ko-KR, es-US, es-ES, fr-FR, de-DE, hu-HU).

---

## 1. All-Locale Catalog Scope Definition

### What "100% Catalog" Means Per Locale

A locale achieves 100% catalog status when:

1. **Content completeness:** All 24 brands × 42 books = 1,008 titles localized and atom-ready for that locale.
2. **Atoms fully populated:** Every (persona, topic) pair in the locale's persona set has a complete atom pool, validated to 100% coverage across all templates.
3. **Distribution infrastructure live:** Storefront accounts created, metadata schema validated for the locale, ISBNs/ASINs assigned, first content batch approved on primary platform.
4. **Marketing validated:** Invisible scripts researched and approved by native speakers; title testing completed; platform-specific keyword positioning confirmed.
5. **CI gates passing:** locale_territory_consistency (gate #49) passes for all books; no blocking distribution or metadata issues.
6. **Launch wave deployed:** Pilot 6-brand wave launched; native speaker feedback collected; readiness for full scale confirmed.

This is not merely a YAML entry in locale_registry.yaml — it is a full operational state.

### Catalog Size Progression by Phase

| Locale | Phase | Timeline | Pilot Books | Full Catalog | Brands |
|--------|-------|----------|-------------|--------------|--------|
| **en-US** | 1 (Active) | Ongoing | 50–75 (Seed Wave in progress) | 1,008 | 24 |
| **zh-TW** | 1 | Mo 1–3 | 42 (6 brands × 7 books) | 1,008 (long-term) | 6 → 24 |
| **ja-JP** | 2 | Mo 4–6 | 42 (6 brands × 7 books) | 1,008 (long-term) | 6 → 24 |
| **ko-KR** | 3 | Mo 5–7 | 28 (4 brands × 7 books) | 1,008 (long-term) | 4 → 24 |
| **de-DE** | 4 | Mo 7–12 | 21 (3 brands × 7 books) | 1,008 (long-term) | 3 → 24 |
| **fr-FR** | 4 | Mo 7–12 | 14 (2 brands × 7 books) | 1,008 (long-term) | 2 → 24 |
| **hu-HU** | 4 | Mo 7–12 | 14 (2 brands × 7 books) | 1,008 (long-term) | 2 → 24 |
| **es-US** | 4 | Mo 7–12 | 21 (3 brands × 7 books) | 1,008 (long-term) | 3 → 24 |
| **es-ES** | 4 | Mo 7–12 | 14 (2 brands × 7 books) | 1,008 (long-term) | 2 → 24 |
| **zh-HK** | 2–3 | Mo 6–9 | 28 (4 brands × 7 books) | 1,008 (long-term) | 4 → 24 |
| **zh-CN** | 5 | Mo 10–18 | 42 (6 brands × 7 books) | 1,008 (long-term) | 6 → 24 |
| **zh-SG** | 5 | Mo 12–18 | 14 (2 brands × 7 books) | 1,008 (long-term) | 2 → 24 |

**Key principle:** Expansion is phased, not all-at-once. Each phase validates locale separation, TTS quality, invisible script fit, and distribution routing before scaling to full 1,008.

---

## 2. Marketing Positioning Per Locale

This section defines the marketing strategy and "invisible script" — the hidden belief that makes a title resonate — for each of the twelve locales. Each locale has a different cultural context, search language, and positioning angle.

### en-US: The Baseline Market

**Invisible script:** *"I'm stuck in productivity-based identity. The nervous system is the missing key to lasting change."*

**Consumer language:** Burnout, anxiety, sleep, relationships, self-worth, nervous system, somatic, breathwork.

**High-value search keywords:**
- "nervous system reset" / "vagus nerve exercises"
- "anxiety without anxiety disorder" / "manage panic attacks at home"
- "sleep deprivation recovery" / "insomnia natural remedies"
- "burnout recovery" / "work-life balance"
- "relationship anxiety" / "attachment styles"

**Title philosophy:** Owns a search keyword; names the invisible script precisely; brand voice carries imprint (Calm vs Edge vs Rise vs Root). City-specific titles include locale when pinned (NYC, LA, SF/Bay/Silicon Valley, Chicago, Boston, DC). No generic "for Readers" or "How to Feel Better" placeholders.

**Platform-specific positioning:**
- **Spotify:** Sleep, focus, wellness, "winding down"
- **Apple Books:** Mental health, nervous system, self-improvement
- **Audible:** Deep dives, narrative, premium positioning
- **Google Play:** Accessibility, free/affordable entry, broad categories

**Atoms library:** Fully populated (100% coverage across 24 brands, 42 topics per brand, 10 personas per topic).

**Current status:** Seed Wave in progress (50–75 titles, Phoenix Drop template), full 1,008 title-gen pending atoms completion.

---

### zh-TW (Traditional Chinese): Taiwan Market

**Invisible script:** *"我不是無能，我的神經系統過度警覺。" ("I'm not incapable; my nervous system is hypervigilant.")*

**Cultural context:**
- Tech sector burnout (竹科 workers, 996-like hours, semiconductor industry stress)
- Academic pressure legacy (聯考, 大考 culture remains in Gen Z)
- Filial piety vs personal autonomy (孝順與自我需求的衝突)
- Social media comparison culture (Instagram/Dcard, gen_z angle)
- Healthcare worker shortages (rural 偏鄉 distribution challenges)

**High-value search keywords (in Traditional Chinese):**
- "睡眠修復" / "失眠自然療法" (sleep repair, insomnia natural remedy)
- "工作倦怠" / "職業倦怠恢復" (work burnout, burnout recovery)
- "焦慮管理" / "恐慌發作" (anxiety management, panic attacks)
- "神經系統調理" / "迷走神經" (nervous system regulation, vagus nerve)
- "人際關係焦慮" / "依附關係" (relationship anxiety, attachment)

**Title philosophy notes:**
- Avoid clinical language (精神健康, 心理治療). Use "神經系統" (nervous system), "自我照顧" (self-care), "身心調和" (mind-body harmony).
- Tech sector positioning (竹科, overwork) resonates strongly in titles.
- Filial piety angle works for grief, identity, boundary-setting brands.
- Gen Z angle: social media pressure, comparison anxiety.
- Avoid "meditation" as primary hook (too spiritual/niche); use "nervous system" reframe.

**Platform-specific positioning:**
- **Spotify TW:** Sleep, focus, wellness
- **Apple Books TW:** Self-development, nervous system, modern wellness
- **Google Play TW:** Accessibility, affordable entry
- **Findaway TW:** Distribution to independent retailers

**Persona set (to be defined in LOCALE_PERSONAS.md):**
- `anxious_insomniac_tw` — 28–45, tech sector, Taipei/Hsinchu, sleepless due to overwork
- `burned_out_professional_tw` — 28–45, 竹科 worker, 996-adjacent hours
- `gen_z_tw` — 18–26, IG-native, university student or early career, comparison anxiety
- `bereaved_adult_tw` — 30–65, filial piety context, grief and family duty
- `anxious_attacher_tw` — 22–40, relationship anxiety, modern dating
- `healthcare_worker_tw` — nurses and doctors, 偏鄉 (rural) and urban hospital burnout

**Phase 1 pilot brands (6 brands × 7 books = 42 titles):**
- `sleep_repair_tw` — hook: 停止嘗試入睡 (stop trying to fall asleep)
- `stabilizer_tw` — hook: 神經系統問題，不是能力問題 (nervous system issue, not capability issue)
- `panic_first_aid_tw` — hook: 5分鐘內平息恐慌 (calm panic in 5 minutes)
- `gen_z_grounding_tw` — hook: 社群媒體比較文化的解藥 (antidote to social comparison)
- `grief_companion_tw` — hook: 悲傷需要見證者，不需要修復 (grief needs witness, not fix)
- `inner_security_tw` — hook: 每個關係問題都是神經系統問題 (every relationship issue is nervous system)

**TTS voice:** ElevenLabs (zh-TW) or Google Neural2 (cmn-TW-Wavenet-A). Validate naturalness and emotional tone.

**Go-live timeline:** Months 1–3 alongside en-US Wave 1.

---

### zh-HK (Traditional Chinese): Hong Kong Market

**Invisible script:** *"我的焦慮不是性格缺陷；這是我的神經系統在過度警覺。" ("My anxiety isn't a character flaw; my nervous system is hypervigilant.")*

**Cultural context:**
- Political/social anxiety context (different from Taiwan, different from mainland)
- British-influenced professional culture (Hong Kong English + Cantonese)
- High population density, fast-paced city living
- Healthcare worker shortages in public hospitals
- Cantonese cultural identity (distinct from Mandarin mainland/Taiwan)

**Differences from zh-TW:**
- Hong Kong has higher English penetration — en-US may compete for affluent audiences
- Cantonese written in formal contexts; audio positioning should respect cultural fluency
- Political climate creates different invisible scripts around control, safety, and autonomy
- Smaller market than Taiwan; positioning should emphasize accessibility and relatability

**High-value search keywords:**
- "睡眠修復" / "失眠自然療法" (sleep repair)
- "工作倦怠恢復" / "職業壓力" (burnout, work pressure)
- "焦慮管理" / "神經系統調理" (anxiety management, nervous system)
- "香港生活壓力" (Hong Kong living stress)
- "人際關係" / "工作人脈" (relationships, workplace dynamics)

**Title philosophy notes:**
- Avoid mainland Simplified Chinese framing — position as distinct Hong Kong/Cantonese brand.
- Acknowledge political uncertainty (higher need for control, emotional regulation).
- Accessibility angle: "affordable wellness for busy Hong Kong professionals."
- Healthcare worker positioning: public hospital burnout is severe.

**TTS voice:** ElevenLabs (zh-HK) with Cantonese capability OR Google Neural2 (yue-HK-Standard-A for Cantonese, cmn-HK for formal written Chinese).

**Persona set:**
- `anxious_insomniac_hk` — 28–50, urban professional, overwork + political anxiety
- `burned_out_healthcare_hk` — nurses, public hospital, 24-hour shifts
- `gen_z_hk` — 18–26, social anxiety, online pressure
- `financial_sector_hk` — 30–55, banking/trading, high-stakes environment

**Phase 2–3 timeline:** Months 6–9 (alongside or shortly after zh-TW Phase 1 success).

**Strategy note:** Position zh-HK as sibling to zh-TW (both Traditional Chinese) but with distinct Hong Kong cultural framing. Do not position as "mainland lite" — emphasize Hong Kong's distinct needs.

---

### zh-CN (Simplified Chinese): Mainland China Market

**Invisible script:** *"我不是很弱。這是高效文明的代價。現在我選擇修復。" ("I'm not weak. This is the cost of high-efficiency civilization. Now I choose repair.")*

**Critical notes:**
- **Phase 5 only.** Requires local distribution infrastructure (Ximalaya, NetEase, WeChat Read, Dedao) — do NOT start content production until distribution pipeline is live.
- **No Google Play or Findaway.** Mainland China blocks both platforms. Aggregators and direct deals only.
- **Content review required.** Mainland authorities require compliance review; mental health positioning must be secular, wellness-framed.
- **Different script (Simplified vs Traditional).** Do not reuse zh-TW translations or branding.

**Cultural context:**
- Achievement culture (高考 exam pressure for all age groups, work-life as "obligation" framing)
- Longevity/health obsession (抗衰老, 健康管理)
- State-sanctioned wellness (not "therapy" or "mental health," which carry stigma)
- Rapid urbanization, high-speed living (similar to Hong Kong but with state integration)
- Tech sector burnout (互聯網人 culture, "996" and "加班文化" visible and normalized)

**High-value search keywords:**
- "睡眠修復" / "失眠解決方案" (sleep repair, insomnia solutions)
- "工作倦怠恢復" / "職業壓力管理" (burnout recovery, work pressure management)
- "焦慮調理" / "神經系統優化" (anxiety regulation, nervous system optimization)
- "抗衰老" / "健康管理" (anti-aging, health management) — longevity angle
- "瑜伽冥想" / "身心調和" (yoga meditation, mind-body harmony)

**Title philosophy notes:**
- Avoid "mental health" (精神健康) — frame as "nervous system" (神經系統), "wellness" (健康), "optimization" (優化).
- Longevity angle works — aging/vitality positioning acceptable.
- Tech sector burnout highly relatable (互聯網公司員工).
- State-compliant language required: no "therapy," no "trauma," no "disorder."
- Avoid political/identity framing — keep wellness apolitical.

**Platform-specific positioning:**
- **Ximalaya (喜馬拉雅):** Largest audiobook platform in mainland China, strong wellness category
- **NetEase Cloud Music (網易雲音樂):** Music-first but growing audiobook section, young audience
- **WeChat Read (微信讀書):** WeChat ecosystem, highly integrated, strong discovery
- **Dedao (得到):** Knowledge/self-improvement focused, higher-income audience, subscription model

**Persona set:**
- `anxious_insomniac_cn` — 28–50, urban professional, Beijing/Shanghai/Shenzhen, overwork anxiety
- `burned_out_tech_worker_cn` — 25–45, 互聯網公司, 996 hours, "加班文化"
- `gen_z_cn` — 18–26, 高考 pressure legacy, social media pressure, early career
- `health_conscious_urbanite_cn` — 30–65, focus on longevity, fitness, wellness optimization
- `healthcare_worker_cn` — doctors/nurses, hospital burnout

**Phase 5 timeline:** Months 10–18. **Prerequisite:** Local platform accounts open and tested, content review process mapped, Ximalaya and NetEase deals signed.

**Distribution strategy:** Launch via Ximalaya (largest reach) + NetEase (young audience) first; scale to WeChat Read and Dedao once process is streamlined.

---

### ja-JP (Japanese): Japan Market

**Invisible script:** *"私は弱くありません。神経系統です。それを整えることは、誇りある選択です。" ("I'm not weak. It's my nervous system. Regulating it is a proud choice.")*

**Critical rules:**
- **NEVER use "mental health" (精神的健康) in titles or positioning.** Mental health carries high stigma in Japan.
- **Use "nervous system" (神経系), "wellness" (ウェルビーイング), "self-care" (セルフケア), "nervous regulation" (神経調整).**
- **Politeness register (丁寧語) required throughout narration.** Not casual (です/ます vs だ).
- **Karoshi (過労死) culture:** Burnout brands are highest-priority and highest-resonance.

**Cultural context:**
- Karoshi (過労死, death from overwork) is a known phenomenon — burnout highly relatable
- 社畜 (corporate slave) culture normalized; work identity central to life
- Mental health stigma remains despite recent awareness efforts
- Seasonal affective patterns (winter darkness in northern Japan)
- Aesthetic appreciation for detail, nature, contemplation
- Deep immersion in audio — podcast and audiobook growth accelerating

**High-value search keywords:**
- "睡眠改善" / "不眠症" (sleep improvement, insomnia)
- "疲労回復" / "疲れ対策" (fatigue recovery, fatigue management)
- "職場ストレス" / "仕事の疲れ" (workplace stress, work fatigue)
- "リラックス" / "瞑想" (relaxation, meditation)
- "神経系統調整" / "自律神経" (nervous system regulation, autonomic nervous system)

**Title philosophy notes:**
- Avoid clinical language entirely (therapist, therapy, disorder, mental health).
- Somatic/nervous-system framing is premium positioning in Japan (sophisticated, evidence-based).
- Nature imagery works (Mount Kurama, Kyoto temples, seasonal references).
- Politeness (敬語) and formal structure required in all copy.
- Karoshi and overwork positioning resonates deeply — "work-life balance" angle works across personas.

**Platform-specific positioning:**
- **Audible Japan:** Premium positioning, narrative-heavy, available
- **Spotify JP:** Sleep, focus, wellness (young audience)
- **Apple Books JP:** Wellness, nervous system, self-development
- **Kobo JP:** Strong market in Japan, diverse categories
- **Google Play JP:** Accessibility, affordability

**Persona set:**
- `anxious_insomniac_jp` — 30–50, 社畜 (salaryman), Tokyo/Osaka, overwork insomnia
- `burned_out_professional_jp` — 28–45, karoshi-adjacent, any industry, overwork + perfectionism
- `gen_z_jp` — 18–26, 引きこもり risk (hikikomori), academic pressure legacy, social anxiety
- `caregiver_jp` — 35–60, elder care burden (介護), family duty + personal burnout
- `seasonal_affected_jp` — year-round but winter-peak, northern Japan, seasonal darkness

**Phase 2 timeline:** Months 4–6 after zh-TW Phase 1 success.

**Phase 2 pilot brands (6 brands × 7 books = 42 titles):**
- `sleep_repair_jp` — hook: "夜中に目が覚めるのは神経系統です"
- `stabilizer_jp` — hook: "過労死文化を生き延びる"
- `karoshi_recovery_jp` — hook: "仕事の疲れは神経系統の問題です"
- `caregiver_support_jp` — hook: "介護疲れは神経系統問題、道徳的失敗ではありません"
- `seasonal_reset_jp` — hook: "冬の暗さを神経系統から調整"
- `contemplative_wisdom_jp` — hook: "禅的リラックス、科学的根拠" (Zen relaxation, scientific basis)

**TTS voice:** ElevenLabs (ja-JP) with politeness register validation. Google Neural2 (ja-JP-Neural2-B) as fallback. Validate tone for formal, meditative content.

---

### ko-KR (Korean): South Korea Market

**Invisible script:** *"나는 약하지 않다. 나의 신경계가 과도하게 경각심을 가지고 있을 뿐이다. 이제 나는 치유를 선택한다." ("I'm not weak. My nervous system is hypervigilant. Now I choose healing.")*

**Cultural context:**
- **빨리빨리 (Ppalli-ppalli) culture:** Fast-paced living, rapid decision-making, impatience with slow processes. Micro sessions (15–30 min) may outperform deep dives.
- **Achievement culture:** 학벌 (educational hierarchy), 수능 (national exam), perfectionism pervasive.
- **Burnout (번아웃) is high-awareness, high-search term.** Awareness post-pandemic is higher than 5 years ago.
- **K-beauty and wellness overlap:** Metabolic, longevity, skin-health angles resonate.
- **Mental health awareness growing:** Less stigma than Japan, but still conservative.
- **High audio consumption:** Podcast/audiobook market growing rapidly, younger audience engaged.

**High-value search keywords:**
- "수면 개선" / "불면증 자연 치료" (sleep improvement, insomnia natural remedy)
- "번아웃 회복" / "직장 스트레스" (burnout recovery, work stress)
- "불안감 관리" / "공황 발작" (anxiety management, panic attacks)
- "신경계 조정" / "미주신경" (nervous system regulation, vagus nerve)
- "직장 인간관계" / "동료 스트레스" (workplace relationships, colleague stress)

**Title philosophy notes:**
- 번아웃 (burnout) is high-search, high-resonance — lead with this positioning.
- Micro session format (15–30 min) should be tested alongside standard deep dives.
- K-beauty wellness crossover: metabolic health, longevity, skin wellness angles work.
- Achievement culture angle: perfectionism, over-studying, exam pressure (even for adults).
- Avoid overly spiritual framing; secular, science-based positioning works best.

**Platform-specific positioning:**
- **Spotify KR:** Sleep, focus, wellness, young audience
- **Apple Books KR:** Self-development, wellness, nervous system
- **Google Play KR:** Accessibility, affordability
- **Naver Audiobook:** Largest Korean audiobook platform, strong discovery
- **Kakao Page:** Growing audiobook section, entertainment-integrated

**Persona set:**
- `anxious_insomniac_kr` — 28–50, Seoul/Busan, overwork insomnia
- `burned_out_professional_kr` — 25–45, 번아웃 (burnout), achievement culture legacy
- `gen_z_kr` — 18–26, 수능 pressure, social anxiety, early career
- `perfectionist_achiever_kr` — 30–55, career-focused, perfectionism-driven
- `k_beauty_wellness_kr` — 25–45, health-conscious, metabolic/longevity focus

**Phase 3 timeline:** Months 5–7 after zh-TW Phase 1 launches.

**Phase 3 pilot brands (4 brands × 7 books = 28 titles):**
- `sleep_repair_kr` — hook: "번아웃이 당신의 수면을 파괴합니다"
- `stabilizer_kr` — hook: "신경계 과도 경각심: 능력 문제가 아닙니다"
- `perfectionism_unwind_kr` — hook: "완벽함 추구의 신경계 비용"
- `burnout_recovery_kr` — hook: "번아웃은 신경계입니다, 약함이 아닙니다"

**TTS voice:** ElevenLabs (ko-KR) or Google Neural2 (ko-KR-Neural2-A). Validate tone for younger, more casual positioning than Japanese market.

**Format consideration:** Test 15–20 min micro sessions (aligned with ppalli-ppalli culture) vs 30–45 min standard sessions; measure completion rates and user satisfaction.

---

### de-DE (German): Germany / Austria / Switzerland (DACH)

**Invisible script:** *"Ich bin nicht schwach. Das ist ein Nervensystem-Problem. Ich wähle jetzt, es zu reparieren." ("I'm not weak. This is a nervous system issue. I'm now choosing to repair it.")*

**Critical rule:** Science-based, evidence-grounded framing is required. Avoid overtly spiritual framing. Secular nervous system / neuroscience angle works best.

**Cultural context:**
- **Evidence-based purchasing:** Germans and Austrians want scientific backing, peer-reviewed research references.
- **Largest European audiobook market:** DACH region (Germany, Austria, Switzerland) is a significant opportunity.
- **Stressbewältigung (stress management) and Burnout are high-search terms.**
- **Professional/formal register:** "Sie" (formal you) and structured language required in all copy.
- **Audible.de is a significant market player** — premium positioning works.
- **Skepticism of pseudoscience:** Avoid wellness cliché; ground everything in neuroscience or somatic evidence.

**High-value search keywords:**
- "Schlaf verbessern" / "Schlafstörungen natürlich" (sleep improvement, insomnia natural)
- "Burnout-Erholung" / "Arbeitsstress" (burnout recovery, work stress)
- "Angststörung Management" / "Panikattacken" (anxiety management, panic attacks)
- "Nervensystem Regulation" / "Vagus Nerv" (nervous system regulation, vagus nerve)
- "Stressbewältigung" / "Achtsamkeit" (stress management, mindfulness)

**Title philosophy notes:**
- Lead with neuroscience credibility, not lifestyle branding.
- "Nervensystem" framing is premium and credible.
- "Burnout" is high-awareness, high-search — position burnout recovery prominently.
- Avoid vague wellness language; be specific about mechanisms (nervous system, vagus, parasympathetic).
- Professional register (formal "Sie") and structured language required.
- Audible positioning should emphasize expert narration and research depth.

**Platform-specific positioning:**
- **Audible.de:** Premium positioning, expert narration, research-backed
- **Spotify DE:** Sleep, focus, wellness, younger audience
- **Apple Books DE:** Self-development, health, wellness
- **Google Play DE:** Accessibility, affordability
- **Findaway DE:** Independent retail distribution

**Persona set:**
- `anxious_insomniac_de` — 28–50, urban professional, Berlin/Munich, overwork insomnia
- `burned_out_professional_de` — 28–45, burnout + perfectionism, any industry
- `science_driven_wellness_de` — 30–60, skeptical of pseudoscience, wants research backing
- `caregiver_de` — 35–65, elder care (Pflege), family duty + burnout
- `manager_burnout_de` — 40–60, leadership pressure, Mittelstand (mid-market) companies

**Phase 4 timeline:** Months 7–12 with other European locales.

**Phase 4 pilot brands (3 brands × 7 books = 21 titles):**
- `sleep_repair_de` — hook: "Nervensystem-Reparatur für Arbeits-Schlaflosigkeit"
- `stabilizer_de` — hook: "Burnout ist ein Nervensystem-Problem, nicht ein Charakter-Problem"
- `adhd_anchor_de` — hook: "ADHS und Burnout: Nervensystem-Strategien" (science-based, not vague)

**TTS voice:** ElevenLabs (de-DE) with professional register, or Google Neural2 (de-DE-Neural2-A). Validate tone for formal, evidence-based positioning.

---

### fr-FR (French): France Market

**Invisible script:** *"Je ne suis pas faible. C'est mon système nerveux. Je choisis maintenant de le réparer avec intelligence." ("I'm not weak. It's my nervous system. I'm now choosing to repair it with intelligence.")*

**Cultural context:**
- **Philosophical framing accepted:** French audiences appreciate existential and philosophical angles alongside somatic.
- **Stoic and existentialist traditions:** "What is in my control vs. what isn't" resonates.
- **Strong audiobook market:** France has one of Europe's most mature audiobook ecosystems.
- **Secular framing preferred:** Avoid overtly spiritual positioning; philosophical and rational angles work better.
- **Work-life balance is evolving:** Post-COVID shift toward questioning hustle culture.
- **Healthcare awareness:** Public health discussion is nuanced and sophisticated.

**High-value search keywords:**
- "Sommeil réparation" / "Insomnie naturelle" (sleep repair, insomnia natural)
- "Récupération du burnout" / "Stress professionnel" (burnout recovery, work stress)
- "Gestion de l'anxiété" / "Attaques de panique" (anxiety management, panic attacks)
- "Régulation du système nerveux" / "Nerf vague" (nervous system regulation, vagus nerve)
- "Récupération émotionnelle" / "Sagesse existentielle" (emotional recovery, existential wisdom)

**Title philosophy notes:**
- Philosophical framing works: "What can I control?" (stoic angle), autonomy, freedom themes.
- "Système nerveux" positioning is credible and sophisticated.
- Avoid motivational cliché; intellectual depth is expected.
- Existential and contemplative angles enhance appeal (e.g., "Finding meaning in recovery").
- Emotional intelligence (l'intelligence émotionnelle) framing works well.
- Literary/poetic language can be integrated without seeming overwrought.

**Platform-specific positioning:**
- **Audible France:** Premium positioning, philosophical depth, expert narration
- **Spotify FR:** Sleep, focus, wellness, younger/broader audience
- **Apple Books FR:** Self-development, philosophy, wellness
- **Google Play FR:** Accessibility, affordability
- **Findaway FR:** Independent distribution
- **Kobo FR:** Strong audiobook presence in French market

**Persona set:**
- `anxious_insomniac_fr` — 28–50, Paris/Lyon, overwork insomnia, intellectual bent
- `burned_out_professional_fr` — 28–45, burnout + questioning hustle culture
- `philosophical_seeker_fr` — 30–65, existential interest, meaning-making, contemplation
- `caregiver_fr` — 35–65, family care burden, philosophical acceptance
- `creative_professional_fr` — 25–50, artist/writer/knowledge worker, creative anxiety

**Phase 4 timeline:** Months 7–12 with other European locales.

**Phase 4 pilot brands (2 brands × 7 books = 14 titles):**
- `sleep_repair_fr` — hook: "Réparation du sommeil par l'intelligence du système nerveux"
- `contemplative_wisdom_fr` — hook: "Sagesse stoïque et système nerveux: rétablir le contrôle"

**TTS voice:** ElevenLabs (fr-FR) or Google Neural2 (fr-FR-Neural2-A). Validate tone for philosophical, contemplative positioning.

---

### hu-HU (Hungarian): Hungary Market

**Invisible script:** *"Nem vagyok gyenge. Ez az idegrendszer. Most azt választom, hogy helyrehozom." ("I'm not weak. It's my nervous system. Now I'm choosing to repair it.")*

**Critical notes:**
- **Smaller market but high per-capita audio consumption:** Hungary has engaged, educated audience.
- **ElevenLabs only for Hungarian TTS:** Google Neural2 does NOT have hu-HU Neural2 voice; use Google Standard (hu-HU-Standard-A) as fallback, but prioritize ElevenLabs.
- **Mental health stigma remains higher than Western Europe:** Wellness / self-development framing preferred over clinical language.

**Cultural context:**
- **High education levels:** Educated, analytical audience appreciates evidence-based positioning.
- **Smaller market means less competition:** Early entry can establish strong market position.
- **Health consciousness:** Strong focus on wellness, longevity, prevention.
- **Post-socialist healthcare context:** Some skepticism of institutional mental health; self-directed wellness preferred.
- **Strong folk remedy tradition:** Herbal, somatic, traditional wellness angles resonate.

**High-value search keywords:**
- "Alvás javítás" / "Insomnia kezelés" (sleep improvement, insomnia treatment)
- "Kiégés helyreállítása" / "Munkahelyi stressz" (burnout recovery, work stress)
- "Szorongás kezelése" / "Panikroham" (anxiety management, panic attacks)
- "Idegrendszer szabályozás" / "Vagus ideg" (nervous system regulation, vagus nerve)
- "Wellness" / "Önellátás" (wellness, self-care)

**Title philosophy notes:**
- Wellness framing (wellness, self-care) preferred over "mental health."
- Evidence-based positioning works for educated audience.
- Herbal/natural angles acceptable (Hungarian folk medicine tradition).
- Practical, actionable positioning resonates — avoid overly abstract framing.
- Politeness register appropriate but less formal than Japanese; natural Hungarian register acceptable.

**Platform-specific positioning:**
- **Spotify HU:** Sleep, focus, wellness, younger audience
- **Apple Books HU:** Wellness, health, self-development
- **Google Play HU:** Accessibility, affordability
- **Findaway HU:** Independent distribution
- **Kobo HU:** Strong market presence

**Persona set:**
- `anxious_insomniac_hu` — 28–50, Budapest/Debrecen, overwork insomnia
- `burned_out_professional_hu` — 28–45, burnout + perfectionism
- `health_conscious_adult_hu` — 30–65, wellness focus, prevention-oriented
- `caregiver_hu` — 35–65, elder care burden
- `educator_hu` — 25–60, teacher/professor, emotional labor burnout

**Phase 4 timeline:** Months 7–12 with other European locales.

**Phase 4 pilot brands (2 brands × 7 books = 14 titles):**
- `sleep_repair_hu` — hook: "Alvás javítás az idegrendszer intelligenciájával"
- `stabilizer_hu` — hook: "Kiégés az idegrendszer problémája, nem karakter probléma"

**TTS voice:** ElevenLabs (hu-HU) is preferred and required. Google Standard (hu-HU-Standard-A) as fallback only. Do NOT use Google Neural2 (does not exist for hu-HU).

---

### es-US (US Hispanic Market)

**Invisible script:** *"No soy débil. Mi sistema nervioso está demasiado alerta. Ahora elijo sanarme." ("I'm not weak. My nervous system is overalert. Now I choose to heal.")*

**Critical notes:**
- **Largest non-English US audiobook opportunity.** Highest US ROI outside en-US.
- **Neutral Latin American Spanish preferred, not Castilian.** Avoid Spain-specific framing.
- **Distribute to US storefronts (same territory as en-US) but different locale.**
- **Different cultural context from Spain:** Family structure, work-life balance values, immigration/acculturation themes may apply.

**Cultural context:**
- **Family and community values:** Family support and obligation central to identity.
- **Work-ethic culture:** Strong work identity; burnout can feel like personal failure.
- **Acculturation stress:** For immigrants, additional layer of identity/belonging anxiety.
- **Healthcare access:** Lower health literacy in some segments; accessibility and affordability critical.
- **Growing wellness awareness:** Younger, bilingual Latinos increasingly engaged with wellness content.
- **Religious/spiritual tradition:** Some audiences may respond to spiritual alongside secular framing (discretionary per title).

**High-value search keywords:**
- "Reparación del sueño" / "Remedio natural para el insomnio" (sleep repair, insomnia remedy)
- "Recuperación del agotamiento" / "Estrés laboral" (burnout recovery, work stress)
- "Manejo de la ansiedad" / "Ataques de pánico" (anxiety management, panic attacks)
- "Regulación del sistema nervioso" / "Nervio vago" (nervous system regulation, vagus nerve)
- "Bienestar familiar" / "Relaciones de pareja" (family wellness, couple relationships)

**Title philosophy notes:**
- Lead with accessibility and family wellness (not just individual; family systems matter).
- Neutral Latin American Spanish required; no Castilian features (no "vosotros," no "c/z" distinction).
- Family/community angle: relationships, family dynamics, caregiving.
- Acculturation angle (for appropriate personas): navigating two cultures, identity integration.
- Practical, actionable positioning — avoid overly abstract or overly spiritual framing.
- Affordable framing works — "accessible wellness," not premium positioning.

**Platform-specific positioning:**
- **Spotify US (es-US category):** Sleep, focus, wellness, younger/bilingual audience
- **Apple Books US (es-US category):** Wellness, self-development
- **Google Play US (es-US category):** Accessibility, affordability, discovery
- **Audible US (es-US category):** Premium positioning, family narratives

**Persona set:**
- `anxious_insomniac_us_es` — 28–50, working parent, bilingual, overwork + family duties
- `burned_out_professional_us_es` — 25–50, career-focused, perfectionism, any industry
- `acculturation_anxious_us_es` — 18–40, immigrant/bilingual, identity anxiety, belonging
- `healthcare_worker_us_es` — nurses/health aides, US public healthcare, burnout
- `caregiver_us_es` — 35–65, elder parent care, family duty + burnout

**Phase 4 timeline:** Months 7–12 with other locales.

**Phase 4 pilot brands (3 brands × 7 books = 21 titles):**
- `sleep_repair_es_us` — hook: "Reparación del sueño para padres trabajadores"
- `stabilizer_es_us` — hook: "Tu sistema nervioso, no tu debilidad"
- `gen_z_grounding_es_us` — hook: "Ansiedad en dos culturas" (acculturation angle)

**TTS voice:** ElevenLabs (es-US) or Google Neural2 (es-US-Neural2-A). Validate neutral Latin American accent (not Spain Castilian).

---

### es-ES (Spanish Market)

**Invisible script:** *"No soy débil. Es mi sistema nervioso. Ahora elijo sanarlo con inteligencia." ("I'm not weak. It's my nervous system. Now I choose to heal it with intelligence.")*

**Critical notes:**
- **Castilian Spanish required:** Different from es-US (vosotros, c/z distinction, European cultural framing).
- **Separate storefront from es-US:** Do not mix in same catalog upload.
- **Different cultural and political context** from Latin America; Spain-specific positioning required.

**Cultural context:**
- **Parliamentary democracy, EU member:** Different political/security context than US Hispanic market.
- **Work-life balance culture evolving:** Spain has more structured work hours than US, but post-COVID stress remains high.
- **Healthcare system public and accessible:** Different healthcare literacy baseline than some US Hispanic segments.
- **Strong audiobook market in Spain:** Growing, educated audience.
- **Philosophical tradition:** Like France, existentialist and philosophical framing works.
- **Regional identities:** Catalonia, Basque Country, other regions have distinct identities; positioning should be inclusive but Spain-wide.

**High-value search keywords:**
- "Reparación del sueño" / "Insomnio natural" (sleep repair, insomnia natural)
- "Recuperación del agotamiento" / "Estrés laboral" (burnout recovery, work stress)
- "Gestión de la ansiedad" / "Ataques de pánico" (anxiety management, panic attacks)
- "Regulación del sistema nervioso" / "Nervio vago" (nervous system regulation, vagus nerve)
- "Bienestar" / "Salud mental" (wellness, mental health — less stigma than some markets)

**Title philosophy notes:**
- Castilian register required (vosotros for informal, European spelling/framing).
- Philosophical/existential framing works (like French market).
- Work-life balance angle resonates post-COVID.
- Science-based positioning credible and appreciated.
- Regional inclusivity: frame as Spain-wide, not Madrid-centric.

**Platform-specific positioning:**
- **Spotify ES:** Sleep, focus, wellness, younger audience
- **Apple Books ES:** Wellness, self-development, health
- **Google Play ES:** Accessibility, affordability
- **Findaway ES:** Independent distribution
- **Kobo ES:** Strong market presence in Spain

**Persona set:**
- `anxious_insomniac_es` — 28–50, Madrid/Barcelona, overwork insomnia
- `burned_out_professional_es` — 28–45, burnout + work-life questions
- `philosophical_wellness_es` — 30–65, existential + wellness interests
- `healthcare_worker_es` — 25–60, public healthcare, burnout
- `caregiver_es` — 35–65, family care, elder support

**Phase 4 timeline:** Months 7–12 with other European locales.

**Phase 4 pilot brands (2 brands × 7 books = 14 titles):**
- `sleep_repair_es` — hook: "Reparación del sueño para profesionales europeos"
- `stabilizer_es` — hook: "Agotamiento es un problema del sistema nervioso, no un carácter"

**TTS voice:** ElevenLabs (es-ES) or Google Neural2 (es-ES-Neural2-A). Validate Castilian register (vosotros, European pronunciation).

---

### zh-SG (Singaporean Chinese, Simplified)

**Invisible script:** *"我不是不行。我的神經系統過度警覺。現在我選擇治癒。" ("I'm not incapable. My nervous system is hypervigilant. Now I choose to heal.")*

**Critical notes:**
- **English dominates Singapore commerce.** Evaluate whether en-US or zh-SG is higher ROI for this market. Chinese-speaking Singapore audience is smaller than often assumed.
- **Simplified Chinese script (like mainland China), but separate storefront.** Do not reuse zh-CN content without Singaporean cultural adaptation.
- **Multi-cultural context:** Chinese, Malay, Indian, British heritage influence.

**Cultural context:**
- **High English penetration:** English is official working language; affluent audiences may prefer en-US.
- **Efficiency and practicality valued:** Fast-paced, result-oriented, no-nonsense positioning.
- **Multicultural and cosmopolitan:** Positioning should acknowledge diversity without exoticizing.
- **Healthcare awareness:** High health literacy; evidence-based positioning works.
- **Smaller market:** Lower volume, but often higher margin (affluent city-state).

**High-value search keywords:**
- "睡眠修復" / "失眠" (sleep repair, insomnia)
- "工作倦怠" / "職業壓力" (work burnout, work pressure)
- "焦慮管理" / "神經系統" (anxiety management, nervous system)
- "健康管理" / "自我照顧" (health management, self-care)
- "新加坡工作生活" (Singapore work-life context)

**Title philosophy notes:**
- Efficiency angle: practical, fast, results-oriented.
- Cosmopolitan positioning: acknowledge diverse Singapore.
- Evidence-based preferred; avoid cliché wellness language.
- Affordability angle can work for broader reach, but premium positioning acceptable too.

**Platform-specific positioning:**
- **Spotify SG:** Sleep, focus, wellness
- **Apple Books SG:** Wellness, health
- **Google Play SG:** Accessibility
- **Findaway SG:** Distribution

**Persona set:**
- `anxious_professional_sg` — 25–50, Singapore, high-pressure career
- `health_conscious_sg` — 30–65, wellness focus, efficiency-oriented
- `gen_z_sg` — 18–26, bilingual, modern anxiety

**Phase 5 timeline:** Months 12–18 (later phase due to market size).

**Phase 5 pilot brands (2 brands × 7 books = 14 titles):**
- `sleep_repair_sg` — hook: "高效新加坡專業人士的睡眠修復"
- `stabilizer_sg` — hook: "新加坡工作壓力的神經系統解決方案"

**TTS voice:** ElevenLabs (zh-SG fallback to zh-CN) or Google Neural2 (cmn-CN-Wavenet-A, fallback). Validate efficiency and clarity of tone.

**Market validation:** Before full Phase 5 launch, test whether en-US positions better than zh-SG in Singapore market. May pivot strategy based on early adoption data.

---

## 3. Per-Locale Go-Live Checklist

This section defines the exact criteria that must be complete before a locale can launch its pilot wave. Each locale has the same template, with locale-specific additions where needed.

### en-US Go-Live Checklist

**Status:** Ongoing (Seed Wave active, full catalog in progress).

#### Content

- [x] Locale persona definitions written (unified_personas.txt, en-US personas defined)
- [x] Atoms directory created: atoms/en-US/ (fully populated)
- [x] All required (persona, topic) pairs have atom pools (coverage gate 100%)
- [x] Translation quality validated by native speaker review (baseline for other locales)
- [x] Location variable files populated for US Tier 1 cities (NYC, LA, Chicago); Tier 2 (SF/Bay, Seattle, Austin, Houston); Tier 3 (Miami, Boston, Denver, DC, Atlanta)

#### Technical

- [x] locale_registry.yaml entry present and validated (is_baseline: true)
- [x] brand_registry_locale_extension.yaml has all 24 en-US brands
- [x] content_roots_by_locale.yaml entry added for en-US
- [x] CI gate #49 (locale_territory_consistency) passes for all en-US books
- [x] TTS voice auditioned and approved (ElevenLabs en-US primary, Google Neural2 fallback)
- [x] BookSpec locale/territory fields validated (locale: en-US, territory: US)

#### Distribution

- [x] Storefront accounts created for US territory (Google Play US, Findaway US, Apple Books US, Kobo US, Spotify US)
- [x] Metadata schema validated for en-US (title, description, keywords in English)
- [x] Distribution routing rules verified (en-US: US storefronts only, no international)
- [x] First 50–75 books (Seed Wave) uploaded and approved on primary platforms
- [x] ISBNs/ASINs assigned per book

#### Marketing

- [x] Invisible script research completed for en-US (productivity-based identity, nervous system as key, burnout recovery)
- [x] Title testing done (keyword research, A/B testing for market-speak)
- [x] Platform category positioning confirmed (Spotify: Sleep/Wellness; Apple Books: Mental Health/Self-Help; Audible: Premium; Google Play: Broad)
- [x] Launch wave plan: Seed Wave (50–75 titles) → validation → Wave 2–4 scale

#### Launch Status

- **Wave 1 (Seed Wave) active:** 50–75 Phoenix Drop titles in distribution
- **Next phase:** Full 1,008 title generation and distribution (upon atoms 100% completion)

---

### zh-TW Go-Live Checklist

**Target status:** Complete by Month 3 (Phase 1 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, zh-TW personas: anxious_insomniac_tw, burned_out_professional_tw, gen_z_tw, bereaved_adult_tw, anxious_attacher_tw, healthcare_worker_tw)
- [ ] Atoms directory created: atoms/zh-TW/ (fully populated with Traditional Chinese)
- [ ] All required (persona, topic) pairs have atom pools for 6 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Taiwanese speaker review (not mainland Simplified; Traditional script verified)
- [ ] Location variable files populated for TW cities (Taipei, Hsinchu 竹科 region, Taichung)
- [ ] Invisible script hook testing: native speaker validation of key phrases (e.g., "停止嘗試入睡" for sleep brand)

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: zh-TW, script: Traditional Chinese, tts_locale_code: zh-TW)
- [ ] brand_registry_locale_extension.yaml has all 6 Phase 1 pilot brands (sleep_repair_tw, stabilizer_tw, panic_first_aid_tw, gen_z_grounding_tw, grief_companion_tw, inner_security_tw)
- [ ] content_roots_by_locale.yaml entry added for zh-TW
- [ ] CI gate #49 (locale_territory_consistency) passes for all zh-TW pilot books (locale: zh-TW, territory: TW, no US storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs zh-TW primary; Google Neural2 cmn-TW-Wavenet-A fallback; validate emotional tone for Traditional script)
- [ ] BookSpec locale/territory fields validated (locale: zh-TW, territory: TW)

#### Distribution

- [ ] Storefront accounts created for TW territory (Google Play TW, Findaway TW, Apple Books TW, Kobo TW, Spotify TW)
- [ ] Metadata schema validated for zh-TW (title, description, keywords in Traditional Chinese; no mainland Simplified words)
- [ ] Distribution routing rules verified (zh-TW: TW storefronts only; NOT US storefronts; NOT HK storefronts)
- [ ] First 6–7 books from each of 6 pilot brands (42 titles total) uploaded and approved on primary TW platforms
- [ ] ISBNs/ASINs assigned per book (TW ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for zh-TW (tech sector burnout, filial piety, social comparison, academic legacy)
- [ ] Title testing done (keyword research for Traditional Chinese market; validate "停止嘗試入睡" resonance, "竹科倦怠" resonance)
- [ ] Platform category positioning confirmed (Spotify TW: Sleep/Wellness; Apple Books TW: Self-Development; Google Play TW: Wellness)
- [ ] Launch wave plan: 6-brand pilot (42 titles) → native speaker validation (4–6 weeks) → feedback integration → scale decision

#### Locale-specific additions (zh-TW)

- [ ] Traditional Chinese script verified (not Simplified; all atoms in Traditional)
- [ ] Taiwan-specific cultural references validated (竹科, 聯考, IG/Dcard, not mainland context)
- [ ] Filial piety and family duty angle tested with target personas
- [ ] Gen Z social media pressure angle validated in titles/hooks

#### Launch Status

- **Target:** Phase 1 pilot live by Month 3
- **Success criteria:** 42 titles live, >80% reviews positive, native speaker feedback incorporated

---

### ja-JP Go-Live Checklist

**Target status:** Complete by Month 6 (Phase 2 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, ja-JP personas: anxious_insomniac_jp, burned_out_professional_jp, gen_z_jp, caregiver_jp, seasonal_affected_jp)
- [ ] Atoms directory created: atoms/ja-JP/ (fully populated with Japanese, Kanji/Hiragana/Katakana, politeness register 丁寧語)
- [ ] All required (persona, topic) pairs have atom pools for 6 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Japanese speaker review (politeness register validated; no mental health stigma language)
- [ ] Location variable files populated for JP cities (Tokyo, Osaka, Kyoto temples/nature references, northern Japan seasonal context)
- [ ] Invisible script hook testing: native speaker validation that NO "mental health" language used; all hooks use "神経系統" or "ウェルビーイング"
- [ ] Politeness register validated throughout atom content (丁寧語 required for narration)

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: ja-JP, script: Japanese, tts_locale_code: ja-JP)
- [ ] brand_registry_locale_extension.yaml has all 6 Phase 2 pilot brands (sleep_repair_jp, stabilizer_jp, karoshi_recovery_jp, caregiver_support_jp, seasonal_reset_jp, contemplative_wisdom_jp)
- [ ] content_roots_by_locale.yaml entry added for ja-JP
- [ ] CI gate #49 (locale_territory_consistency) passes for all ja-JP pilot books (locale: ja-JP, territory: JP, no US storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs ja-JP primary, Google Neural2 ja-JP-Neural2-B fallback; validate politeness register, emotional depth for meditative content)
- [ ] BookSpec locale/territory fields validated (locale: ja-JP, territory: JP)

#### Distribution

- [ ] Storefront accounts created for JP territory (Google Play JP, Findaway JP, Apple Books JP, Kobo JP, Audible JP, Spotify JP)
- [ ] Metadata schema validated for ja-JP (title, description, keywords in Japanese; NO "精神的健康" or mental health stigma language)
- [ ] Distribution routing rules verified (ja-JP: JP storefronts only; NOT US storefronts)
- [ ] First 6–7 books from each of 6 pilot brands (42 titles total) uploaded and approved on primary JP platforms (prioritize Audible JP for premium positioning)
- [ ] ISBNs/ASINs assigned per book (JP ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for ja-JP (karoshi culture, overwork normalization, nervous system reframe, seasonal affective patterns, contemplative/aesthetic angle)
- [ ] Title testing done (keyword research for Japanese market; validate "過労死回復" resonance, "神経系統" positioning as premium, karoshi angle)
- [ ] Platform category positioning confirmed (Audible JP: Premium/Narrative; Spotify JP: Sleep/Wellness; Apple Books JP: Self-Development)
- [ ] Launch wave plan: 6-brand pilot (42 titles) → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (ja-JP)

- [ ] NO "mental health" (精神的健康) in any titles or marketing copy — verified by native speaker
- [ ] Politeness register (丁寧語) validated for all narration scripts
- [ ] Karoshi (過労死) angle tested and confirmed resonance with burned_out_professional_jp persona
- [ ] Seasonal affective angle validated (winter darkness, Mount Kurama/nature references)
- [ ] 社畜 (salaryman) culture framing validated for burned_out_professional_jp positioning

#### Launch Status

- **Target:** Phase 2 pilot live by Month 6
- **Success criteria:** 42 titles live, >80% reviews positive, native speaker feedback incorporated, karoshi/nervous system positioning validated

---

### ko-KR Go-Live Checklist

**Target status:** Complete by Month 7 (Phase 3 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, ko-KR personas: anxious_insomniac_kr, burned_out_professional_kr, gen_z_kr, perfectionist_achiever_kr, k_beauty_wellness_kr)
- [ ] Atoms directory created: atoms/ko-KR/ (fully populated with Korean Hangul)
- [ ] All required (persona, topic) pairs have atom pools for 4 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Korean speaker review
- [ ] Location variable files populated for KR cities (Seoul, Busan)
- [ ] Invisible script hook testing: native speaker validation of 번아웃 (burnout) positioning, ppalli-ppalli (빨리빨리) pacing expectations

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: ko-KR, script: Hangul, tts_locale_code: ko-KR)
- [ ] brand_registry_locale_extension.yaml has all 4 Phase 3 pilot brands (sleep_repair_kr, stabilizer_kr, perfectionism_unwind_kr, burnout_recovery_kr)
- [ ] content_roots_by_locale.yaml entry added for ko-KR
- [ ] CI gate #49 (locale_territory_consistency) passes for all ko-KR pilot books (locale: ko-KR, territory: KR, no US storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs ko-KR primary, Google Neural2 ko-KR-Neural2-A fallback; validate tone for fast-paced, achievement-oriented content)
- [ ] BookSpec locale/territory fields validated (locale: ko-KR, territory: KR)

#### Distribution

- [ ] Storefront accounts created for KR territory (Google Play KR, Findaway KR, Apple Books KR, Kobo KR, Naver Audiobook, Kakao Page)
- [ ] Metadata schema validated for ko-KR (title, description, keywords in Korean; focus 번아웃 positioning)
- [ ] Distribution routing rules verified (ko-KR: KR storefronts only; NOT US storefronts)
- [ ] First 4 pilot brands with 7 books each (28 titles total) uploaded and approved on primary KR platforms (prioritize Naver Audiobook for largest reach)
- [ ] ISBNs/ASINs assigned per book (KR ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for ko-KR (번아웃 awareness, achievement culture, perfectionism cost, 수능 legacy, 빨리빨리 pacing expectations, K-beauty wellness crossover)
- [ ] Title testing done (keyword research for Korean market; validate "번아웃 회복" resonance, perfectionism angle, micro-session format viability)
- [ ] Platform category positioning confirmed (Naver Audiobook: Discovery; Spotify KR: Sleep/Wellness; Apple Books KR: Self-Development)
- [ ] Launch wave plan: 4-brand pilot (28 titles) → micro-session format testing vs standard (A/B test) → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (ko-KR)

- [ ] 번아웃 (burnout) positioning validated as high-priority, high-resonance hook
- [ ] Micro-session format (15–30 min) tested against standard 30–45 min: measure completion rates, satisfaction, engagement
- [ ] Achievement culture / perfectionism angle validated with perfectionist_achiever_kr persona
- [ ] K-beauty wellness crossover (metabolic health, longevity) tested with appropriate personas

#### Launch Status

- **Target:** Phase 3 pilot live by Month 7
- **Success criteria:** 28 titles live, >80% reviews positive, micro-session format viability data collected, native speaker feedback incorporated

---

### de-DE Go-Live Checklist

**Target status:** Complete by Month 12 (Phase 4 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, de-DE personas: anxious_insomniac_de, burned_out_professional_de, science_driven_wellness_de, caregiver_de, manager_burnout_de)
- [ ] Atoms directory created: atoms/de-DE/ (fully populated with German, formal register)
- [ ] All required (persona, topic) pairs have atom pools for 3 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native German speaker review (formal register "Sie" verified)
- [ ] Location variable files populated for DACH region (Berlin, Munich, Vienna, Zurich)
- [ ] Invisible script hook testing: native speaker validation of science-grounded positioning, "Nervensystem" credibility, "Burnout" resonance

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: de-DE, script: Latin, tts_locale_code: de-DE)
- [ ] brand_registry_locale_extension.yaml has all 3 Phase 4 pilot brands (sleep_repair_de, stabilizer_de, adhd_anchor_de)
- [ ] content_roots_by_locale.yaml entry added for de-DE
- [ ] CI gate #49 (locale_territory_consistency) passes for all de-DE pilot books (locale: de-DE, territory: DE, no US storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs de-DE primary, Google Neural2 de-DE-Neural2-A fallback; validate formal register, expert narration tone)
- [ ] BookSpec locale/territory fields validated (locale: de-DE, territory: DE)

#### Distribution

- [ ] Storefront accounts created for DACH territory (Google Play DE, Findaway DE, Apple Books DE, Kobo DE, Spotify DE, Audible DE)
- [ ] Metadata schema validated for de-DE (title, description, keywords in German; emphasis on science-grounded language, "Stressbewältigung," "Burnout")
- [ ] Distribution routing rules verified (de-DE: DACH storefronts only; NOT US storefronts)
- [ ] First 3 pilot brands with 7 books each (21 titles total) uploaded and approved on primary DACH platforms (prioritize Audible.de for premium positioning)
- [ ] ISBNs/ASINs assigned per book (DE ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for de-DE (evidence-based purchasing, Burnout awareness, work-life questioning, professional skepticism of pseudoscience)
- [ ] Title testing done (keyword research for German market; validate "Nervensystem Regulation" credibility, "Burnout" resonance, DACH regional relevance)
- [ ] Platform category positioning confirmed (Audible.de: Premium/Expert; Spotify DE: Sleep/Wellness; Apple Books DE: Health/Self-Development)
- [ ] Launch wave plan: 3-brand pilot (21 titles) → expert narration validation → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (de-DE)

- [ ] Science-grounded positioning validated: research credibility, peer-review angle, mechanism explanation required
- [ ] Formal register (Sie, professional language) verified throughout
- [ ] DACH regional inclusivity confirmed (not Germany-only framing; Austria/Switzerland relevance validated)
- [ ] Audible.de premium positioning validated; expert narration quality auditioned

#### Launch Status

- **Target:** Phase 4 pilot live by Month 12
- **Success criteria:** 21 titles live, >80% reviews positive, science-grounded positioning validated by educated audience, native speaker feedback incorporated

---

### fr-FR Go-Live Checklist

**Target status:** Complete by Month 12 (Phase 4 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, fr-FR personas: anxious_insomniac_fr, burned_out_professional_fr, philosophical_seeker_fr, caregiver_fr, creative_professional_fr)
- [ ] Atoms directory created: atoms/fr-FR/ (fully populated with French)
- [ ] All required (persona, topic) pairs have atom pools for 2 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native French speaker review (philosophical register, poetic language acceptable)
- [ ] Location variable files populated for France (Paris, Lyon, Mediterranean references)
- [ ] Invisible script hook testing: native speaker validation of philosophical/existential framing, autonomy angle, contemplative tone

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: fr-FR, script: Latin, tts_locale_code: fr-FR)
- [ ] brand_registry_locale_extension.yaml has all 2 Phase 4 pilot brands (sleep_repair_fr, contemplative_wisdom_fr)
- [ ] content_roots_by_locale.yaml entry added for fr-FR
- [ ] CI gate #49 (locale_territory_consistency) passes for all fr-FR pilot books (locale: fr-FR, territory: FR, no US storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs fr-FR primary, Google Neural2 fr-FR-Neural2-A fallback; validate philosophical, contemplative tone)
- [ ] BookSpec locale/territory fields validated (locale: fr-FR, territory: FR)

#### Distribution

- [ ] Storefront accounts created for FR territory (Google Play FR, Findaway FR, Apple Books FR, Kobo FR, Spotify FR, Audible France)
- [ ] Metadata schema validated for fr-FR (title, description, keywords in French; philosophical language acceptable)
- [ ] Distribution routing rules verified (fr-FR: FR storefronts only; NOT US storefronts)
- [ ] First 2 pilot brands with 7 books each (14 titles total) uploaded and approved on primary FR platforms
- [ ] ISBNs/ASINs assigned per book (FR ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for fr-FR (existential framing, work-life balance questioning, autonomy/control angle, philosophical tradition)
- [ ] Title testing done (keyword research for French market; validate philosophical positioning, existential angle, emotional intelligence framing)
- [ ] Platform category positioning confirmed (Audible France: Premium/Philosophical; Spotify FR: Sleep/Wellness; Apple Books FR: Self-Development)
- [ ] Launch wave plan: 2-brand pilot (14 titles) → philosophical positioning validation → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (fr-FR)

- [ ] Philosophical/existential framing validated as premium positioning
- [ ] Autonomy and control angle (stoic framing) validated with target personas
- [ ] Literary/poetic language quality assured by native speaker (sophistication expected)

#### Launch Status

- **Target:** Phase 4 pilot live by Month 12
- **Success criteria:** 14 titles live, >80% reviews positive, philosophical positioning resonates with educated French audience, native speaker feedback incorporated

---

### hu-HU Go-Live Checklist

**Target status:** Complete by Month 12 (Phase 4 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, hu-HU personas: anxious_insomniac_hu, burned_out_professional_hu, health_conscious_adult_hu, caregiver_hu, educator_hu)
- [ ] Atoms directory created: atoms/hu-HU/ (fully populated with Hungarian)
- [ ] All required (persona, topic) pairs have atom pools for 2 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Hungarian speaker review
- [ ] Location variable files populated for Hungary (Budapest, Debrecen, regional cities)
- [ ] Invisible script hook testing: native speaker validation of wellness (not "mental health") framing, practical/actionable positioning

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: hu-HU, script: Latin, tts_locale_code: hu-HU)
- [ ] brand_registry_locale_extension.yaml has all 2 Phase 4 pilot brands (sleep_repair_hu, stabilizer_hu)
- [ ] content_roots_by_locale.yaml entry added for hu-HU
- [ ] CI gate #49 (locale_territory_consistency) passes for all hu-HU pilot books (locale: hu-HU, territory: HU, no US storefront routing)
- [ ] **TTS voice auditioned and approved: ElevenLabs hu-HU PRIMARY (Google Neural2 hu-HU does NOT exist; use Google hu-HU-Standard-A as fallback ONLY)**
- [ ] BookSpec locale/territory fields validated (locale: hu-HU, territory: HU)

#### Distribution

- [ ] Storefront accounts created for HU territory (Google Play HU, Findaway HU, Apple Books HU, Kobo HU, Spotify HU)
- [ ] Metadata schema validated for hu-HU (title, description, keywords in Hungarian; wellness framing, no mental health stigma language)
- [ ] Distribution routing rules verified (hu-HU: HU storefronts only; NOT US storefronts)
- [ ] First 2 pilot brands with 7 books each (14 titles total) uploaded and approved on primary HU platforms
- [ ] ISBNs/ASINs assigned per book (HU ISBNs distinct from en-US)

#### Marketing

- [ ] Invisible script research completed for hu-HU (health consciousness, wellness vs mental health distinction, practical outcomes, evidence-based positioning)
- [ ] Title testing done (keyword research for Hungarian market; validate wellness framing, practical action orientation)
- [ ] Platform category positioning confirmed (Spotify HU: Sleep/Wellness; Apple Books HU: Health/Wellness; Google Play HU: Accessibility)
- [ ] Launch wave plan: 2-brand pilot (14 titles) → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (hu-HU)

- [ ] **ElevenLabs hu-HU voice required — Google Neural2 hu-HU does NOT exist (critical: no Google Neural2 option for Hungarian)**
- [ ] Google Standard (hu-HU-Standard-A) acceptable only as fallback; ElevenLabs primary
- [ ] Wellness framing (not "mental health") validated throughout copy
- [ ] Health-conscious, prevention-oriented positioning confirmed with target personas

#### Launch Status

- **Target:** Phase 4 pilot live by Month 12
- **Success criteria:** 14 titles live, >80% reviews positive, ElevenLabs voice quality validated, native speaker feedback incorporated

---

### es-US Go-Live Checklist

**Target status:** Complete by Month 12 (Phase 4 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, es-US personas: anxious_insomniac_us_es, burned_out_professional_us_es, acculturation_anxious_us_es, healthcare_worker_us_es, caregiver_us_es)
- [ ] Atoms directory created: atoms/es-US/ (fully populated with Neutral Latin American Spanish, NOT Castilian)
- [ ] All required (persona, topic) pairs have atom pools for 3 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native US Hispanic Spanish speaker review (neutral Latin American accent, no Castilian vosotros/c/z)
- [ ] Location variable files populated for US cities with significant Hispanic populations (NYC, Los Angeles, Chicago, Houston, Miami)
- [ ] Invisible script hook testing: native speaker validation of family/community angle, acculturation (where applicable), practical outcomes

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: es-US, script: Latin, tts_locale_code: es-US)
- [ ] brand_registry_locale_extension.yaml has all 3 Phase 4 pilot brands (sleep_repair_es_us, stabilizer_es_us, gen_z_grounding_es_us)
- [ ] content_roots_by_locale.yaml entry added for es-US
- [ ] CI gate #49 (locale_territory_consistency) passes for all es-US pilot books (locale: es-US, territory: US [same as en-US], no international storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs es-US primary, Google Neural2 es-US-Neural2-A fallback; validate neutral Latin American accent)
- [ ] BookSpec locale/territory fields validated (locale: es-US, territory: US)

#### Distribution

- [ ] Storefront accounts created for US territory (Google Play US [es-US category], Findaway US, Apple Books US [es-US category], Kobo US, Spotify US [es-US category])
- [ ] Metadata schema validated for es-US (title, description, keywords in Spanish; neutral Latin American language, family/wellness focus)
- [ ] Distribution routing rules verified (es-US: US storefronts ONLY; NOT international; territory: US, not Mexico/Latin America)
- [ ] First 3 pilot brands with 7 books each (21 titles total) uploaded and approved on primary US platforms in es-US category
- [ ] ISBNs/ASINs assigned per book (es-US ISBNs distinct from en-US, distinct from es-ES)

#### Marketing

- [ ] Invisible script research completed for es-US (family/community values, work-ethic culture, acculturation stress for immigrant personas, healthcare accessibility, bilingual identity)
- [ ] Title testing done (keyword research for US Hispanic market; validate family wellness angle, acculturation angle for gen_z_grounding_es_us persona, practical outcomes focus)
- [ ] Platform category positioning confirmed (Spotify US [es-US]: Sleep/Wellness; Apple Books US [es-US]: Wellness/Self-Development; Google Play US [es-US]: Accessibility)
- [ ] Launch wave plan: 3-brand pilot (21 titles) → US Hispanic market validation → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (es-US)

- [ ] Neutral Latin American Spanish validated — no Castilian vosotros or c/z distinction
- [ ] Family/community angle integrated into title positioning (not just individual wellness)
- [ ] Acculturation angle (for gen_z_grounding_es_us brand) validated with bilingual Gen Z personas
- [ ] Accessibility and affordability positioning confirmed (largest non-English US market; affordability important)

#### Launch Status

- **Target:** Phase 4 pilot live by Month 12
- **Success criteria:** 21 titles live, >80% reviews positive, US Hispanic market positioning validated, family/community angle resonates, native speaker feedback incorporated

---

### es-ES Go-Live Checklist

**Target status:** Complete by Month 12 (Phase 4 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, es-ES personas: anxious_insomniac_es, burned_out_professional_es, philosophical_wellness_es, healthcare_worker_es, caregiver_es)
- [ ] Atoms directory created: atoms/es-ES/ (fully populated with Castilian Spanish)
- [ ] All required (persona, topic) pairs have atom pools for 2 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Spanish (Spain) speaker review (Castilian register, vosotros, c/z distinction)
- [ ] Location variable files populated for Spain (Madrid, Barcelona, regional cities; acknowledge Catalonia/regional identities without imposing)
- [ ] Invisible script hook testing: native speaker validation of philosophical/existential framing, work-life balance questioning, science-based positioning

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: es-ES, script: Latin, tts_locale_code: es-ES)
- [ ] brand_registry_locale_extension.yaml has all 2 Phase 4 pilot brands (sleep_repair_es, stabilizer_es)
- [ ] content_roots_by_locale.yaml entry added for es-ES
- [ ] CI gate #49 (locale_territory_consistency) passes for all es-ES pilot books (locale: es-ES, territory: ES, no US/international storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs es-ES primary, Google Neural2 es-ES-Neural2-A fallback; validate Castilian register)
- [ ] BookSpec locale/territory fields validated (locale: es-ES, territory: ES)

#### Distribution

- [ ] Storefront accounts created for Spain territory (Google Play ES, Findaway ES, Apple Books ES, Kobo ES, Spotify ES)
- [ ] Metadata schema validated for es-ES (title, description, keywords in Castilian Spanish; philosophical/existential language acceptable)
- [ ] Distribution routing rules verified (es-ES: Spain storefronts ONLY; NOT US; NOT Latin America)
- [ ] First 2 pilot brands with 7 books each (14 titles total) uploaded and approved on primary Spain platforms
- [ ] ISBNs/ASINs assigned per book (es-ES ISBNs distinct from en-US, distinct from es-US)

#### Marketing

- [ ] Invisible script research completed for es-ES (philosophical tradition, work-life balance questioning, evidence-based positioning, regional identities)
- [ ] Title testing done (keyword research for Spain market; validate philosophical angle, work-life balance resonance, regional inclusivity)
- [ ] Platform category positioning confirmed (Spotify ES: Sleep/Wellness; Apple Books ES: Wellness/Philosophy; Google Play ES: Health/Accessibility)
- [ ] Launch wave plan: 2-brand pilot (14 titles) → Spain market validation → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (es-ES)

- [ ] Castilian Spanish register validated (vosotros, c/z pronunciation)
- [ ] Philosophical/existential framing validated as premium positioning
- [ ] Regional inclusivity confirmed (not Madrid-centric; acknowledge Catalonia, Basque, other regions respectfully)
- [ ] Spain-specific work-life balance angle (structured work hours vs. US model) validated

#### Launch Status

- **Target:** Phase 4 pilot live by Month 12
- **Success criteria:** 14 titles live, >80% reviews positive, philosophical positioning resonates with Spanish educated audience, regional inclusivity validated, native speaker feedback incorporated

---

### zh-HK Go-Live Checklist

**Target status:** Complete by Month 9 (Phase 2–3 launch).

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, zh-HK personas: anxious_professional_hk, burned_out_healthcare_hk, gen_z_hk, financial_sector_hk)
- [ ] Atoms directory created: atoms/zh-HK/ (fully populated with Traditional Chinese, Cantonese cultural context)
- [ ] All required (persona, topic) pairs have atom pools for 4 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Hong Kong Chinese speaker review (Traditional script, Hong Kong cultural framing, not mainland or Taiwan positioning)
- [ ] Location variable files populated for Hong Kong (Hong Kong Island, Kowloon, New Territories; urban density context)
- [ ] Invisible script hook testing: native speaker validation of Hong Kong-specific cultural context, political/safety anxiety angle (distinct from Taiwan/mainland)

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: zh-HK, script: Traditional Chinese, tts_locale_code: zh-HK)
- [ ] brand_registry_locale_extension.yaml has all 4 Phase 2–3 pilot brands (to be defined, aligned with zh-TW brands but HK-positioned)
- [ ] content_roots_by_locale.yaml entry added for zh-HK
- [ ] CI gate #49 (locale_territory_consistency) passes for all zh-HK pilot books (locale: zh-HK, territory: HK, no US/TW/mainland storefront routing)
- [ ] TTS voice auditioned and approved (ElevenLabs zh-HK primary with Cantonese capability OR Google Neural2 yue-HK-Standard-A for Cantonese; validate Cantonese tone vs formal written Chinese)
- [ ] BookSpec locale/territory fields validated (locale: zh-HK, territory: HK)

#### Distribution

- [ ] Storefront accounts created for HK territory (Google Play HK, Findaway HK, Apple Books HK, Kobo HK, Spotify HK)
- [ ] Metadata schema validated for zh-HK (title, description, keywords in Traditional Chinese; Hong Kong-specific cultural context, NOT mainland Simplified positioning)
- [ ] Distribution routing rules verified (zh-HK: HK storefronts ONLY; NOT US; NOT TW; NOT mainland China)
- [ ] First 4 pilot brands with 7 books each (28 titles total) uploaded and approved on primary HK platforms
- [ ] ISBNs/ASINs assigned per book (HK ISBNs distinct from en-US, zh-TW, zh-CN)

#### Marketing

- [ ] Invisible script research completed for zh-HK (Hong Kong political/social anxiety context, British-influenced professional culture, Cantonese identity, healthcare worker burnout, high population density stress)
- [ ] Title testing done (keyword research for Hong Kong market; validate Hong Kong cultural positioning [distinct from Taiwan/mainland], healthcare worker angle, urban pressure context)
- [ ] Platform category positioning confirmed (Spotify HK: Sleep/Wellness; Apple Books HK: Self-Development; Google Play HK: Wellness)
- [ ] Launch wave plan: 4-brand pilot (28 titles) → Hong Kong market validation → native speaker feedback (4–6 weeks) → scale decision

#### Locale-specific additions (zh-HK)

- [ ] Hong Kong distinct cultural positioning validated (NOT Taiwan reuse, NOT mainland reuse)
- [ ] Political/social anxiety angle (distinct from Taiwan/mainland) integrated into invisible script
- [ ] Cantonese cultural identity validated; formal written Chinese register confirmed
- [ ] Healthcare worker burnout angle (public hospital context) validated with burned_out_healthcare_hk persona
- [ ] Urban density and fast-paced living context confirmed in atoms

#### Launch Status

- **Target:** Phase 2–3 pilot live by Month 9 (alongside or shortly after ja-JP Phase 2)
- **Success criteria:** 28 titles live, >80% reviews positive, Hong Kong distinct positioning validated, native speaker feedback incorporated, Cantonese/written Chinese TTS quality confirmed

---

### zh-CN Go-Live Checklist

**Target status:** Complete by Month 18 (Phase 5 launch, LATEST phase).

#### Pre-Launch Prerequisites (BEFORE atoms production)

- [ ] **Local platform accounts opened and tested:** Ximalaya (喜馬拉雅), NetEase Cloud Music (網易雲音樂), WeChat Read (微信讀書), Dedao (得到)
- [ ] **Content review process mapped:** Research mainland China content review requirements for wellness/health categories; document approval process, timelines, and compliance language rules
- [ ] **Ximalaya and NetEase distribution deals signed:** Confirm upload protocols, metadata schema, compliance requirements
- [ ] **Payment/payout infrastructure validated:** Ensure distribution partners can process payments to company accounts
- [ ] **Political sensitivity guidelines documented:** No political/identity framing allowed; wellness must be apolitical; state-aligned language required in some areas

#### Content

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, zh-CN personas: anxious_insomniac_cn, burned_out_tech_worker_cn, gen_z_cn, health_conscious_urbanite_cn, healthcare_worker_cn)
- [ ] Atoms directory created: atoms/zh-CN/ (fully populated with Simplified Chinese, mainland Chinese cultural context, NO mainland political framing)
- [ ] All required (persona, topic) pairs have atom pools for 6 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native mainland Chinese speaker review (Simplified script, not Traditional; state-compliant language; no mental health stigma; no political framing)
- [ ] Location variable files populated for China (Beijing, Shanghai, Shenzhen, Hangzhou; 996 culture, tech sector, urbanization context)
- [ ] Invisible script hook testing: native speaker validation of longevity/health optimization angle, tech sector burnout (互聯網公司), state-compliant wellness framing

#### Technical

- [ ] locale_registry.yaml entry present and validated (locale: zh-CN, script: Simplified Chinese, tts_locale_code: zh-CN, notes: "Google Play NOT available; Findaway does NOT distribute to mainland China; use local platforms only")
- [ ] brand_registry_locale_extension.yaml has all 6 Phase 5 pilot brands (to be defined, distinct from zh-TW/zh-HK brands)
- [ ] content_roots_by_locale.yaml entry added for zh-CN
- [ ] CI gate #49 (locale_territory_consistency) passes for all zh-CN pilot books (locale: zh-CN, territory: CN, NO Google Play/Findaway routing, local platforms only)
- [ ] TTS voice auditioned and approved (ElevenLabs zh-CN primary, Google Neural2 cmn-CN-Wavenet-A fallback; validate tone for optimization/longevity angle)
- [ ] BookSpec locale/territory fields validated (locale: zh-CN, territory: CN)

#### Distribution

- [ ] Storefront accounts created for CN territory (Ximalaya, NetEase Cloud Music, WeChat Read, Dedao; Apple Books CN as secondary)
- [ ] **Metadata schema validated for zh-CN:** Title, description, keywords in Simplified Chinese; state-compliant language; NO "mental health" (精神健康), NO "therapy" (治療), NO "trauma" (創傷) where flagged; USE "wellness" (健康), "optimization" (優化), "nervous system" (神經系統), "longevity" (抗衰老)
- [ ] **Distribution routing rules strictly enforced:** zh-CN books ONLY to local platforms (Ximalaya, NetEase, WeChat Read, Dedao, Apple Books CN); ABSOLUTELY NOT to Google Play US/international, ABSOLUTELY NOT to Findaway
- [ ] Content review completed for first 6–7 books per brand (42 titles total) on at least one local platform (recommend Ximalaya as largest); approval confirmed before wider distribution
- [ ] ISBNs/ASINs assigned per book (CN ISBNs distinct from en-US, distinct from all other Chinese locales)

#### Marketing

- [ ] Invisible script research completed for zh-CN (achievement culture, 高考 legacy, longevity/anti-aging obsession, 996/加班 normalization, tech sector pressure, high-speed urbanization, state wellness narrative)
- [ ] Title testing done (keyword research for mainland China market; validate "抗衰老" (anti-aging) resonance, tech sector angle, apolitical wellness framing, state-compliant positioning)
- [ ] Platform-specific positioning confirmed (Ximalaya: Largest reach, wellness category strong; NetEase: Young audience, music-integrated; WeChat Read: Ecosystem integration; Dedao: Knowledge/premium segment)
- [ ] Launch wave plan: 6-brand pilot (42 titles) → local platform content review → approval → native speaker feedback → scale decision

#### Locale-specific additions (zh-CN)

- [ ] **NO Google Play or Findaway:** Absolutely no routing to international platforms; CI gate #49 must block any attempt
- [ ] **State-compliant language:** All copy audited for sensitive terms; "wellness" (not "mental health"), "optimization" (not "therapy"), "nervous system" (not "trauma")
- [ ] **Local platform compliance:** Content review process completed for each platform; compliance documents filed with each
- [ ] **Longevity/anti-aging angle validated:** 抗衰老, 健康管理 positioning tested with health_conscious_urbanite_cn and appropriate personas
- [ ] **Tech sector (互聯網公司) burnout positioning:** 996 culture, 加班文化 angle validated with burned_out_tech_worker_cn persona
- [ ] **Simplified Chinese script verified:** NOT Traditional; all atoms in Simplified; no Taiwan/HK content reuse without Simplified adaptation

#### Launch Status

- **Target:** Phase 5 pilot live by Month 18 (LATEST phase, after all other locales)
- **Prerequisite:** All local platform accounts, compliance processes, and distribution partnerships must be signed and tested BEFORE atoms production begins
- **Success criteria:** 42 titles approved and live on at least one major platform (Ximalaya), >80% approval rate on content review, native speaker feedback incorporated, state-compliant positioning validated, absolutely no accidental routing to international platforms

---

### zh-SG Go-Live Checklist

**Target status:** Complete by Month 18 (Phase 5 launch).

#### Market Validation Prerequisite

- [ ] **Market research completed:** Validate whether zh-SG or en-US is higher ROI for Singapore market; if en-US significantly outperforms, deprioritize zh-SG production
- [ ] **Audience analysis:** English penetration in Singapore audiobook market; bilingual audience segmentation; preference data

#### Content (Conditional on Market Validation)

- [ ] Locale persona definitions written (LOCALE_PERSONAS.md, zh-SG personas: anxious_professional_sg, health_conscious_sg, gen_z_sg)
- [ ] Atoms directory created: atoms/zh-SG/ (fully populated with Simplified Chinese, Singapore cultural context, efficiency/practicality angle)
- [ ] All required (persona, topic) pairs have atom pools for 2 pilot brands (coverage gate 100% for pilot scope)
- [ ] Translation quality validated by native Singapore Chinese speaker review (Simplified script, Singapore English/Chinese code-switching cultural context)
- [ ] Location variable files populated for Singapore (Singapore city-state, urban density, multicultural context)
- [ ] Invisible script hook testing: native speaker validation of efficiency angle, cosmopolitan positioning, evidence-based framing

#### Technical (Conditional)

- [ ] locale_registry.yaml entry present and validated (locale: zh-SG, script: Simplified Chinese, tts_locale_code: zh-SG)
- [ ] brand_registry_locale_extension.yaml has 2 Phase 5 pilot brands (to be defined)
- [ ] content_roots_by_locale.yaml entry added for zh-SG
- [ ] CI gate #49 (locale_territory_consistency) passes for all zh-SG pilot books (locale: zh-SG, territory: SG, no US/mainland routing)
- [ ] TTS voice auditioned and approved (ElevenLabs zh-SG or fallback to zh-CN; Google Neural2 cmn-CN-Wavenet-A fallback)
- [ ] BookSpec locale/territory fields validated (locale: zh-SG, territory: SG)

#### Distribution (Conditional)

- [ ] Storefront accounts created for SG territory (Google Play SG, Findaway SG, Apple Books SG, Kobo SG, Spotify SG)
- [ ] Metadata schema validated for zh-SG (title, description, keywords in Simplified Chinese; efficiency, practicality, evidence-based language)
- [ ] Distribution routing rules verified (zh-SG: SG storefronts only; NOT mainland; NOT US)
- [ ] First 2 pilot brands with 7 books each (14 titles total) uploaded and approved on primary SG platforms
- [ ] ISBNs/ASINs assigned per book (SG ISBNs distinct from all other locales)

#### Marketing (Conditional)

- [ ] Invisible script research completed for zh-SG (efficiency, practicality, cosmopolitan identity, health consciousness, high English penetration)
- [ ] Title testing done (keyword research for Singapore market; validate efficiency angle, evidence-based positioning, cosmopolitan appeal)
- [ ] Platform category positioning confirmed (Spotify SG: Sleep/Wellness; Apple Books SG: Health/Wellness)
- [ ] Launch wave plan: 2-brand pilot (14 titles) → Singapore market validation → native speaker feedback → scale decision

#### Market Decision Gate (CRITICAL)

- [ ] **Before atoms production, validate:** Is zh-SG or en-US higher ROI? If en-US significantly outperforms in Singapore testing, PAUSE zh-SG production and invest marketing dollars in en-US instead. Do NOT produce zh-SG atoms if market data shows en-SG performs better.

#### Launch Status

- **Target:** Phase 5 pilot (conditional) by Month 18
- **Critical gate:** Market validation must confirm zh-SG viability before atoms investment
- **Success criteria (if proceeding):** 14 titles live, >80% reviews, efficiency/evidence-based positioning validated, English vs Chinese audience data collected for future strategy

---

## 4. Consolidated Readiness Tracker

This table shows the current status of each locale across the five key dimensions: Content, Technical, Distribution, Marketing, and Launch Status. Updated as of 2026-03-03.

| Locale | Content Ready | Technical Ready | Distribution Ready | Marketing Ready | Launch Status | Phase |
|--------|--------------|-----------------|-------------------|-----------------|---------------|-------|
| **en-US** | ✅ Partial (atoms 100%, pilot titles generated) | ✅ | ✅ US storefronts live | ✅ | **Wave 1 Active** (Seed Wave 50–75 titles in distribution) | 1 |
| **zh-TW** | 🔲 Phase 1 pilot atoms pending | 🔲 Brands defined, atoms in progress | 🔲 Storefront accounts pending | 🔲 Research in progress | **Planned Month 1–3** | 1 |
| **ja-JP** | 🔲 Phase 2 atoms pending | 🔲 Brands defined, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 4–6** | 2 |
| **ko-KR** | 🔲 Phase 3 atoms pending | 🔲 Brands defined, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 5–7** | 3 |
| **de-DE** | 🔲 Phase 4 atoms pending | 🔲 Brands defined, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 7–12** | 4 |
| **fr-FR** | 🔲 Phase 4 atoms pending | 🔲 Brands defined, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 7–12** | 4 |
| **hu-HU** | 🔲 Phase 4 atoms pending | 🔲 ElevenLabs validated (Google Neural2 NOT available) | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 7–12** | 4 |
| **es-US** | 🔲 Phase 4 atoms pending | 🔲 Brands defined, atoms pending | 🔲 US storefront routing prepared | 🔲 Research pending | **Planned Month 7–12** | 4 |
| **es-ES** | 🔲 Phase 4 atoms pending | 🔲 Brands defined, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 7–12** | 4 |
| **zh-HK** | 🔲 Phase 2–3 atoms pending | 🔲 Brands pending, atoms pending | 🔲 Storefront pending | 🔲 Research pending | **Planned Month 6–9** | 2–3 |
| **zh-CN** | 🔲 Phase 5 — PREREQUISITE: local platforms signed & compliance documented | 🔲 Local platform routing required (NO Google Play/Findaway) | 🔲 BLOCKED: Requires Ximalaya, NetEase, WeChat, Dedao accounts first | 🔲 Research pending compliance | **Planned Month 10–18** (Phase 5 LATEST) | 5 |
| **zh-SG** | 🔲 Phase 5 — CONDITIONAL on market validation | 🔲 Conditional on market decision | 🔲 Conditional on market decision | 🔲 Research pending | **Planned Month 12–18 (conditional)** | 5 |

**Key Legend:**
- ✅ = Complete and validated
- 🔲 = In progress or pending
- **Phase 1:** en-US (active), zh-TW (months 1–3)
- **Phase 2:** ja-JP (months 4–6), zh-HK companion track (months 6–9)
- **Phase 3:** ko-KR (months 5–7)
- **Phase 4:** de-DE, fr-FR, hu-HU, es-US, es-ES (months 7–12)
- **Phase 5:** zh-CN (months 10–18, blocked until local platform infrastructure), zh-SG (months 12–18, conditional on market validation)

---

## 5. What "100% Catalog" Means Per Locale — Operational Definition

### The Five Dimensions of 100% Readiness

A locale achieves 100% catalog status when it reaches green across all five dimensions:

#### 1. Content Completeness

**100% content** = All 24 brands × 42 books per brand = 1,008 titles localized, atom-backed, and reviewed by native speakers.

For pilot phases, 100% = all required atoms for pilot brands populated and validated (e.g., zh-TW Phase 1: 6 brands × 7 books = 42 titles, atoms 100% for those 6 brands).

**Validation:**
- All atoms in atoms/[locale]/ directory
- Coverage gate passing (all persona/topic/brand combinations have atoms)
- Native speaker review completed (translation quality, cultural fit, invisible script resonance)
- CI gate #49 (locale_territory_consistency) passing for all books in locale

#### 2. Technical Infrastructure

**100% technical** = Locale entry in all required configuration files; routing rules enforced; TTS voice tested and approved.

**Validation:**
- locale_registry.yaml entry present, validated (language, region, script, TTS provider, storefront_ids)
- brand_registry_locale_extension.yaml includes all locale brands
- content_roots_by_locale.yaml entry added
- BookSpec locale/territory fields validated for all books
- TTS voice auditioned and approved (primary and fallback providers)
- CI gate #49 passing (locale_territory_consistency, distribution routing validation)

#### 3. Distribution Readiness

**100% distribution** = Storefront accounts created for locale territory; first batch of books uploaded and approved on primary platforms.

**Validation:**
- Storefront accounts opened and tested (Google Play, Apple Books, Findaway, Spotify, Kobo, locale-specific platforms)
- Metadata schema validated for locale (title, description, keywords in locale language; no inappropriate cross-locale content)
- Distribution routing rules verified and enforced (e.g., zh-TW → TW storefronts only, no US)
- First 6–7 books per pilot brand (minimum 14 titles) uploaded, approved, and live on primary platform
- ISBNs/ASINs assigned and registered
- Payment/payout infrastructure validated

#### 4. Marketing Readiness

**100% marketing** = Invisible scripts researched and validated; title positioning tested; platform-specific category strategy confirmed; go-live communication plan drafted.

**Validation:**
- Invisible script research completed and approved by native speaker (cultural fit, resonance, psychological accuracy)
- High-value search keywords identified for locale language
- Title A/B testing completed OR keyword research validation showing positioning aligns with market search behavior
- Platform category positioning confirmed (Spotify: Sleep/Wellness vs. Apple Books: Self-Development, etc. by locale)
- Go-live communication plan drafted (launch announcement, influencer seeding, paid discovery)
- Competitive landscape analysis completed (which brands/titles compete in locale, differentiation strategy)

#### 5. Operational Launch Readiness

**100% launch** = Pilot wave deployed; native speaker feedback collection active; readiness to scale (or pause and iterate) decided.

**Validation:**
- Pilot wave (6–7 books per brand) live on primary platform
- Customer review/feedback collection mechanism in place
- Native speaker review cycle scheduled (4–6 weeks post-launch)
- Success metrics defined (>80% average rating, >100 reviews within 4 weeks, >X downloads/streams)
- Scale decision gate: if metrics met, proceed to next phase; if not, iterate based on feedback

### NOT 100% Until All Five Are Green

A locale is NOT ready to launch if:
- Atoms exist but marketing positioning hasn't been tested (missing dimension 4)
- Technical infrastructure is set up but storefront accounts aren't created (missing dimension 3)
- Storefront is live but TTS voice hasn't been auditioned (missing dimension 2)
- Marketing research is done but atoms haven't been created (missing dimension 1)

**All five dimensions must be complete and validated before go-live.**

---

## 6. Marketing Execution Notes

This section provides guidance on how to operationalize the marketing strategy across all locales.

### Title Philosophy Scaling

The title philosophy defined in TITLE_AND_CATALOG_MARKETING_SYSTEM.md (US baseline) scales to other locales with these modifications:

**US baseline (en-US):** Owns a search keyword (consumer language, not internal slug); names the invisible script precisely; carries brand voice (Calm vs Edge vs Rise vs Root); includes locale when city-specific.

**Per-locale scaling:**
1. **Search keyword owns locale language:** Translate the intent, not the word. Example: "nervous system reset" in en-US becomes "神經系統調整" (zh-TW), "神経系統リセット" (ja-JP), "신경계 조정" (ko-KR). These are NOT English keywords translated; they are native-language search terms the persona actually types.

2. **Invisible script is culture-specific:** The invisible script for a burned-out Taiwan software engineer (竹科 worker, 996-adjacent) is different from a New York executive (hustle culture reframe). Invisible scripts must be researched per locale, not imported from en-US.

3. **Brand voice carries imprint but is localized:** The imprint (Calm, Edge, Rise, Root) is consistent across locales, but word choice, tone, and framing adjust per culture. Example: "Calm" in en-US uses accessible, friendly language; "Calm" in de-DE uses science-grounded, formal language; "Calm" in fr-FR uses philosophical, existential framing.

4. **Avoid literal translation:** Never translate en-US titles directly to other locales. Example: "Nervous System Reset" (en-US) should NOT become a direct translation. Instead, research what the equivalent emotional need is in the locale, then title that. In ja-JP, the invisible script is about overcoming karoshi stigma, so the title might be "過労死文化を生き延びるための神経系統調整" (surviving karoshi culture through nervous system regulation) — completely different framing, same underlying emotion.

### Invisible Script Research Process Per Locale

Follow this process for each new locale:

1. **Deep research briefing review:** Study the relevant deep research briefs for the locale (from all_deep_research_omega integration). These briefs contain persona-specific invisible scripts, belief flips, and consumer language for the target market.

2. **Native speaker interviews (3–5 conversations):**
   - Interview therapists, coaches, or wellness practitioners in the locale
   - Ask: "What is the hidden belief your clients carry that keeps them stuck?"
   - Example questions:
     - Taiwan: "What do 竹科 workers believe about themselves when they can't sleep?"
     - Japan: "What's the unspoken shame around overwork in your culture?"
     - Germany: "What scientific proof do your clients need to trust wellness advice?"

3. **Market language research:**
   - Analyze search volume and search language for the locale (Google Trends, locale search tools)
   - Map consumer language (what people type vs. clinical terminology)
   - Identify high-opportunity search keywords

4. **Competitive landscape review:**
   - What titles, books, and creators already address this topic in the locale?
   - What positioning are they using?
   - Where is there a gap?

5. **Invisible script validation:**
   - Draft 2–3 possible invisible scripts based on research
   - Test with 10–15 target personas (survey, interviews, or focus group)
   - Select the one with highest resonance
   - Validate with native speaker reviewer before title generation

6. **Title generation and A/B testing:**
   - Generate titles based on validated invisible script
   - Test with target personas (short survey: "Which title would make you click?")
   - Measure click-through intent, not just preference
   - Lock top 5–10 validated title hooks; use these to guide atom content and marketing messaging

### Platform-Specific Keyword Research By Locale

Each platform has different category structures and search behaviors per locale. Conduct platform-specific research:

1. **Spotify:**
   - Category structure: Sleep, Focus, Wellness, Meditation, etc. (varies by locale)
   - Search keywords: "sleep," "relax," "anxiety," "meditation" (high-volume)
   - Positioning: Young audience, short-form friendly, discovery-driven
   - Strategy per locale: Lead with sleep/wellness categories; emphasize episode length and format

2. **Apple Books:**
   - Category structure: Mental Health, Self-Help, Health & Wellness, Psychology, etc.
   - Search keywords: Long-tail ("anxiety management," "burnout recovery," "sleep insomnia")
   - Positioning: Quality-conscious, literary, premium
   - Strategy per locale: Emphasize credibility, author expertise, sophistication of approach

3. **Google Play:**
   - Category structure: Health & Fitness, Audiobooks, Self-Help
   - Search keywords: Mix of high-volume and long-tail
   - Positioning: Accessibility, affordability, diversity
   - Strategy per locale: Broad category coverage; affordable pricing; focus on discoverability

4. **Audible (where available):**
   - Category structure: Health, Wellness, Psychology, Meditation, Spoken Word
   - Search keywords: Premium positioning; credibility-focused
   - Positioning: Narration quality matters; expert voice; subscription model
   - Strategy per locale: Emphasize narrator expertise; research credibility angle

5. **Locale-specific platforms:**
   - **Ximalaya (China):** Wellness category, longevity/health keywords, "抗衰老" high-volume
   - **Naver Audiobook (Korea):** Wellness, self-development, burnout, "번아웃" high-volume
   - **Kakao Page (Korea):** Entertainment-integrated, lifestyle
   - **WeChat Read (China):** Knowledge/content-ecosystem, premium positioning

### Review Cycle: Pilot → Validation → Scale

For each locale launch, follow this review cycle:

**Week 1–2 (Pre-launch):**
- Final native speaker review of all pilot titles (3–5 native speakers, 2+ reviews per title)
- Fix any language/cultural issues
- Lock final metadata and descriptions
- Upload to primary platform

**Week 3–6 (Pilot live):**
- Monitor customer reviews and ratings (target: >80% 4–5 stars, >100 reviews within 4 weeks)
- Collect direct feedback from native speakers in target persona groups
- Track downloads/streams (benchmark: 100–500 downloads per title per month for pilot phase)
- Document all feedback in locale-specific feedback log

**Week 7–10 (Validation):**
- Native speaker review meeting: discuss customer feedback, identify patterns
- If feedback is positive (>80% rating, positive sentiment in reviews):
  - Approve scale to next cohort of brands
  - Iterate content/titles based on specific feedback
  - Plan wave 2 expansion (next 6–12 brands)
- If feedback is mixed or negative:
  - Pause scale
  - Identify root causes (language, positioning, format, pricing)
  - Iterate atoms and titles
  - Retest with smaller second cohort

**Month 3–6 (Scale):**
- Launch Wave 2 (next set of brands)
- Expand to additional storefronts if primary platform validates well
- Begin marketing promotion (paid ads, influencer seeding, press coverage)

---

## 7. Launch Wave Sequencing by Phase

### Phase 1 (Months 1–3): en-US Seed Wave + zh-TW Pilot

- **en-US:** Seed Wave (50–75 Phoenix Drop titles) live on all US storefronts; ongoing feedback collection
- **zh-TW:** 6 pilot brands × 7 books = 42 titles live on TW storefronts; native speaker feedback collection active
- **Milestone (Week 12):** Decide scale decision for both locales; if >80% rating + >100 reviews, approve Phase 2 expansion

### Phase 2 (Months 4–6): ja-JP Pilot + zh-HK Companion (Months 6–9)

- **ja-JP:** 6 pilot brands × 7 books = 42 titles live on JP storefronts; native speaker feedback collection
- **zh-HK:** (Start Month 6) 4 pilot brands × 7 books = 28 titles live on HK storefronts; native speaker feedback collection
- **Milestone (Week 26):** ja-JP scale decision; decision on zh-HK viability

### Phase 3 (Months 5–7): ko-KR Pilot

- **ko-KR:** 4 pilot brands × 7 books = 28 titles live on KR storefronts; **A/B test:** micro-session format (15–30 min) vs. standard (30–45 min); measure completion rates
- **Milestone (Week 30):** ko-KR scale decision; micro-session format viability decision

### Phase 4 (Months 7–12): European Locales + Spanish

- **de-DE, fr-FR, hu-HU, es-US, es-ES:** Parallel launches (staggered by 2–4 weeks to manage localization capacity)
  - de-DE: 3 brands × 7 books = 21 titles
  - fr-FR: 2 brands × 7 books = 14 titles
  - hu-HU: 2 brands × 7 books = 14 titles
  - es-US: 3 brands × 7 books = 21 titles
  - es-ES: 2 brands × 7 books = 14 titles
- **Milestone (Week 52):** All Phase 4 locales scale decision

### Phase 5 (Months 10–18): China + Singapore

- **zh-CN:** (Months 10–18, BLOCKED until local platform accounts + compliance processes signed)
  - Prerequisite: Ximalaya, NetEase, WeChat Read, Dedao accounts open and tested; content review process documented
  - 6 pilot brands × 7 books = 42 titles; content review approval required before distribution
- **zh-SG:** (Months 12–18, CONDITIONAL on market validation)
  - Decision gate: If en-US testing shows higher ROI in Singapore, deprioritize zh-SG; shift investment to en-US marketing instead

**Total rollout timeline:** Month 1 (start) → Month 18 (completion of Phase 5, conditional). By Month 12, most locales have launched and begun scale phase.

---

## 8. Key Success Metrics and Monitoring

### Per-Locale Launch Metrics

For each locale pilot launch, monitor:

1. **Rating and review volume:**
   - Target: >80% 4–5 star rating within 4 weeks of launch
   - Minimum reviews required: 100 (demonstrates sustained engagement)
   - Competency threshold: If <70% rating or <50 reviews, pause and investigate

2. **Download/stream volume:**
   - Target: 100–500 downloads per title per month (pilot phase baseline)
   - Locale comparison: Compare zh-TW pilot downloads to en-US Seed Wave pacing
   - If significantly lower, investigate: language quality, marketing, positioning, or platform underperformance

3. **Completion rate (where available):**
   - For platforms that track it (Audible, some subscription services): measure % of listeners who complete books
   - Target: >60% completion rate (indicates content resonates, not just clicked)
   - ko-KR specific: Compare micro-session completion vs. standard format

4. **Native speaker feedback sentiment:**
   - Qualitative review of customer reviews and direct feedback from native speakers
   - Identify recurring themes: What works? What confuses? What resonates?
   - Document and feed back into atoms iteration

5. **Keyword performance:**
   - Track which search keywords drive most clicks per locale
   - Compare keyword targeting to research predictions
   - Adjust metadata and marketing messaging to lead with high-performing keywords

### Quarterly Readiness Reviews

Every 3 months (end of each phase), conduct a locale readiness review:

- **Content review:** Are atoms being produced on schedule? Are translation quality and native speaker feedback positive?
- **Technical review:** Are CI gates passing? Any distribution routing issues? TTS quality holding?
- **Distribution review:** Are storefronts processing uploads smoothly? Are ISBNs/ASINs assigning correctly? Are payment streams flowing?
- **Marketing review:** Are launch positioning and title strategy resonating? Are invisible scripts validated by market feedback?
- **Scale decision:** Based on metrics, should we scale to next wave, iterate, or pause?

---

## Appendix: Locale Rollout Decision Tree

Use this decision tree to determine readiness for each phase transition:

```
LOCALE READY TO LAUNCH PILOT?

1. Content dimension complete?
   - Atoms 100% populated and reviewed? YES → continue
   - NO → wait for atoms completion

2. Technical dimension complete?
   - locale_registry.yaml entry validated? YES → continue
   - CI gate #49 passing? YES → continue
   - NO → fix config and re-test

3. Distribution dimension complete?
   - Storefront accounts created and tested? YES → continue
   - First batch uploaded to primary platform? YES → continue
   - NO → open accounts and test upload workflow

4. Marketing dimension complete?
   - Invisible script researched and validated by native speaker? YES → continue
   - Title positioning tested? YES → continue
   - NO → conduct research and testing

5. All dimensions green?
   - YES → LAUNCH PILOT
   - NO → PAUSE and complete missing dimension

PILOT LIVE FOR 4–6 WEEKS. COLLECT NATIVE SPEAKER FEEDBACK.

READY TO SCALE?

1. Rating >80% on primary platform? YES → continue
2. >100 reviews within 4 weeks? YES → continue
3. Native speaker feedback positive (>70% sentiment)? YES → continue
4. Download/stream volume meets locale baseline? YES → continue

ALL METRICS GREEN? LAUNCH WAVE 2 (NEXT COHORT OF BRANDS)
METRICS MIXED OR RED? PAUSE AND ITERATE. FIX ROOT CAUSE (LANGUAGE, POSITIONING, OR MARKETING). RETEST.
```

---

## Appendix: Invisible Script Research Template

Use this template to document invisible script research per locale:

```
## [LOCALE] Invisible Script Research

### Market Context
- [Key cultural/economic factors shaping this market]

### Primary Invisible Scripts (Top 3)
1. **Script 1:** [Full statement, as if said by the target persona]
   - Belief flip (counter-intuitive reframe): [What flips this belief?]
   - Evidence: [What market research validates this script?]
   - Resonance validation: [Interview/survey data showing resonance]

2. **Script 2:** ...
3. **Script 3:** ...

### Persona-Specific Variants
- **[Persona 1]:** [Unique variant of invisible script for this persona]
- **[Persona 2]:** ...

### Consumer Language (Search Keywords & Phrases)
- High-volume keywords: [3–5 keywords + search volume]
- Long-tail keywords: [5–10 longer phrases]
- Phrases to avoid: [Cultural sensitivity alerts]

### Title Implications
- Title strategy: [How should titles embody this invisible script?]
- Example hooks (not full titles): [2–3 hook phrases]

### Platform Positioning Per Locale
- **[Platform 1]:** [Positioning angle, category strategy]
- **[Platform 2]:** ...

### Validation Status
- Native speaker review: [APPROVED / PENDING / REVISE]
- Market testing: [COMPLETE / PENDING]
- Ready to generate atoms: [YES / NO]
```

---

## Summary

This document provides the single, authoritative plan for Phoenix V4's 100% multi-locale expansion. It covers:

- **Catalog scope per locale** (table showing brand and title progression across 12 locales)
- **Marketing positioning per locale** (invisible scripts, keywords, platform strategy for each of the 12 locales)
- **Go-live checklists** (detailed, actionable checklist per locale; templates for content, technical, distribution, and marketing readiness)
- **Consolidated readiness tracker** (dashboard showing status of all locales across five dimensions)
- **Operational definitions** (what "100% ready" means; the five dimensions that must all be green)
- **Execution guidance** (how to scale title philosophy, research invisible scripts, test keywords, manage review cycles)

**Critical blockers by phase:**
- Phase 1 (zh-TW): Blocked until atoms/zh-TW fully populated and native speaker reviewed
- Phase 5 (zh-CN): BLOCKED until Ximalaya, NetEase, WeChat, Dedao accounts open and compliance processes documented
- Phase 5 (zh-SG): CONDITIONAL on market validation (if en-US outperforms zh-SG in Singapore, skip zh-SG; invest in en-US instead)

All go-live checklists are comprehensive, locale-specific, and cover content, technical, distribution, marketing, and launch readiness criteria. No locale proceeds to pilot without all five dimensions green.

