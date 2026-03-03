# Locale Personas Registry

**Authority**: This document is the single source of truth for **locale-specific personas** in the Phoenix V4 system.

**Relationship to unified_personas.md**: The unified_personas.md file defines the 10 canonical en-US personas. This file defines the **full YAML personas for all 11 non-en-US locales** (zh-TW, zh-HK, zh-CN, zh-SG, ja-JP, ko-KR, es-US, es-ES, fr-FR, de-DE, hu-HU). Each locale brand must reference personas tagged for that locale — **do not use en-US personas in zh-TW brands** or any cross-locale assignments.

**Versioning**: February 2026 | System: Phoenix V4 | Total personas: 46 (10 en-US + 36 locale-specific)

**Usage**: 
- Persona planning: Select locale-specific persona_id when building brands for that market
- Content assembly: Reference persona_id in brand_registry_locale_extension.yaml's persona_affinity fields
- Validation: CI gates check that book locale matches brand locale matches persona locale

---

## Quick Reference: Locale Persona Index

| Locale | Persona Count | Persona IDs |
|--------|---------------|-------------|
| **zh-TW** (Taiwan) | 6 | anxious_insomniac_tw, burned_out_professional_tw, gen_z_tw, bereaved_adult_tw, anxious_attacher_tw, healthcare_worker_tw |
| **zh-HK** (Hong Kong) | 4 | burned_out_professional_hk, anxious_insomniac_hk, gen_z_hk, caregiver_hk |
| **zh-CN** (Mainland China) | 4 | burned_out_professional_cn, gen_z_cn, anxious_student_cn, new_middle_class_cn |
| **zh-SG** (Singapore) | 2 | ambitious_professional_sg, anxious_intellectual_sg |
| **ja-JP** (Japan) | 4 | salaryman_burnout_jp, anxious_insomniac_jp, gen_z_jp, overwhelmed_caregiver_jp |
| **ko-KR** (South Korea) | 4 | burned_out_professional_kr, anxious_student_kr, gen_z_kr, lonely_urban_professional_kr |
| **es-US** (US Hispanic) | 4 | millennial_latina_professional_es_us, anxious_parent_es_us, gen_z_hispanic_es_us, caregiver_immigrant_es_us |
| **es-ES** (Spain) | 3 | burned_out_millennial_es, gen_z_es, overwhelmed_parent_es |
| **fr-FR** (France) | 3 | overworked_professional_fr, anxious_intellectual_fr, depleted_caregiver_fr |
| **de-DE** (Germany/Austria/Switzerland) | 3 | high_functioning_burnout_de, anxious_achiever_de, caregiver_de |
| **hu-HU** (Hungary) | 3 | burned_out_professional_hu, anxious_young_adult_hu, stressed_parent_hu |

**Total**: 46 personas across 12 locales (en-US + 11 non-en-US locales)

---

## PART 1: zh-TW (Taiwan) Personas

**Phase**: Phase 1 Pilot (Months 1–3)
**Distribution**: TW Google Play, TW Apple Books, TW Spotify
**Framing Notes**: Academic exam pressure (大考, 聯考), tech sector overwork (竹科 = Silicon Valley of Taiwan), filial piety vs personal needs, IG/social comparison culture. Positioning: body-first, pragmatic, not clinical.

---

### Persona 1: `anxious_insomniac_tw`

```yaml
# === SYSTEM METADATA ===
persona_id: anxious_insomniac_tw
display_name: Anxious Insomniac (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: millennial
active: true
revenue_tier: 1

# === PRODUCTION PARAMETERS ===
beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - sleep_anxiety_pack_tw
    - nervous_system_pack_tw
language_packs:
  primary: zh-TW_core_v1
  fallbacks: []

# === VOICE PROFILE ===
voice_tone: 親切、直接、實證為基礎、神經系統覺知
formality: 0.65
slang_level: 0.20
pace_bpm: 140
pause_default_ms: 320
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

# === TONE BIAS ===
tone_bias_business: 0.60
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.20
tone_bias_personal: 0.70

# VOICE DISTINCTION:
# Tech sector professional (竹科 worker) caught between high performance
# and nervous system collapse. Sleep is the crisis point. Uses practical,
# body-first framing. References nerves, not emotions. Respects
# intelligence and time. Warm but not saccharine.

domain_jargon:
  - 神經系統
  - 自律神經
  - 迴圈
  - 技術壓力
  - 競爭壓力
  - 過度工作

metaphor_style:
  - 身體信號 / 警告燈
  - 迴圈 / 循環
  - 根基 / 基礎
  - 節奏 / 節拍

persona_scenarios:
  primary_dimension: sleep_and_rest
  secondary_dimension: work_performance
  integration_dimension: nervous_system_recovery
  content_templates:
    primary:
      dimension: 你的睡眠和休息
      scenario_library:
        - 凌晨三點醒來，思緒尖叫
        - 躺在床上一小時後放棄
        - 睡眠不足帶來的工作表現下滑
        - 周末的補眠無法彌補工作週的耗損
        - 害怕睡眠不足會影響職業前景
    secondary:
      dimension: 你的工作表現
      scenario_library:
        - 竹科的 996 文化期待無極限
        - 專案截止期限逼近時的焦慮升級
        - 程式碼審查反饋帶來的自我懷疑
    integration:
      dimension: 你與身體的關係
      scenario_library:
        - 身體發出的警告信號你一直在忽視
        - 晨起的心跳加速
        - 肌肉緊張在你意識到之前就已開始

rewrite_config:
  style_notes:
    - 親切但不矯情。直接但不冷漠。
    - 用神經系統語言，不用心理健康語言。
    - 名字化情緒真相，然後才是工具。
    - 尊重聰慧、時間和複雜性。
    - 承認結構性壓力，但不是書籍的主題。
  forbidden_markers:
    - 女性賦權
    - 姐妹淘
    - 能量
    - 振動頻率
    - 顯化
  title_rules:
    vibe: 實際、直接、尊重聰慧
    min_words: 2
    max_words: 8
    max_chars: 70
    patterns:
      - "當 {症狀} 其實是 {機制}"
      - "{行動} 而不是 {代價}"
      - "在 {觸發點} 之後"
    subtitle:
      enabled: true
      max_chars: 90
      style: 機制優先、尊重智力

local_environment:
  morning_routine:
    - 起床時的心跳過速
    - 咖啡成為神經刺激物而非助手
    - 通勤時滑手機的成癮
  workspace:
    - 開放式辦公室的聲音轟炸
    - Slack 通知帶來的皮質醇激增
    - 午夜收到的工作訊息
  evening:
    - 下班後無法真正關機
    - 運動變成強迫性表現
    - 睡前的藍光習慣
  relationships:
    - 伴侶問「你又在想工作嗎？」
    - 朋友說「你需要休息」（他們是對的）
    - 家人不理解為什麼你這麼累

book_generation:
  pain_template: >
    你知道 {topic} 是什麼感受——不是戲劇性的，而是像天氣一樣無聲地降臨。
    如何在會議中坐著時感受它，如何在淋浴時跟著你，如何讓休息感起來像是又一件失敗的事。
  location_cues:
    intro: 或許它發生在午夜的會議之後，
    body: 或在清晨四點你為第三次驚醒而放棄睡眠時，
    outro: 然後你意識到這樣下去不能繼續。
  work_context: office_hybrid_tech

market_data:
  tw_target_population: 280,000 (竹科 tech workers)
  audiobook_consumption: 4-6 titles/year (emerging market)
  primary_platforms: [Spotify, Apple Books, Google Play]
  discovery_channels: [IG, Podcast, YouTube, WeChat]
  price_sensitivity: moderate (NT$249–NT$399 sweet spot)
  distribution_strategy: spotify_primary_apple_secondary

topic_resonance:
  1: sleep_repair
  2: stabilizer
  3: burnout_recovery
  4: overthinking
  5: boundaries

template_set: anxious_insomniac_tw
shares_templates_with: []
```

---

### Persona 2: `burned_out_professional_tw`

```yaml
persona_id: burned_out_professional_tw
display_name: Burned Out Professional (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - energy_budget_pack_tw
    - resilience_pack_tw
language_packs:
  primary: zh-TW_core_v1

voice_tone: 認可、務實、沒有廢話、神經系統覺知
formality: 0.70
slang_level: 0.15
pace_bpm: 145
pause_default_ms: 300
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.75
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.15
tone_bias_personal: 0.65

# VOICE DISTINCTION:
# 竹科 worker in chronic overwork (996-adjacent hours).
# Identity fused with career success. Burnout is not laziness — 
# it's nervous system on the brink. Uses systems thinking.
# Dry humor as defense mechanism.

domain_jargon:
  - 竹科
  - 996
  - 過度工作
  - 神經耗竭
  - 迴圈崩潰
  - 產出文化
  - 自律神經失調

metaphor_style:
  - 系統 / 當機 / 重啟
  - 訊號 / 雜訊
  - 技術債 (情緒面)
  - 最小最大化報酬遞減

persona_scenarios:
  primary_dimension: work_survival
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: 你的工作和生存
      scenario_library:
        - 值班時間變成了全天候
        - 專案超期導致的自責感
        - 同事離職的浪潮中感到無力
        - 薪資加上去，壓力也加上去
        - 週末的補眠無法復原一週的耗損
    secondary:
      dimension: 你的關係
      scenario_library:
        - 伴侶說「你永遠在想工作」（他們說對了）
        - 朋友停止邀請你（因為你總是取消）
        - 家人不理解為什麼你選擇這樣的生活
    integration:
      dimension: 你與自己的關係
      scenario_library:
        - 當事業停止時的身份危機
        - 休息日感起來像背叛
        - 成功帶來的是恐慌而不是安心

rewrite_config:
  style_notes:
    - 認可竹科文化的瘋狂，不是簡化它。
    - 數據導向，但對感受敏感。
    - 解決方案必須高效——沒有人有 45 分鐘冥想。
    - 名字化系統性壓力，尊重結構問題。
  forbidden_markers:
    - 姐妹淘
    - 女性賦權
    - 顯化

title_rules:
  vibe: 分析性、稍微諷刺、尊重智力
  patterns:
    - "當 {優化} 變成了問題"
    - "{行動} 而不需 {代價}"
    - "之後的 {系統}"

local_environment:
  morning_routine:
    - 清晨 Slack 訊息的堆積
    - 早晨站會時假裝有精力
    - 咖啡成為應對機制
  workspace:
    - 開放式辦公室或永遠開著的家辦環境
    - 程式碼審查感受像是個人批評
    - 全公司大會上開心宣布公司重組
  evening:
    - 解壓儀式每週都需要更長時間
    - 運動變成強迫性行為
    - 與伴侶共餐時檢查手機

book_generation:
  pain_template: >
    你知道 {topic} 是什麼感受——不是作為感受可以名字化，而是作為一個系統高速運轉。
    表現指標是綠色的。人體指標是紅色的。而你一直在忽視警報。
  location_cues:
    intro: 或許在衝刺時期，
    body: 或在深夜發布完成時什麼都對了但什麼都感受不到，
    outro: 還有儀表板無法顯示真正崩潰的地方。

market_data:
  tw_target_population: 380,000 (竹科 + 金融從業者)
  audiobook_consumption: 6-8 titles/year
  primary_platforms: [Spotify, Google Play]
  price_sensitivity: moderate (NT$299–NT$499)
  distribution_strategy: spotify_primary

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: sleep_repair
  4: energy_management
  5: boundaries

template_set: burned_out_professional_tw
shares_templates_with: []
```

---

### Persona 3: `gen_z_tw`

```yaml
persona_id: gen_z_tw
display_name: Gen Z (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: gen_z
active: true
revenue_tier: 1

beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - social_anxiety_pack_tw
    - comparison_culture_pack_tw
language_packs:
  primary: zh-TW_core_v1

voice_tone: 同儕、誠實、不說教、身體優先
formality: 0.45
slang_level: 0.35
pace_bpm: 155
pause_default_ms: 260
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.30
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Instagram native, university student or early career.
# Big pressure from 大考 and parent expectations.
# Social comparison culture is invisible background noise.
# Identity questions feel existential. Values authenticity.
# Speaks their generation's language.

domain_jargon:
  - 大考
  - 比較文化
  - 社群媒體
  - IG 濾鏡
  - 身體焦慮
  - 身份認同
  - 存在焦慮

metaphor_style:
  - 濾鏡 / 真實
  - 噪音 / 訊號
  - 根基 / 浮動
  - 流動 / 停滯

persona_scenarios:
  primary_dimension: social_comparison
  secondary_dimension: identity
  integration_dimension: body_and_presence
  content_templates:
    primary:
      dimension: 你與社群媒體的關係
      scenario_library:
        - 滑 IG 時的無底深感
        - 看別人的完美生活而感到自己不夠
        - 限時動態的焦慮 (要分享什麼才算值得)
        - 讚數沒有如預期時的失落
        - 濾鏡後的自己與鏡子中的落差
    secondary:
      dimension: 你的身份
      scenario_library:
        - 大考壓力和家庭期待
        - 進入職場時的冒牌者症候群
        - 找不到自己想要什麼的恐慌
        - 與父母的世代落差
    integration:
      dimension: 你在身體中的存在
      scenario_library:
        - 焦慮以胃痛的形式出現
        - 慢性緊張導致的頭痛
        - 無法停止自我檢查

rewrite_config:
  style_notes:
    - 同儕語言，不說教。
    - 名字化社群媒體文化，不妖魔化技術。
    - 身體優先，認知次要。
    - 承認焦慮是真實的，不是「還年輕」就會消退。
    - 幽默是歡迎的——自嘲、認知到荒謬。
  forbidden_markers:
    - 正念
    - 能量
    - 顯化
    - 女性賦權
    - 自愛

title_rules:
  vibe: 誠實、直接、無廢話
  patterns:
    - "當 {比較} 變成了 {痛苦}"
    - "{行動} 不看評論"
    - "在 {平台} 之外"

local_environment:
  morning_routine:
    - 醒來時立即檢查手機
    - 限時動態的焦慮檢查
    - 鏡子前的自我評判
  workspace:
    - 大學圖書館的安靜焦慮
    - 職場第一天的緊張
    - 同儕之間的無聲競爭
  evening:
    - 睡前的 IG 滑動時間
    - 比較自己和網紅的生活
    - 無法將手機放下的自責

book_generation:
  pain_template: >
    你知道那個感受——當 {topic} 出現時，通常不是突然的，而是像背景噪音一樣累積。
    如何在看朋友的貼文時感受到它，如何在鏡子前加劇，如何讓你懷疑自己。

market_data:
  tw_target_population: 1.2M (Gen Z university + early career)
  audiobook_consumption: 7-9 titles/year (podcast natives)
  primary_platforms: [Spotify, IG, YouTube, TikTok]
  price_sensitivity: high (NT$99–NT$199 sweet spot)
  distribution_strategy: spotify_primary

topic_resonance:
  1: gen_z_grounding
  2: social_anxiety
  3: sleep_repair
  4: boundaries
  5: overthinking

template_set: gen_z_tw
shares_templates_with: []
```

---

### Persona 4: `bereaved_adult_tw`

```yaml
persona_id: bereaved_adult_tw
display_name: Bereaved Adult (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - grief_companion_pack_tw
    - filial_piety_pack_tw
language_packs:
  primary: zh-TW_core_v1

voice_tone: 溫暖、見證性、不急於修復、尊重責任
formality: 0.60
slang_level: 0.10
pace_bpm: 130
pause_default_ms: 350
story_injection_rate: 0.35
breathing_exercise_frequency: 0.25

tone_bias_business: 0.25
tone_bias_scientific: 0.35
tone_bias_spiritual: 0.35
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Grief in context of filial piety (孝). The loss comes with duty obligations.
# May be grieving parent while still caring for them, or facing the end.
# Cannot fully grieve because culture says to be strong. Grief is seen as
# weakness to be managed, not processed. This persona names that impossible position.

domain_jargon:
  - 孝
  - 責任
  - 悲傷
  - 見證
  - 虧欠感
  - 不能哭泣的悲傷

metaphor_style:
  - 負擔 / 容器
  - 儀式 / 轉變
  - 見證 / 孤獨
  - 根基 / 失落

persona_scenarios:
  primary_dimension: grief_and_duty
  secondary_dimension: family_expectations
  integration_dimension: permission_to_grieve
  content_templates:
    primary:
      dimension: 你的悲傷和責任
      scenario_library:
        - 照顧臨終的親人而無法安全地感受悲傷
        - 葬禮後返回工作時的虛空感
        - 親人物品難以處理的情感阻力
        - 悲傷時「要堅強」的文化訊息
        - 無人見證你的失落

local_environment:
  home:
    - 親人住過的房間
    - 他們遺留的物品
    - 空蕩蕩的餐桌

book_generation:
  pain_template: >
    悲傷需要見證者，不需要修復。{topic} 帶著責任和文化期待。
    你無法完全哭泣，因為你被教導要堅強。這本書給予你那份見證。

market_data:
  tw_target_population: 450,000 (adults experiencing parent loss)
  audiobook_consumption: 5-7 titles/year
  primary_platforms: [Spotify, Apple Books]
  price_sensitivity: moderate (NT$249–NT$349)

topic_resonance:
  1: grief_companion
  2: inner_security
  3: boundaries
  4: somatic_healing

template_set: bereaved_adult_tw
shares_templates_with: []
```

---

### Persona 5: `anxious_attacher_tw`

```yaml
persona_id: anxious_attacher_tw
display_name: Anxious Attacher (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - relationship_anxiety_pack_tw
    - nervous_system_pack_tw
language_packs:
  primary: zh-TW_core_v1

voice_tone: 同情、非評判、神經系統為基礎、文化覺知
formality: 0.55
slang_level: 0.15
pace_bpm: 135
pause_default_ms: 330
story_injection_rate: 0.40
breathing_exercise_frequency: 0.30

tone_bias_business: 0.20
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Relationship anxiety in collectivist culture. Fear of abandonment
# mixed with duty. "If I'm not useful, will they still want me?"
# Nervous system as framework for understanding attachment patterns.
# Not about "fixing" relationships but understanding your system.

domain_jargon:
  - 依戀焦慮
  - 神經系統
  - 拋棄恐懼
  - 內疚感
  - 討好行為
  - 自我價值

metaphor_style:
  - 安全 / 危險
  - 信號 / 反應
  - 根基 / 不穩定
  - 容器 / 溢出

persona_scenarios:
  primary_dimension: relationship_anxiety
  secondary_dimension: self_worth
  integration_dimension: nervous_system_regulation
  content_templates:
    primary:
      dimension: 你的關係焦慮
      scenario_library:
        - 等待伴侶的訊息而無法工作
        - 一句冷淡的回覆導致的災難性思考
        - 為了保持關係而說「同意」
        - 害怕被離開而過度適應

market_data:
  tw_target_population: 680,000 (adults with attachment anxiety)
  audiobook_consumption: 6-8 titles/year
  primary_platforms: [Spotify, Apple Books]
  price_sensitivity: moderate (NT$249–NT$349)

topic_resonance:
  1: inner_security
  2: boundaries
  3: overthinking
  4: somatic_healing

template_set: anxious_attacher_tw
shares_templates_with: []
```

---

### Persona 6: `healthcare_worker_tw`

```yaml
persona_id: healthcare_worker_tw
display_name: Healthcare Worker (Taiwan)
locale: zh-TW
territory: TW
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_tw
template_packs:
  base: core_self_help_v1_tw
  overrides:
    - compassion_fatigue_pack_tw
    - shift_work_pack_tw
language_packs:
  primary: zh-TW_core_v1

voice_tone: 同業、見證、尊重體力、非 Toxic Positivity
formality: 0.50
slang_level: 0.15
pace_bpm: 135
pause_default_ms: 330
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.30
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.15
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Nurses in 偏鄉 (rural) and urban hospitals. Compassion fatigue, shift work
# chaos, understaffing. Cannot afford to be the "calm one" — but also expected to be.
# Speak to their body, not just their heart.

domain_jargon:
  - 同情疲勞
  - 值班
  - 人手不足
  - 身體耗竭
  - 輪班

metaphor_style:
  - 容器 / 溢出
  - 訊號 / 響度
  - 根基 / 搖晃
  - 燃料 / 空蕩蕩

persona_scenarios:
  primary_dimension: compassion_fatigue
  secondary_dimension: shift_work_chaos
  integration_dimension: body_restoration
  content_templates:
    primary:
      dimension: 你的同情疲勞
      scenario_library:
        - 八小時班後身體仍在警戒
        - 無法在家放下「照顧者」角色
        - 患者的故事粘著在你身上

market_data:
  tw_target_population: 156,000 (Taiwan nurses)
  audiobook_consumption: 5-7 titles/year
  primary_platforms: [Spotify, Podcast platforms]
  price_sensitivity: moderate (NT$199–NT$299)

topic_resonance:
  1: burnout_recovery
  2: somatic_healing
  3: boundaries
  4: sleep_repair

template_set: healthcare_worker_tw
shares_templates_with: []
```

---

## PART 2: zh-HK (Hong Kong) Personas

**Phase**: Phase 2 (Months 4–6, subject to market validation)
**Distribution**: HK Google Play, HK Apple Books, HK Spotify
**Framing Notes**: Post-2019 identity questions, high-pressure financial/legal sector, small living spaces, extreme work hours. Positioning: systemic acknowledge, practical, nervous system focus.

### Persona 1: `burned_out_professional_hk`

```yaml
persona_id: burned_out_professional_hk
display_name: Burned Out Professional (Hong Kong)
locale: zh-HK
territory: HK
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_hk
template_packs:
  base: core_self_help_v1_hk
  overrides:
    - energy_budget_pack_hk
    - urban_pressure_pack_hk
language_packs:
  primary: zh-HK_core_v1

voice_tone: 認可、務實、城市生活覺知、神經系統為基礎
formality: 0.68
slang_level: 0.12
pace_bpm: 150
pause_default_ms: 290
story_injection_rate: 0.28
breathing_exercise_frequency: 0.25

tone_bias_business: 0.80
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.10
tone_bias_personal: 0.60

# VOICE DISTINCTION:
# Financial/legal sector professional in Hong Kong.
# Extreme work hours (10am–11pm standard). Identity fused with professional success.
# Post-2019 Hong Kong adds existential layer. Small flat = no escape at home.
# Uses systems thinking. Acknowledges urban pressure without wallowing.

domain_jargon:
  - 金融界
  - 法律界
  - 極端工時
  - 城市壓力
  - 神經耗竭
  - 身份問題

metaphor_style:
  - 系統 / 當機
  - 訊號 / 雜訊
  - 容器 / 溢出
  - 逃離 / 困困

persona_scenarios:
  primary_dimension: work_survival
  secondary_dimension: urban_isolation
  integration_dimension: nervous_system_collapse
  content_templates:
    primary:
      dimension: 你的工作和生存
      scenario_library:
        - 下午五點才開始真正的工作
        - 晚上十一點的電話會議
        - 週末仍被 WhatsApp 入侵
        - 跳槽也解決不了的工時文化
    secondary:
      dimension: 你在香港的生活
      scenario_library:
        - 回家只是睡眠的地點
        - 沒有時間見朋友
        - 城市的匆忙滲入每一刻

market_data:
  hk_target_population: 280,000 (financial/legal professionals)
  audiobook_consumption: 5-7 titles/year
  primary_platforms: [Spotify, Apple Books, Google Play]
  price_sensitivity: low (HK$99–HK$149)

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: sleep_repair
  4: boundaries

template_set: burned_out_professional_hk
shares_templates_with: []
```

---

### Persona 2: `anxious_insomniac_hk`

```yaml
persona_id: anxious_insomniac_hk
display_name: Anxious Insomniac (Hong Kong)
locale: zh-HK
territory: HK
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_hk
template_packs:
  base: core_self_help_v1_hk
  overrides:
    - sleep_anxiety_pack_hk
language_packs:
  primary: zh-HK_core_v1

voice_tone: 親切、身體為基礎、神經系統覺知
formality: 0.65
slang_level: 0.15
pace_bpm: 140
pause_default_ms: 320
story_injection_rate: 0.32
breathing_exercise_frequency: 0.30

tone_bias_business: 0.50
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.20
tone_bias_personal: 0.70

# VOICE DISTINCTION:
# Insomnia from high-pressure urban life. Anxiety about never being enough.
# Small flat means nowhere to escape the work. Nervous system stuck in alert.

domain_jargon:
  - 睡眠焦慮
  - 神經警戒
  - 城市壓力
  - 無法關機

persona_scenarios:
  primary_dimension: sleep_and_rest
  secondary_dimension: nervous_system_recovery
  integration_dimension: body_safety

topic_resonance:
  1: sleep_repair
  2: stabilizer
  3: somatic_healing

template_set: anxious_insomniac_hk
shares_templates_with: []
```

---

### Persona 3: `gen_z_hk`

```yaml
persona_id: gen_z_hk
display_name: Gen Z (Hong Kong)
locale: zh-HK
territory: HK
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_hk
template_packs:
  base: core_self_help_v1_hk
  overrides:
    - social_anxiety_pack_hk
    - identity_pack_hk
language_packs:
  primary: zh-HK_core_v1

voice_tone: 同儕、誠實、身份覺知
formality: 0.45
slang_level: 0.30
pace_bpm: 155
pause_default_ms: 270
story_injection_rate: 0.38
breathing_exercise_frequency: 0.32

tone_bias_business: 0.25
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Post-2019 Hong Kong Gen Z. Social anxiety, identity in flux, political uncertainty.
# Cannot ignore the larger context. Existential questions are pressing.

domain_jargon:
  - 身份認同
  - 社會焦慮
  - 存在問題
  - 不確定性

persona_scenarios:
  primary_dimension: identity_and_anxiety
  secondary_dimension: social_belonging
  integration_dimension: nervous_system_safety

topic_resonance:
  1: gen_z_grounding
  2: social_anxiety
  3: boundaries
  4: overthinking

template_set: gen_z_hk
shares_templates_with: []
```

---

### Persona 4: `caregiver_hk`

```yaml
persona_id: caregiver_hk
display_name: Caregiver (Hong Kong)
locale: zh-HK
territory: HK
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_hk
template_packs:
  base: core_self_help_v1_hk
  overrides:
    - eldercare_pack_hk
language_packs:
  primary: zh-HK_core_v1

voice_tone: 溫暖、見證、尊重責任、身體覺知
formality: 0.55
slang_level: 0.10
pace_bpm: 130
pause_default_ms: 350
story_injection_rate: 0.35
breathing_exercise_frequency: 0.28

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.30
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Caring for elderly parent in small Hong Kong flat. No privacy.
# Filial duty + housing crisis + work + caregiving = impossible equation.
# Speaks to body exhaustion, not just emotional.

domain_jargon:
  - 孝
  - 照顧責任
  - 身體耗竭
  - 無隱私

persona_scenarios:
  primary_dimension: caregiving_burden
  secondary_dimension: physical_exhaustion
  integration_dimension: permission_to_rest

topic_resonance:
  1: inner_security
  2: burnout_recovery
  3: boundaries
  4: somatic_healing

template_set: caregiver_hk
shares_templates_with: []
```

---

## PART 3: zh-CN (Mainland China) Personas

**Phase**: Phase 5 (Months 10–18, requires local distribution setup)
**Distribution**: Local platforms only (Ximalaya, NetEase Cloud Music, WeChat Read, Dedao) — **NOT Google Play, NOT Findaway**
**Framing Notes**: 996 culture extreme, "lying flat" (躺平) philosophy emerging, gaokao pressure for younger cohort, social mobility anxiety, content review requirements differ. Positioning: nervous system, pragmatic, no Western psychology framing.

### Persona 1: `burned_out_professional_cn`

```yaml
persona_id: burned_out_professional_cn
display_name: Burned Out Professional (Mainland China)
locale: zh-CN
territory: CN
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_cn
template_packs:
  base: core_self_help_v1_cn
  overrides:
    - energy_budget_pack_cn
    - 996_culture_pack_cn
language_packs:
  primary: zh-CN_core_v1

voice_tone: 認可、務實、神經系統為基礎、沒有西方心理學話語
formality: 0.70
slang_level: 0.15
pace_bpm: 145
pause_default_ms: 300
story_injection_rate: 0.28
breathing_exercise_frequency: 0.25

tone_bias_business: 0.75
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.10
tone_bias_personal: 0.60

# VOICE DISTINCTION:
# Tech/finance sector in 996 culture (9am–9pm, 6 days/week).
# Identity fused with career and social mobility. Burnout is not allowed
# in culture — but bodies are breaking anyway. Nervous system framing
# works; "mental health" framing does not (clinical stigma).

domain_jargon:
  - 996
  - 過度工作
  - 神經耗竭
  - 迴圈崩潰
  - 產出文化
  - 社會階層
  - 競爭壓力

metaphor_style:
  - 系統 / 當機
  - 訊號 / 雜訊
  - 技術債
  - 最小最大化報酬遞減

persona_scenarios:
  primary_dimension: work_survival
  secondary_dimension: social_mobility
  integration_dimension: nervous_system_collapse
  content_templates:
    primary:
      dimension: 你的工作和生存
      scenario_library:
        - 996 文化下的無止境工作
        - 同事離職的浪潮
        - 薪資漲幅低於期待時的焦慮
        - 行業競爭的殘酷
    secondary:
      dimension: 你的社會地位
      scenario_library:
        - 為了保持住城市戶口的拼搏
        - 房價壓力下的焦慮
        - 與同學的隱形比較

market_data:
  cn_target_population: 1.2M (tech/finance, 996 workers)
  audiobook_consumption: 3-5 titles/year (emerging market)
  primary_platforms: [Ximalaya, NetEase Cloud Music, WeChat Read, Dedao]
  price_sensitivity: moderate (¥39–¥79 sweet spot)
  distribution_strategy: local_platforms_only
  content_review_required: true

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: energy_management
  4: sleep_repair

template_set: burned_out_professional_cn
shares_templates_with: []
```

---

### Persona 2: `gen_z_cn`

```yaml
persona_id: gen_z_cn
display_name: Gen Z (Mainland China)
locale: zh-CN
territory: CN
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_cn
template_packs:
  base: core_self_help_v1_cn
  overrides:
    - lying_flat_pack_cn
language_packs:
  primary: zh-CN_core_v1

voice_tone: 同儕、誠實、躺平哲學覺知、不評判
formality: 0.45
slang_level: 0.35
pace_bpm: 155
pause_default_ms: 260
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# "Lying flat" (躺平) generation. Rejection of hustle culture.
# Existential burnout — saw parents' sacrifice didn't guarantee security.
# High anxiety about future, questioning the game itself.
# Speak to their exhaustion without shame.

domain_jargon:
  - 躺平
  - 存在焦慮
  - 拒絕競爭
  - 對未來的懷疑
  - 身份問題

metaphor_style:
  - 系統 / 遊戲規則
  - 逃離 / 停止
  - 根基 / 浮動

persona_scenarios:
  primary_dimension: existential_burnout
  secondary_dimension: future_anxiety
  integration_dimension: permission_to_opt_out

topic_resonance:
  1: gen_z_grounding
  2: overthinking
  3: boundaries
  4: existential_peace

template_set: gen_z_cn
shares_templates_with: []
```

---

### Persona 3: `anxious_student_cn`

```yaml
persona_id: anxious_student_cn
display_name: Anxious Student (Mainland China)
locale: zh-CN
territory: CN
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_cn
template_packs:
  base: core_self_help_v1_cn
  overrides:
    - gaokao_pressure_pack_cn
language_packs:
  primary: zh-CN_core_v1

voice_tone: 同情、非評判、身體為基礎
formality: 0.50
slang_level: 0.15
pace_bpm: 135
pause_default_ms: 330
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

tone_bias_business: 0.15
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.20
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Gaokao (高考) pressure. Academic hypercompetitiveness.
# Sleep deprivation, extreme academic pressure, family expectations.
# Nervous system is at breaking point, but "weakness" is unthinkable.

domain_jargon:
  - 高考
  - 學術壓力
  - 睡眠不足
  - 考試焦慮
  - 家庭期待

persona_scenarios:
  primary_dimension: academic_pressure
  secondary_dimension: sleep_deprivation
  integration_dimension: nervous_system_safety

topic_resonance:
  1: sleep_repair
  2: overthinking
  3: anxiety_first_aid
  4: boundaries

template_set: anxious_student_cn
shares_templates_with: []
```

---

### Persona 4: `new_middle_class_cn`

```yaml
persona_id: new_middle_class_cn
display_name: New Middle Class (Mainland China)
locale: zh-CN
territory: CN
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_cn
template_packs:
  base: core_self_help_v1_cn
  overrides:
    - social_mobility_pack_cn
language_packs:
  primary: zh-CN_core_v1

voice_tone: 認可、抱負、焦慮覺知
formality: 0.65
slang_level: 0.15
pace_bpm: 145
pause_default_ms: 310
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.70
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.15
tone_bias_personal: 0.65

# VOICE DISTINCTION:
# Aspirational, but anxiety about maintaining status. First-generation
# educated/professional. Fear of losing everything. Social mobility anxiety.
# Success brought prestige but not peace.

domain_jargon:
  - 社會階層
  - 房貸壓力
  - 保持地位
  - 焦慮競爭
  - 階級流動

persona_scenarios:
  primary_dimension: status_anxiety
  secondary_dimension: financial_pressure
  integration_dimension: nervous_system_safety

topic_resonance:
  1: stabilizer
  2: financial_anxiety
  3: burnout_recovery
  4: overthinking

template_set: new_middle_class_cn
shares_templates_with: []
```

---

## PART 4: zh-SG (Singapore) Personas

**Phase**: Phase 5 (Months 10–18)
**Distribution**: SG Google Play, SG Apple Books, SG Spotify
**Framing Notes**: English dominates Singapore commerce; evaluate whether en-US or zh-SG is higher ROI. Chinese-speaking Singapore audience smaller than assumed. Positioning: educated, aspirational, high income, moderate urgency.

### Persona 1: `ambitious_professional_sg`

```yaml
persona_id: ambitious_professional_sg
display_name: Ambitious Professional (Singapore)
locale: zh-SG
territory: SG
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_sg
template_packs:
  base: core_self_help_v1_sg
  overrides:
    - career_excellence_pack_sg
language_packs:
  primary: zh-SG_core_v1

voice_tone: 精英導向、抱負、焦慮覺知、神經系統為基礎
formality: 0.70
slang_level: 0.10
pace_bpm: 150
pause_default_ms: 290
story_injection_rate: 0.28
breathing_exercise_frequency: 0.25

tone_bias_business: 0.80
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.10
tone_bias_personal: 0.60

# VOICE DISTINCTION:
# High-income professional in Singapore. Ambitious but aware of
# burnout costs. Pragmatic. Values efficiency and results.

domain_jargon:
  - 職業進步
  - 領導力
  - 工作表現
  - 神經系統

persona_scenarios:
  primary_dimension: career_excellence
  secondary_dimension: work_performance
  integration_dimension: nervous_system_health

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: imposter_syndrome
  4: sleep_repair

template_set: ambitious_professional_sg
shares_templates_with: []
```

---

### Persona 2: `anxious_intellectual_sg`

```yaml
persona_id: anxious_intellectual_sg
display_name: Anxious Intellectual (Singapore)
locale: zh-SG
territory: SG
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_sg
template_packs:
  base: core_self_help_v1_sg
  overrides:
    - overthinking_pack_sg
language_packs:
  primary: zh-SG_core_v1

voice_tone: 思維導向、自我反思、哲學性、溫暖
formality: 0.60
slang_level: 0.10
pace_bpm: 140
pause_default_ms: 320
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

tone_bias_business: 0.40
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.25
tone_bias_personal: 0.75

# VOICE DISTINCTION:
# Educated, philosophical. Overthinking is default mode.
# Values ideas and understanding.

domain_jargon:
  - 思考
  - 分析
  - 理解
  - 神經系統

persona_scenarios:
  primary_dimension: overthinking
  secondary_dimension: philosophical_anxiety
  integration_dimension: somatic_peace

topic_resonance:
  1: overthinking
  2: sleep_repair
  3: boundaries
  4: contemplative_wisdom

template_set: anxious_intellectual_sg
shares_templates_with: []
```

---

## PART 5: ja-JP (Japan) Personas

**Phase**: Phase 2 (Months 4–6)
**Distribution**: JP Google Play, JP Apple Books, Audible JP, Kobo JP, Spotify JP
**Framing Notes**: CRITICAL — NEVER use "mental health" (精神的健康) in titles or positioning. High stigma. USE "nervous system" (神経系), "wellbeing" (ウェルビーイング), "self-care" (セルフケア). Politeness register (丁寧語) required throughout narration. Karoshi (過労死) culture makes burnout brands highest priority.

### Persona 1: `salaryman_burnout_jp`

```yaml
persona_id: salaryman_burnout_jp
display_name: Salaryman Burnout (Japan)
locale: ja-JP
territory: JP
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_jp
template_packs:
  base: core_self_help_v1_jp
  overrides:
    - salaryman_culture_pack_jp
    - karoshi_prevention_pack_jp
language_packs:
  primary: ja-JP_core_v1

voice_tone: 丁寧、認識、神経系統覚知、文化尊重
formality: 0.75
slang_level: 0.05
pace_bpm: 140
pause_default_ms: 330
story_injection_rate: 0.25
breathing_exercise_frequency: 0.28

tone_bias_business: 0.75
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.15
tone_bias_personal: 0.60

# VOICE DISTINCTION:
# 社畜 (salaryman) culture. Overwork is expected. Identity fused with company.
# Karoshi (過労死) risk is real and unspoken. Politeness throughout — formality
# is sign of respect. Use "神経系" not "心理" or "メンタル."

domain_jargon:
  - 神経系
  - 自律神経
  - 過度労働
  - 疲労
  - 社会的責任
  - ウェルビーイング
  - セルフケア

metaphor_style:
  - システム / 過負荷
  - 信号 / ノイズ
  - バランス / 傾き
  - リズム / 乱れ

persona_scenarios:
  primary_dimension: work_survival
  secondary_dimension: physical_exhaustion
  integration_dimension: nervous_system_recovery
  content_templates:
    primary:
      dimension: あなたの仕事と過度労働
      scenario_library:
        - 深夜の会議が日常になった
        - 週末も仕事の電話に応じている
        - 有給休暇を取る「勇気」がない
        - 同期が過労で倒れたニュース
        - 自分のペースと会社の期待のギャップ
    secondary:
      dimension: あなたの身体
      scenario_library:
        - 朝起きられない疲労感
        - 首や肩の慢性的な緊張
        - 消化器官の不調
    integration:
      dimension: あなたと神経系統の関係
      scenario_library:
        - 身体からのサインを無視していた
        - 休息すること自体が罪悪感につながる
        - ウェルビーイングが「贅沢」に思える

rewrite_config:
  style_notes:
    - 敬語・丁寧語を一貫して使用。敬意の表現。
    - 「精神」「メンタル」を避ける。「神経系」「ウェルビーイング」を使う。
    - 社会的責任を認める（放棄させない）が、身体の限界も名前化。
    - 解決策は実践的で、時間効率の良いもの。
    - 会社文化を妖魔化しない。システムの現実を名前化する。
  forbidden_markers:
    - positive thinking
    - mind over matter
    - あなたは強い
    - 我慢
    - 根性
  title_rules:
    vibe: 敬意を示す、実証的、神経系統中心
    min_words: 2
    max_words: 8
    max_chars: 70
    patterns:
      - "当 {症状} は実は {機制}"
      - "{行動} を {代償} なしに"
      - "神経系統の {ニーズ}"
    subtitle:
      enabled: true
      max_chars: 90
      style: ウェルビーイング中心、敬意のある

local_environment:
  morning_routine:
    - 朝の通勤ラッシュの中での疲労感
    - 駅で息切れする自分を見つめる
    - 会社のドアを開ける瞬間の緊張
  workspace:
    - オフィスの蛍光灯と人口音
    - 上司の視線を感じながら休憩する
    - 会議の無限ループ
  evening:
    - 帰りの電車での寝落ち
    - 夜遅い飲み会の社交的期待
    - 家に帰ってからも仕事メール
  relationships:
    - 妻が疲れている顔を見ている
    - 子どもの声が耳に入らない疲労
    - 友人との連絡が途絶えている

book_generation:
  pain_template: >
    あなたは {topic} がどのような感覚かご存知でしょう。
    それはドラマティックではなく、天気のように静かに降り立ちます。
    会議の中で感じ、帰りの電車で深まり、
    「これは続かない」という認識があるにもかかわらず。
  location_cues:
    intro: それは、深夜の会議の後かもしれません。
    body: または、月曜日の朝、出社する力を感じられない瞬間、
    outro: そして身体が「もう限界です」と静かに語りかけ始めたとき。

market_data:
  jp_target_population: 1.8M (corporate salarymen, burnout risk)
  audiobook_consumption: 6.5 titles/year (strong audiobook market)
  primary_platforms: [Spotify, Google Play, Audible JP, Kobo JP]
  discovery_channels: [Podcast, YouTube, Line, Twitter]
  price_sensitivity: moderate (¥1,500–¥2,500 sweet spot)
  distribution_strategy: spotify_primary_audible_secondary

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: sleep_repair
  4: energy_management
  5: somatic_healing

template_set: salaryman_burnout_jp
shares_templates_with: []
```

---

### Persona 2: `anxious_insomniac_jp`

```yaml
persona_id: anxious_insomniac_jp
display_name: Anxious Insomniac (Japan)
locale: ja-JP
territory: JP
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_jp
template_packs:
  base: core_self_help_v1_jp
  overrides:
    - sleep_anxiety_pack_jp
language_packs:
  primary: ja-JP_core_v1

voice_tone: 丁寧、支持的、神経系統中心
formality: 0.75
slang_level: 0.05
pace_bpm: 135
pause_default_ms: 340
story_injection_rate: 0.32
breathing_exercise_frequency: 0.32

tone_bias_business: 0.50
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.15
tone_bias_personal: 0.70

# VOICE DISTINCTION:
# Sleep anxiety from performance pressure. Perfectionism collides with
# biological limit. Uses polite register throughout.

domain_jargon:
  - 睡眠
  - 神経系
  - 不安
  - 自律神経
  - セルフケア

persona_scenarios:
  primary_dimension: sleep_anxiety
  secondary_dimension: nervous_system_dysregulation
  integration_dimension: rest_permission

topic_resonance:
  1: sleep_repair
  2: stabilizer
  3: somatic_healing

template_set: anxious_insomniac_jp
shares_templates_with: []
```

---

### Persona 3: `gen_z_jp`

```yaml
persona_id: gen_z_jp
display_name: Gen Z (Japan)
locale: ja-JP
territory: JP
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_jp
template_packs:
  base: core_self_help_v1_jp
  overrides:
    - hikikomori_prevention_pack_jp
language_packs:
  primary: ja-JP_core_v1

voice_tone: 敬意を示すピア、誠実、非説教的
formality: 0.55
slang_level: 0.20
pace_bpm: 150
pause_default_ms: 280
story_injection_rate: 0.38
breathing_exercise_frequency: 0.35

tone_bias_business: 0.25
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.20
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# 引きこもり (hikikomori) risk, academic pressure, SNS anxiety.
# Social withdrawal and academic hypercompetition. Speaks politely but as peer.

domain_jargon:
  - 引きこもり
  - 社会不安
  - 学業成績
  - 身体感覚
  - つながり

persona_scenarios:
  primary_dimension: social_withdrawal_risk
  secondary_dimension: academic_pressure
  integration_dimension: nervous_system_safety

topic_resonance:
  1: gen_z_grounding
  2: social_anxiety
  3: boundaries
  4: sleep_repair

template_set: gen_z_jp
shares_templates_with: []
```

---

### Persona 4: `overwhelmed_caregiver_jp`

```yaml
persona_id: overwhelmed_caregiver_jp
display_name: Overwhelmed Caregiver (Japan)
locale: ja-JP
territory: JP
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_jp
template_packs:
  base: core_self_help_v1_jp
  overrides:
    - eldercare_pack_jp
language_packs:
  primary: ja-JP_core_v1

voice_tone: 温かい、見守る、敬意を示す
formality: 0.68
slang_level: 0.05
pace_bpm: 130
pause_default_ms: 350
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

tone_bias_business: 0.20
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Caring for aging parent. Women disproportionately impacted.
# Filial duty + work + caregiving = impossible equation.

domain_jargon:
  - 介護
  - 親の世話
  - 身体の疲労
  - 孝
  - 責任

persona_scenarios:
  primary_dimension: caregiving_burden
  secondary_dimension: physical_exhaustion
  integration_dimension: permission_to_rest

topic_resonance:
  1: burnout_recovery
  2: boundaries
  3: somatic_healing
  4: inner_security

template_set: overwhelmed_caregiver_jp
shares_templates_with: []
```

---

## PART 6: ko-KR (South Korea) Personas

**Phase**: Phase 3 (Months 5–7)
**Distribution**: KR Google Play, KR Apple Books, Naver Audiobook, Kakao Page, Spotify KR
**Framing Notes**: 번아웃 (burnout) is high-awareness/high-search. 빨리빨리 (ppalli-ppalli) culture = fast-paced. Academic exam pressure (수능). Achievement culture (학벌). Micro sessions (15–30 min) may outperform long deep dives.

### Persona 1: `burned_out_professional_kr`

```yaml
persona_id: burned_out_professional_kr
display_name: Burned Out Professional (South Korea)
locale: ko-KR
territory: KR
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_kr
template_packs:
  base: core_self_help_v1_kr
  overrides:
    - ppalli_ppalli_culture_pack_kr
    - achievement_pressure_pack_kr
language_packs:
  primary: ko-KR_core_v1

voice_tone: 인정적, 실용적, 신경계 인식, 빠른 페이스
formality: 0.68
slang_level: 0.15
pace_bpm: 160  # faster for ppalli-ppalli culture
pause_default_ms: 260
story_injection_rate: 0.25
breathing_exercise_frequency: 0.22

tone_bias_business: 0.80
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.10
tone_bias_personal: 0.60

# VOICE DISTINCTION:
# 빨리빨리 culture. Everything moves fast. Burnout is visible here.
# Achievement culture (학벌) means career defines identity.
# 번아웃 awareness is high — this persona resonates with searches.

domain_jargon:
  - 번아웃
  - 신경계
  - 과로
  - 빨리빨리
  - 학벌
  - 경쟁
  - 자기계발

metaphor_style:
  - 시스템 / 당기기
  - 신호 / 소음
  - 기술 부채
  - 속도 / 정지

persona_scenarios:
  primary_dimension: work_survival
  secondary_dimension: competitive_culture
  integration_dimension: nervous_system_recovery
  content_templates:
    primary:
      dimension: 당신의 일과 생존
      scenario_library:
        - 무한한 회사 기대
        - 라이벌의 승리 소식
        - 직급과 급여 정체기
        - 더 빨리, 더 많이의 압박
        - 팀 멤버의 이직
    secondary:
      dimension: 당신의 사회적 지위
      scenario_library:
        - 명문대 졸업과 일자리 경쟁
        - 대기업 입사의 압력
        - 나이별 성공의 기준
    integration:
      dimension: 당신과 신경계의 관계
      scenario_library:
        - 쉼 없는 각성 상태
        - 주말도 온전한 휴식이 없음
        - 몸이 보내는 신호 무시

rewrite_config:
  style_notes:
    - 빠르고 직접적. 설명은 간결하게.
    - 번아웃을 일반적인 약점이 아니라 신경계 문제로.
    - 성취 문화를 비난하지 않되, 신체의 한계를 이름 짓기.
    - 마이크로 세션 권장 (15–30분이 이상적).
  forbidden_markers:
    - 명상
    - 영성
    - 치유
    - 감정 표현
  title_rules:
    vibe: 빠르고 직접적, 신경계 중심
    min_words: 2
    max_words: 7
    max_chars: 65
    patterns:
      - "당신의 {증상}은 사실 {메커니즘}"
      - "{행동}도 {대가} 없이"
      - "{시간}내 {결과}"

local_environment:
  morning_routine:
    - 이른 출근 시간
    - 회의 전의 준비
    - 카페인 의존성
  workspace:
    - 끝나지 않는 회의
    - 부장과의 관계 긴장
    - 포기할 수 없는 재택근무
  evening:
    - 야근의 일상화
    - 야식 문화
    - 알콜 의존성
  relationships:
    - 가족과의 단절
    - 친구들과의 만남 취소

book_generation:
  pain_template: >
    당신은 {topic}이 어떤 느낌인지 알 것입니다. 드라마틱하지 않게,
    날씨처럼 조용하게 밀려옵니다. 회의 중에, 이동 중에, 그리고
    "이것이 계속될 수 없다"는 것을 알면서도.
  location_cues:
    intro: 아마도 빠른 주간 업무 중에,
    body: 또는 금요일 밤 퇴근 후 여전히 일을 생각할 때,
    outro: 그리고 신체가 "더 이상 안 됩니다"라고 말하기 시작했을 때.

market_data:
  kr_target_population: 1.5M (corp professionals, high burnout awareness)
  audiobook_consumption: 7-9 titles/year (strong podcast culture)
  primary_platforms: [Spotify, Google Play, Naver Audiobook, Kakao Page]
  discovery_channels: [YouTube, Naver, Kakao Talk, Instagram]
  price_sensitivity: moderate (₩11,000–₩17,000 sweet spot)
  micro_session_preference: high (15–30 min optimal over 60+ min)
  distribution_strategy: spotify_primary_naver_kakao_secondary

topic_resonance:
  1: stabilizer  # "번아웃" search volume is very high
  2: burnout_recovery
  3: energy_management
  4: sleep_repair
  5: boundaries

template_set: burned_out_professional_kr
shares_templates_with: []
```

---

### Persona 2: `anxious_student_kr`

```yaml
persona_id: anxious_student_kr
display_name: Anxious Student (South Korea)
locale: ko-KR
territory: KR
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_kr
template_packs:
  base: core_self_help_v1_kr
  overrides:
    - suneung_pressure_pack_kr
language_packs:
  primary: ko-KR_core_v1

voice_tone: 동료, 판단 없음, 신체 중심
formality: 0.50
slang_level: 0.25
pace_bpm: 155
pause_default_ms: 270
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.20
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# 수능 (suneung) exam pressure. Academic hypercompetitiveness.
# Sleep deprivation. Family expectations on a level many don't understand.

domain_jargon:
  - 수능
  - 학벌
  - 입시 스트레스
  - 수면 부족
  - 신경계

persona_scenarios:
  primary_dimension: academic_pressure
  secondary_dimension: exam_anxiety
  integration_dimension: nervous_system_safety

topic_resonance:
  1: sleep_repair
  2: anxiety_first_aid
  3: overthinking
  4: boundaries

template_set: anxious_student_kr
shares_templates_with: []
```

---

### Persona 3: `gen_z_kr`

```yaml
persona_id: gen_z_kr
display_name: Gen Z (South Korea)
locale: ko-KR
territory: KR
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_kr
template_packs:
  base: core_self_help_v1_kr
  overrides:
    - sns_comparison_pack_kr
language_packs:
  primary: ko-KR_core_v1

voice_tone: 동료, 솔직함, SNS 문화 인식
formality: 0.45
slang_level: 0.30
pace_bpm: 155
pause_default_ms: 270
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# SNS comparison culture (Instagram, TikTok). Social anxiety from
# constant visibility. Burnout awareness is high in this generation.
# Seeks micro-content (short, fast, practical).

domain_jargon:
  - SNS
  - 비교 문화
  - 사회불안
  - 신경계
  - 번아웃

persona_scenarios:
  primary_dimension: social_comparison
  secondary_dimension: identity_anxiety
  integration_dimension: nervous_system_safety

topic_resonance:
  1: gen_z_grounding
  2: social_anxiety
  3: boundaries
  4: sleep_repair

template_set: gen_z_kr
shares_templates_with: []
```

---

### Persona 4: `lonely_urban_professional_kr`

```yaml
persona_id: lonely_urban_professional_kr
display_name: Lonely Urban Professional (South Korea)
locale: ko-KR
territory: KR
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_kr
template_packs:
  base: core_self_help_v1_kr
  overrides:
    - urban_isolation_pack_kr
language_packs:
  primary: ko-KR_core_v1

voice_tone: 온정적, 연결, 신경계 인식
formality: 0.55
slang_level: 0.15
pace_bpm: 140
pause_default_ms: 310
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

tone_bias_business: 0.40
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.20
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Urban isolation. High workplace stress but no genuine connection.
# Social anxiety in competitive environment. Seeking authentic connection.

domain_jargon:
  - 고독감
  - 도시 생활
  - 관계 단절
  - 사회불안
  - 신경계

persona_scenarios:
  primary_dimension: loneliness
  secondary_dimension: social_anxiety
  integration_dimension: nervous_system_connection

topic_resonance:
  1: inner_security
  2: boundaries
  3: social_anxiety
  4: somatic_healing

template_set: lonely_urban_professional_kr
shares_templates_with: []
```

---

## PART 7: es-US (US Hispanic) Personas

**Phase**: Phase 4 (Months 7–12)
**Distribution**: US Google Play, US Findaway, US Apple Books (same US territory as en-US)
**Framing Notes**: Largest non-English US audiobook opportunity. Neutral Latin American Spanish preferred (not Castilian). First-generation professionals, bilingual household stress, cultural expectations + career tension, family caregiving.

### Persona 1: `millennial_latina_professional_es_us`

```yaml
persona_id: millennial_latina_professional_es_us
display_name: Millennial Latina Professional (US Hispanic)
locale: es-US
territory: US
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_es_us
template_packs:
  base: core_self_help_v1_es_us
  overrides:
    - first_generation_pack_es_us
    - cultural_expectations_pack_es_us
language_packs:
  primary: es-US_core_v1
  fallbacks: []

voice_tone: calidez, directa, culturalmente consciente, empoderada
formality: 0.60
slang_level: 0.20
pace_bpm: 145
pause_default_ms: 310
story_injection_rate: 0.38
breathing_exercise_frequency: 0.32

tone_bias_business: 0.70
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.20
tone_bias_personal: 0.75

# VOICE DISTINCTION:
# First-generation professional (parents arrived for opportunity).
# Navigating cultural expectations + career ambitions.
# Code-switching between home and work cultures.
# Shoulder a lot — family expectations, professional pressure, financial responsibility.

domain_jargon:
  - oportunidad
  - responsabilidad familiar
  - bilingüismo
  - expectativas culturales
  - ascenso profesional
  - código-cambio
  - sistema nervioso

metaphor_style:
  - puente / dos mundos
  - raíz / rama
  - carga / contenedor
  - corriente / ancla

persona_scenarios:
  primary_dimension: cultural_identity
  secondary_dimension: professional_ambition
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: tu identidad cultural y profesional
      scenario_library:
        - la reunión donde cambias tu acento sin darte cuenta
        - la llamada de mamá durante tu horario de trabajo
        - la presión de "hacer que valga la pena" la oportunidad familiar
        - el sentimiento de no ser suficientemente algo
        - la culpa por querer más que lo que tuvieron tus padres
    secondary:
      dimension: tu carrera y ambición
      scenario_library:
        - el ascenso que viniste a buscar pero que te cuesta
        - los colegas que no comprenden tu contexto
        - el dinero que sigues enviando a casa
    integration:
      dimension: tu relación contigo misma
      scenario_library:
        - el descanso se siente como abandono
        - el éxito no trae paz
        - la fatiga de vivir en dos idiomas

rewrite_config:
  style_notes:
    - Cálida pero no condescendiente. Directa pero no fría.
    - Respeta la inteligencia y la complejidad cultural.
    - Nombra la presión estructural sin hacerla el tema del libro.
    - Valida ambas culturas sin romanticizar ninguna.
    - Reconoce la fortaleza sin agotamiento.
  forbidden_markers:
    - empoderamiento (usado en exceso)
    - resistencia (puede sentirse prescriptiva)
    - sanación
    - merecimiento
  title_rules:
    vibe: calidez, directa, respeta inteligencia
    min_words: 2
    max_words: 8
    max_chars: 70
    patterns:
      - "Cuando {síntoma} es realmente {mecanismo}"
      - "{Acción} sin {costo}"
      - "Después de {evento}"
    subtitle:
      enabled: true
      max_chars: 90
      style: mecanismo primero, respeta inteligencia

local_environment:
  morning_routine:
    - la conversación en español de la mamá antes de salir
    - el cambio de acento al entrar al trabajo
    - el café como ritual y como supervivencia
  workspace:
    - la oficina donde eres la única cara que se parece a la tuya
    - la reunión donde asumes que hablas por todos los latinos
    - el código-cambio constante
  evening:
    - la llamada a casa que espera que esté disponible
    - la comida que preparas porque nadie más lo hace igual
    - el cuidado invisible que das a otros
  relationships:
    - la pareja que no entiende tu obligación familiar
    - los amigos latinos que se quedaron atrás
    - los padres que no entienden por qué estás "cansada"

book_generation:
  pain_template: >
    Sabes lo que es cuando {topic} llega — no dramáticamente,
    sino como el clima. Cómo se sienta en tu pecho durante las reuniones,
    te sigue a la ducha, hace que el descanso se sienta como otro fracaso.
    Y tiene un idioma. Y tiene un apellido.
  location_cues:
    intro: Quizás sucedió después de una llamada familiar,
    body: o en la oficina cuando finalmente ascendieron a alguien más,
    outro: y algo en ti supo que esto no podía seguir así.

market_data:
  us_hispanic_population: 62.4M
  audiobook_listeners: 8.2M (13% of population)
  audiobook_consumption: 5.5 titles/year
  primary_platforms: [Spotify, Google Play, Apple Books]
  discovery_channels: [Instagram, Podcast español, Word of mouth, Facebook]
  price_sensitivity: moderate ($7.99–$14.99 sweet spot)
  distribution_strategy: spotify_primary_google_secondary
  spanish_dialect_preference: neutral latin american

topic_resonance:
  1: boundaries
  2: overthinking
  3: burnout_recovery
  4: self_worth
  5: family_expectations

template_set: millennial_latina_professional_es_us
shares_templates_with: []
```

---

### Persona 2: `anxious_parent_es_us`

```yaml
persona_id: anxious_parent_es_us
display_name: Anxious Parent (US Hispanic)
locale: es-US
territory: US
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_es_us
template_packs:
  base: core_self_help_v1_es_us
  overrides:
    - bilingual_parenting_pack_es_us
    - work_family_balance_pack_es_us
language_packs:
  primary: es-US_core_v1

voice_tone: comprensión, permiso, sin culpa, cálida
formality: 0.50
slang_level: 0.25
pace_bpm: 135
pause_default_ms: 340
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.30
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Working parent managing bilingual household, work stress, family expectations.
# The "mental load" is real + cultural obligations. Never adds to guilt pile.

domain_jargon:
  - carga mental
  - crianza bilingüe
  - estrés familiar
  - responsabilidades invisibles
  - sistema nervioso

persona_scenarios:
  primary_dimension: parenting_demands
  secondary_dimension: bilingual_household
  integration_dimension: self_compassion
  content_templates:
    primary:
      dimension: las demandas de tu crianza
      scenario_library:
        - la mañana donde todo salió mal antes de las 7:30
        - el colapso en la tienda mientras otros miran
        - la hora de acostarse que tomó 90 minutos
        - el correo escolar que llegó durante una reunión
        - la culpa de elegir trabajo sobre la función escolar
    secondary:
      dimension: tu hogar bilingüe
      scenario_library:
        - hablar dos idiomas con dos culturas diferentes
        - la expectativa de enseñar español mientras trabajas
        - los abuelos que no entienden por qué la niña no habla español perfecto
    integration:
      dimension: tu relación contigo misma
      scenario_library:
        - la persona que eras antes de los hijos y la pena de eso
        - el cuerpo que no se siente tuyo
        - los 10 minutos en el auto que se sintieron como salvación

rewrite_config:
  style_notes:
    - Capítulos cortos. Serán interrumpidas.
    - Nunca añadas culpa. Nómbra la, no la amplíes.
    - Los ejercicios deben funcionar en 2–5 minutos.
    - El cuerpo está exhausto. Lidera con somático, no cognitivo.
    - El humor es bienvenido — suave, autocrítico.
  forbidden_markers:
    - mamá guerrera
    - santidad de la maternidad
    - disfruta cada momento
    - bendecida

title_rules:
  vibe: calidez, permiso, comprensión
  patterns:
    - "Cuando {síntoma} es realmente {agotamiento}"
    - "{Pausa} sin {culpa}"

local_environment:
  morning_routine:
    - la prisa de dos idiomas al mismo tiempo
    - la ropa que cambia planes
    - la comida que preparo anoche
  workspace:
    - la reunión interrumpida por una llamada escolar
    - el mensaje de daycare sobre el incidente
    - la carga invisible de ser la que se acuerda
  evening:
    - la cena que preparo porque nadie más lo hace igual
    - el baño que requiere dos idiomas
    - el colapso después de que duermen

market_data:
  us_hispanic_parents: 14.2M
  audiobook_consumption: 6.2 titles/year (hands-free format = natural fit)
  primary_platforms: [Spotify, Apple Books]
  price_sensitivity: high ($4.99–$9.99 sweet spot)
  distribution_strategy: spotify_primary

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: overthinking
  4: self_worth
  5: family_expectations

template_set: anxious_parent_es_us
shares_templates_with: []
```

---

### Persona 3: `gen_z_hispanic_es_us`

```yaml
persona_id: gen_z_hispanic_es_us
display_name: Gen Z Hispanic (US Hispanic)
locale: es-US
territory: US
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_es_us
template_packs:
  base: core_self_help_v1_es_us
  overrides:
    - identity_navigation_pack_es_us
language_packs:
  primary: es-US_core_v1

voice_tone: pares, honesta, culturalmente consciente
formality: 0.45
slang_level: 0.35
pace_bpm: 155
pause_default_ms: 260
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Cultural identity navigation. Family expectations clash with personal desires.
# Bilingual, bicultural. Social media comparison culture.

domain_jargon:
  - identidad cultural
  - expectativas familiares
  - bilingüismo
  - comparación social
  - autenticidad

persona_scenarios:
  primary_dimension: identity_navigation
  secondary_dimension: family_expectations
  integration_dimension: authentic_self

topic_resonance:
  1: gen_z_grounding
  2: boundaries
  3: social_anxiety
  4: overthinking

template_set: gen_z_hispanic_es_us
shares_templates_with: []
```

---

### Persona 4: `caregiver_immigrant_es_us`

```yaml
persona_id: caregiver_immigrant_es_us
display_name: Caregiver (Immigrant Context) (US Hispanic)
locale: es-US
territory: US
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_es_us
template_packs:
  base: core_self_help_v1_es_us
  overrides:
    - immigrant_caregiving_pack_es_us
language_packs:
  primary: es-US_core_v1

voice_tone: calor, reconocimiento, respeto, sensibilidad a la trayectoria
formality: 0.55
slang_level: 0.10
pace_bpm: 130
pause_default_ms: 350
story_injection_rate: 0.35
breathing_exercise_frequency: 0.28

tone_bias_business: 0.20
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.35
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Caring for family. Immigration context adds complexity —
# economic responsibility, legal uncertainty, long-distance caregiving.

domain_jargon:
  - cuidado familiar
  - responsabilidad económica
  - lejanía
  - obligación
  - sacrificio sin fin

persona_scenarios:
  primary_dimension: caregiving_burden
  secondary_dimension: immigrant_responsibilities
  integration_dimension: permission_to_rest

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: somatic_healing
  4: inner_security

template_set: caregiver_immigrant_es_us
shares_templates_with: []
```

---

## PART 8: es-ES (Spain) Personas

**Phase**: Phase 4 (Months 7–12)
**Distribution**: ES Google Play, ES Findaway, ES Apple Books, ES Spotify
**Framing Notes**: Castilian Spanish (vosotros, c/z distinction). High youth unemployment context, burnout despite achievement, work-life balance aspirations. Extended family expectations.

### Persona 1: `burned_out_millennial_es`

```yaml
persona_id: burned_out_millennial_es
display_name: Burned Out Millennial (Spain)
locale: es-ES
territory: ES
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_es
template_packs:
  base: core_self_help_v1_es
  overrides:
    - spanish_unemployment_context_pack
language_packs:
  primary: es-ES_core_v1

voice_tone: reconocimiento, pragmática, sin ilusiones, empoderada
formality: 0.65
slang_level: 0.15
pace_bpm: 145
pause_default_ms: 310
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.70
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.15
tone_bias_personal: 0.65

# VOICE DISTINCTION:
# High youth unemployment (crisis-era cohort). Finally found work but
# precarious. Burnout despite achievement. "I did everything right
# and it still wasn't enough." Uses Castilian Spanish dialect.

domain_jargon:
  - precariedad laboral
  - desempleo juvenil
  - agotamiento
  - sistema nervioso
  - inequidad

persona_scenarios:
  primary_dimension: work_precarity
  secondary_dimension: economic_anxiety
  integration_dimension: nervous_system_recovery

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: financial_anxiety
  4: boundaries

template_set: burned_out_millennial_es
shares_templates_with: []
```

---

### Persona 2: `gen_z_es`

```yaml
persona_id: gen_z_es
display_name: Gen Z (Spain)
locale: es-ES
territory: ES
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_es
template_packs:
  base: core_self_help_v1_es
  overrides:
    - climate_anxiety_pack_es
    - economic_precarity_pack_es
language_packs:
  primary: es-ES_core_v1

voice_tone: pares, honesta, consciente del clima
formality: 0.45
slang_level: 0.30
pace_bpm: 155
pause_default_ms: 270
story_injection_rate: 0.38
breathing_exercise_frequency: 0.35

tone_bias_business: 0.20
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Climate anxiety, economic precarity, social anxiety.
# Inheriting a broken system. Questioning whether to participate.

domain_jargon:
  - ansiedad climática
  - precariedad económica
  - ansiedad social
  - futuro incierto

persona_scenarios:
  primary_dimension: climate_and_economic_anxiety
  secondary_dimension: social_anxiety
  integration_dimension: nervous_system_safety

topic_resonance:
  1: gen_z_grounding
  2: overthinking
  3: social_anxiety
  4: boundaries

template_set: gen_z_es
shares_templates_with: []
```

---

### Persona 3: `overwhelmed_parent_es`

```yaml
persona_id: overwhelmed_parent_es
display_name: Overwhelmed Parent (Spain)
locale: es-ES
territory: ES
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_es
template_packs:
  base: core_self_help_v1_es
  overrides:
    - work_life_balance_pack_es
language_packs:
  primary: es-ES_core_v1

voice_tone: calidez, comprensión, permiso, realista
formality: 0.55
slang_level: 0.15
pace_bpm: 135
pause_default_ms: 340
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

tone_bias_business: 0.35
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Work-life balance pressure. Extended family expectations.
# "Siesta culture" ideal vs. modern work reality collision.

domain_jargon:
  - equilibrio trabajo-vida
  - responsabilidades familiares
  - expectativas extendidas
  - agotamiento

persona_scenarios:
  primary_dimension: work_family_balance
  secondary_dimension: family_expectations
  integration_dimension: self_compassion

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: overthinking
  4: somatic_healing

template_set: overwhelmed_parent_es
shares_templates_with: []
```

---

## PART 9: fr-FR (France) Personas

**Phase**: Phase 4 (Months 7–12)
**Distribution**: FR Google Play, FR Findaway, FR Apple Books, FR Spotify
**Framing Notes**: Strong audiobook market. Mental health discourse accepts more philosophical framing. Stoic, existentialist angles work alongside somatic. 35-hour week culture ironically doesn't prevent burnout — creative and finance sectors run hotter.

### Persona 1: `overworked_professional_fr`

```yaml
persona_id: overworked_professional_fr
display_name: Overworked Professional (France)
locale: fr-FR
territory: FR
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_fr
template_packs:
  base: core_self_help_v1_fr
  overrides:
    - french_work_culture_pack
language_packs:
  primary: fr-FR_core_v1

voice_tone: sophistiqué, réfléchi, reconnaissant, sans culpabilité
formality: 0.70
slang_level: 0.10
pace_bpm: 145
pause_default_ms: 320
story_injection_rate: 0.32
breathing_exercise_frequency: 0.28

tone_bias_business: 0.70
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.25
tone_bias_personal: 0.65

# VOICE DISTINCTION:
# Ironically, despite 35-hour week legislation, burnout thrives
# (especially creative/finance). Works because love their work.
# Uses philosophical framing alongside somatic. Sophisticated tone.

domain_jargon:
  - épuisement
  - système nerveux
  - déséquilibre
  - passion vs. destruction
  - conscience

metaphor_style:
  - équilibre / déséquilibre
  - système / surcharge
  - philosophie / corps
  - absurde / sens

persona_scenarios:
  primary_dimension: work_passion_vs_exhaustion
  secondary_dimension: philosophical_exhaustion
  integration_dimension: nervous_system_recovery
  content_templates:
    primary:
      dimension: ta carrière et ta passion
      scenario_library:
        - tu aimes ton travail mais il te tue
        - la limite entre passion et destruction
        - les réunions infinies malgré la loi des 35 heures
        - l'ironie d'être "à jour" légalement mais épuisé
    secondary:
      dimension: ta relation avec le travail
      scenario_library:
        - l'identité professionnelle qui surdéfinit le reste
        - le repos qui se sent comme de la culpabilité

market_data:
  fr_target_population: 850,000 (professionals, creative sector)
  audiobook_consumption: 6.5 titles/year (strong market)
  primary_platforms: [Spotify, Google Play, Findaway]
  price_sensitivity: moderate (€9.99–€16.99)
  distribution_strategy: spotify_primary_findaway_secondary

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: sleep_repair
  4: contemplative_wisdom

template_set: overworked_professional_fr
shares_templates_with: []
```

---

### Persona 2: `anxious_intellectual_fr`

```yaml
persona_id: anxious_intellectual_fr
display_name: Anxious Intellectual (France)
locale: fr-FR
territory: FR
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_fr
template_packs:
  base: core_self_help_v1_fr
  overrides:
    - existential_anxiety_pack_fr
language_packs:
  primary: fr-FR_core_v1

voice_tone: philosophique, autoréflexive, existentielle, chaleureuse
formality: 0.65
slang_level: 0.08
pace_bpm: 140
pause_default_ms: 330
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

tone_bias_business: 0.30
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.35
tone_bias_personal: 0.75

# VOICE DISTINCTION:
# Existential anxiety. Overthinking is default mode. Philosophical
# framing resonates. Stoic, existentialist references work here.

domain_jargon:
  - anxiété existentielle
  - introspection
  - sens de la vie
  - absurde
  - conscience

persona_scenarios:
  primary_dimension: existential_anxiety
  secondary_dimension: overthinking
  integration_dimension: meaning_making

topic_resonance:
  1: overthinking
  2: contemplative_wisdom
  3: existential_peace
  4: sleep_repair

template_set: anxious_intellectual_fr
shares_templates_with: []
```

---

### Persona 3: `depleted_caregiver_fr`

```yaml
persona_id: depleted_caregiver_fr
display_name: Depleted Caregiver (France)
locale: fr-FR
territory: FR
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_fr
template_packs:
  base: core_self_help_v1_fr
  overrides:
    - eldercare_pack_fr
language_packs:
  primary: fr-FR_core_v1

voice_tone: chaleureux, témoin, respect de la responsabilité
formality: 0.60
slang_level: 0.08
pace_bpm: 130
pause_default_ms: 350
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

tone_bias_business: 0.20
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.30
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# Caring for aging parent. Guilt around system reliance.
# French culture emphasizes responsibility — but also values personal time.

domain_jargon:
  - soin des aînés
  - culpabilité
  - système de santé
  - responsabilité
  - épuisement

persona_scenarios:
  primary_dimension: caregiving_burden
  secondary_dimension: guilt_and_system
  integration_dimension: permission_to_rest

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: inner_security
  4: somatic_healing

template_set: depleted_caregiver_fr
shares_templates_with: []
```

---

## PART 10: de-DE (Germany/Austria/Switzerland) Personas

**Phase**: Phase 4 (Months 7–12)
**Distribution**: DE Google Play, DE Findaway, DE Audible, DE Apple Books, DE Spotify
**Framing Notes**: Largest European audiobook market. Science/evidence framing strongly preferred. **NO spiritual content**. "Stressbewältigung" (stress management) and "Burnout" are high-search terms. DACH market (Germany, Austria, Switzerland).

### Persona 1: `high_functioning_burnout_de`

```yaml
persona_id: high_functioning_burnout_de
display_name: High-Functioning Burnout (Germany)
locale: de-DE
territory: DE
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_de
template_packs:
  base: core_self_help_v1_de
  overrides:
    - stressbewaltigung_pack_de
language_packs:
  primary: de-DE_core_v1

voice_tone: sachlich, evidenzbasiert, keine Spiritualität, pragmatisch
formality: 0.75
slang_level: 0.05
pace_bpm: 145
pause_default_ms: 310
story_injection_rate: 0.25
breathing_exercise_frequency: 0.25

tone_bias_business: 0.75
tone_bias_scientific: 0.75
tone_bias_spiritual: 0.00
tone_bias_personal: 0.50

# VOICE DISTINCTION:
# High-performance DACH culture. Everything runs efficiently — except the body.
# Burnout arrives as data problem, not feeling. Science framing is authority.
# "Stressbewältigung" is high-search. Meditation doesn't work if it feels unscientific.

domain_jargon:
  - Stressbewältigung
  - Burnout
  - Nervensystem
  - Physiologie
  - Datengetrieben
  - Effizienz
  - Regulierung

metaphor_style:
  - System / Überlast
  - Daten / Signale
  - Effizienz / Grenzwert
  - Wartung / Ausfall

persona_scenarios:
  primary_dimension: work_overload
  secondary_dimension: body_signals_ignored
  integration_dimension: physiological_recovery
  content_templates:
    primary:
      dimension: deine Arbeit und Stressbewältigung
      scenario_library:
        - die Effizienz die zur Selbstzerstörung führt
        - die Leistung die Kosten hat
        - die Fakten die du nicht sehen willst
        - die Grenzen der Optimierung
    secondary:
      dimension: dein Körper spricht
      scenario_library:
        - die Signale die du ignorierst
        - die Daten zeigen Probleme

market_data:
  de_target_population: 1.2M (corporate professionals, high burnout)
  audiobook_consumption: 6.5 titles/year (strong market)
  primary_platforms: [Spotify, Google Play, Audible DE, Findaway]
  discovery_channels: [Podcast, YouTube, LinkedIn]
  price_sensitivity: low (€12.99–€19.99)
  distribution_strategy: audible_google_equal
  scientific_framing_required: true

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: sleep_repair
  4: energy_management
  5: somatic_healing

template_set: high_functioning_burnout_de
shares_templates_with: []
```

---

### Persona 2: `anxious_achiever_de`

```yaml
persona_id: anxious_achiever_de
display_name: Anxious Achiever (Germany)
locale: de-DE
territory: DE
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_de
template_packs:
  base: core_self_help_v1_de
  overrides:
    - scientific_framing_pack_de
language_packs:
  primary: de-DE_core_v1

voice_tone: präzise, wissenschaftlich, unterstützend, keine Spiritualität
formality: 0.72
slang_level: 0.05
pace_bpm: 140
pause_default_ms: 320
story_injection_rate: 0.28
breathing_exercise_frequency: 0.28

tone_bias_business: 0.60
tone_bias_scientific: 0.85
tone_bias_spiritual: 0.00
tone_bias_personal: 0.55

# VOICE DISTINCTION:
# Achiever type. Anxiety from perfectionism. Only believes in evidence-based
# approaches. Spiritual framing is irrelevant or offensive.

domain_jargon:
  - Nervensystem
  - Leistung
  - Perfektion
  - Physiologie
  - Regulierung

persona_scenarios:
  primary_dimension: perfectionism_anxiety
  secondary_dimension: performance_pressure
  integration_dimension: nervous_system_regulation

topic_resonance:
  1: overthinking
  2: stabilizer
  3: imposter_syndrome
  4: sleep_repair

template_set: anxious_achiever_de
shares_templates_with: []
```

---

### Persona 3: `caregiver_de`

```yaml
persona_id: caregiver_de
display_name: Caregiver (Germany)
locale: de-DE
territory: DE
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14_de
template_packs:
  base: core_self_help_v1_de
  overrides:
    - eldercare_pack_de
language_packs:
  primary: de-DE_core_v1

voice_tone: sachlich, unterstützend, Würde, systemorientiert
formality: 0.68
slang_level: 0.05
pace_bpm: 130
pause_default_ms: 340
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.25
tone_bias_scientific: 0.60
tone_bias_spiritual: 0.00
tone_bias_personal: 0.75

# VOICE DISTINCTION:
# Eldercare in system-oriented culture. German healthcare system exists,
# but guilt about "relying on it" persists. Pragmatic framing of duty + limits.

domain_jargon:
  - Pflegevetwortung
  - Systemunterstützung
  - Grenzen
  - Würde

persona_scenarios:
  primary_dimension: caregiving_burden
  secondary_dimension: system_responsibility
  integration_dimension: boundary_setting

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: somatic_healing
  4: inner_security

template_set: caregiver_de
shares_templates_with: []
```

---

## PART 11: hu-HU (Hungary) Personas

**Phase**: Phase 4 (Months 7–12)
**Distribution**: HU Google Play, HU Findaway, HU Apple Books, HU Spotify
**Framing Notes**: **ElevenLabs ONLY** (no Google Neural2 hu-HU). Mental health stigma higher than Western Europe — wellness/self-development framing preferred over clinical language. Smaller market, low competition.

### Persona 1: `burned_out_professional_hu`

```yaml
persona_id: burned_out_professional_hu
display_name: Burned Out Professional (Hungary)
locale: hu-HU
territory: HU
generation_dialect: millennial
active: true
revenue_tier: 1

beat_map: phoenix_14_hu
template_packs:
  base: core_self_help_v1_hu
  overrides:
    - wellness_framing_pack_hu
language_packs:
  primary: hu-HU_core_v1

voice_tone: támogató, gyakorlatias, wellness-orientált, sem klinikai
formality: 0.65
slang_level: 0.12
pace_bpm: 145
pause_default_ms: 310
story_injection_rate: 0.30
breathing_exercise_frequency: 0.28

tone_bias_business: 0.70
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.20
tone_bias_personal: 0.65

# VOICE DISTINCTION:
# Burnout in smaller market. Stigma means clinical language doesn't work.
# Frame as "wellness" and "self-development" rather than therapy.
# ElevenLabs TTS only — no Google Neural2 for Hungarian.

domain_jargon:
  - kiégés
  - önfejlesztés
  - jóllét
  - hálózat (nervous system metaphor)
  - kezelhetőség

metaphor_style:
  - rendszer / túltöltődés
  - energia / kimerülés
  - fejlődés / stagnálás
  - egyensúly / dőlés

persona_scenarios:
  primary_dimension: work_exhaustion
  secondary_dimension: self_development
  integration_dimension: wellness_recovery
  content_templates:
    primary:
      dimension: munkád és kiégésed
      scenario_library:
        - a végtelence munka elvárások
        - a kolléga amely otthagyta a céget
        - a fizetésmegemelés amely nem hozta a békét
    secondary:
      dimension: a te önfejlesztésed
      scenario_library:
        - a kurzus amely nem segített
        - az új készség amely új stresszt hozott

market_data:
  hu_target_population: 480,000 (professionals, growing market)
  audiobook_consumption: 4–6 titles/year (emerging)
  primary_platforms: [Spotify, Google Play, Findaway]
  tts_provider_required: elevenlabs  # ElevenLabs only
  discovery_channels: [Podcast, YouTube, Facebook]
  price_sensitivity: moderate (₹3,490–₹5,490 HUF equivalent sweet spot)
  distribution_strategy: spotify_primary_findaway_secondary

topic_resonance:
  1: stabilizer
  2: burnout_recovery
  3: self_development
  4: sleep_repair
  5: wellness

template_set: burned_out_professional_hu
shares_templates_with: []
```

---

### Persona 2: `anxious_young_adult_hu`

```yaml
persona_id: anxious_young_adult_hu
display_name: Anxious Young Adult (Hungary)
locale: hu-HU
territory: HU
generation_dialect: gen_z
active: true
revenue_tier: 2

beat_map: phoenix_14_hu
template_packs:
  base: core_self_help_v1_hu
  overrides:
    - self_development_frame_hu
language_packs:
  primary: hu-HU_core_v1

voice_tone: támogató, nonmedicalizált, önfejlesztés-orientált
formality: 0.50
slang_level: 0.18
pace_bpm: 150
pause_default_ms: 290
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

tone_bias_business: 0.25
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.25
tone_bias_personal: 0.80

# VOICE DISTINCTION:
# High mental health stigma — avoid clinical framing.
# "Self-development" and "personal growth" framing resonates.
# ElevenLabs TTS only.

domain_jargon:
  - személyes fejlődés
  - önismeret
  - jóllét
  - potenciál
  - kezelhetőség

persona_scenarios:
  primary_dimension: identity_development
  secondary_dimension: anxiety_without_words
  integration_dimension: self_understanding

topic_resonance:
  1: gen_z_grounding
  2: boundaries
  3: sleep_repair
  4: self_development

template_set: anxious_young_adult_hu
shares_templates_with: []
```

---

### Persona 3: `stressed_parent_hu`

```yaml
persona_id: stressed_parent_hu
display_name: Stressed Parent (Hungary)
locale: hu-HU
territory: HU
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14_hu
template_packs:
  base: core_self_help_v1_hu
  overrides:
    - family_responsibility_pack_hu
language_packs:
  primary: hu-HU_core_v1

voice_tone: megértő, gyakorlatias, engedelem, nem önmagában teher
formality: 0.55
slang_level: 0.15
pace_bpm: 135
pause_default_ms: 330
story_injection_rate: 0.35
breathing_exercise_frequency: 0.32

tone_bias_business: 0.30
tone_bias_scientific: 0.35
tone_bias_spiritual: 0.25
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Parent navigating economic pressures and family responsibility.
# Wellness framing, not clinical. ElevenLabs TTS.

domain_jargon:
  - családi felelősség
  - gazdasági nyomás
  - jóllét
  - önygondoskodás
  - kezelhetőség

persona_scenarios:
  primary_dimension: family_stress
  secondary_dimension: economic_pressure
  integration_dimension: wellness_permission

topic_resonance:
  1: boundaries
  2: burnout_recovery
  3: wellness
  4: family_expectations

template_set: stressed_parent_hu
shares_templates_with: []
```

---

## IMPLEMENTATION NOTES

### Locale-Specific Persona Validation

When planning brands for each locale, ensure:

1. **Locale-Persona Lock**: Each brand is assigned ONE locale and ONE persona (or persona set). A Taiwan brand (locale: zh-TW) cannot use en-US personas.

2. **Pipeline Integration**: Persona IDs from this file are referenced in `brand_registry_locale_extension.yaml` under `persona_affinity` fields.

3. **TTS Alignment**: 
   - **hu-HU**: ElevenLabs only (no Google Neural2 hu-HU support)
   - **ja-JP**: Uses politeness register (丁寧語) in all narration
   - All others: ElevenLabs primary, Google Neural2 fallback (where available)

4. **Content Framing Rules**:
   - **ja-JP**: NEVER "mental health" — use "nervous system," "wellbeing," "self-care"
   - **de-DE**: Science/evidence required, NO spiritual content
   - **hu-HU**: Wellness/self-development preferred, avoid clinical language
   - **zh-CN**: Phase 5 only, content review required, local platforms only
   - **zh-TW, zh-HK**: Body-first framing, practical over clinical
   - **es-US, es-ES**: Culturally aware, no patronizing tone

5. **Storefront Routing** (enforced by CI gate #49):
   - Locale-X brands never routed to non-X storefronts
   - zh-CN NOT via Google Play or Findaway
   - hu-HU NOT via Google Neural2 (ElevenLabs only)

---

## Field Reference

Each persona YAML includes:

| Field | Purpose |
|-------|---------|
| `persona_id` | Unique identifier (used in brand_registry_locale_extension.yaml) |
| `display_name` | Human-readable name |
| `locale` | Locale code (zh-TW, ja-JP, etc.) |
| `territory` | Geographic territory for routing |
| `generation_dialect` | millennial, gen_z, gen_x, mixed |
| `active` | true/false (all are true) |
| `revenue_tier` | 1 (highest priority), 2, 3 |
| `voice_tone` | Descriptive prose of narration voice |
| `formality` | 0.0–1.0 (0 = casual, 1 = formal) |
| `slang_level` | 0.0–1.0 (prevalence of colloquial language) |
| `tone_bias_*` | 0.0–1.0 bias toward business, scientific, spiritual, personal |
| `domain_jargon` | Locale-appropriate terminology |
| `metaphor_style` | Culturally resonant metaphor categories |
| `persona_scenarios` | Primary, secondary, integration dimensions + scenario library |
| `topic_resonance` | Ranked list of topic IDs this persona prioritizes |
| `template_set` | Template identifier for this persona |

---

## Historical Note

This registry was created February 2026 to formalize locale-specific persona definitions that previously existed only as naming conventions in locale_strategy.md. This file is the **authority** for all 36 locale-specific personas and ensures brand planning, content assembly, and validation can enforce the single rule: **Each locale brand uses only personas tagged for that locale.**

