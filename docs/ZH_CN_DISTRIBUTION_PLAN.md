# Mainland China (zh-CN) Distribution Pipeline

## The zh-CN Problem

Mainland China is a unique distribution challenge among Phoenix's 12 locales. Unlike every other market, Google Play and Findaway—our primary aggregators—are not available in mainland China. Apple Books provides limited reach. This means that to serve the 900-million-person Chinese audiobook market, we must build a separate distribution pipeline using local platforms.

This is not a minor logistics issue. It is a hard blocker on producing zh-CN content until the infrastructure is in place.

## Why zh-CN Is Different

Google Play is blocked in mainland China by the Great Firewall. Findaway, Spotify, and most Western audiobook aggregators cannot distribute to mainland storefronts. Apple Books has limited reach. This is not a temporary issue or a minor market friction—it is architectural. To serve mainland readers, we must use platforms that operate within the Chinese internet ecosystem: Ximalaya, NetEase Cloud Music, WeChat Read, and Dedao. Each requires separate publisher accounts, separate onboarding, and separate metadata in Simplified Chinese.

Additionally, content in mainland China undergoes review by local regulatory bodies. This is not identical to international content standards. Certain wellness and mental health messaging requires sensitivity to local regulatory guidance.

## Required Local Platforms

**Ximalaya (喜马拉雅)** — Audio content platform native to mainland. Largest dedicated audiobook distribution channel. Requires verified publisher account, content metadata in Simplified Chinese, and compliance with mainland content guidelines.

**NetEase Cloud Music (网易云音乐)** — Music and audio streaming service with audiobook section. Significant reach in metropolitan areas. Requires NetEase partner account, metadata, and content review approval.

**WeChat Read (微信读书)** — Tencent's integrated audiobook service within the WeChat ecosystem. Critical reach for younger audiences. Requires Tencent publisher partnership and embedded content review.

**Dedao (得到)** — Premium self-help audiobook platform. Smaller but highly engaged audience for wellness and self-development content. Requires separate publisher verification.

Each platform has its own account structure, metadata schema, content submission format, and approval timeline. Setting up all four accounts before producing content is mandatory.

## Onboarding Requirements

Each platform requires:

- **Publisher account verification.** Legal entity registration in mainland China (or partner agent). Bank account for payouts. Business license documentation. Timeline: 2–4 weeks.

- **Content format specifications.** Audio codec requirements (typically MP3 320kbps or AAC), metadata XML schemas specific to each platform, cover art specifications, and episode naming conventions. Each platform has slightly different requirements.

- **Metadata in Simplified Chinese.** Book titles, descriptions, author names, and category tags must be translated and localized, not just transliterated. Terminology differs significantly from en-US (different search language, different positioning language).

- **Content review and compliance.** Mainland China has specific content review requirements. Submissions must undergo platform review; timeline is 1–2 weeks per batch. Rejected content requires revision before resubmission.

- **Tax documentation and payout setup.** Remittance to foreign bank accounts requires specific tax forms and banking relationships. Work with a local financial services partner.

## Prerequisite Checklist

Before producing any zh-CN content, complete the following:

- [ ] **Local distributor account opened.** At least one mainland Chinese publisher agent or verified entity account established with Ximalaya.

- [ ] **Content metadata translated.** Book titles, descriptions, author bios, and positioning language translated from en-US to Simplified Chinese by native translator familiar with mainland Chinese search behavior and platform conventions.

- [ ] **TTS voice auditioned for Putonghua quality.** ElevenLabs eleven_multilingual_v2 zh-CN or Google cmn-CN-Wavenet-A tested with full audiobook sample. Confirm natural Putonghua accent (mainland Mandarin, not Taiwan or Hong Kong variants).

- [ ] **Content review requirements researched.** Legal/compliance review of which wellness topics, mental health messaging, and self-help frameworks are acceptable under mainland guidelines. Document any messaging constraints.

- [ ] **All four platform onboarding completed.** Ximalaya, NetEase Cloud Music, WeChat Read, Dedao accounts verified and ready to receive submissions.

- [ ] **Financial setup verified.** Tax and payout infrastructure in place with accounting partner. Test transfer on dummy submission.

## Text-to-Speech for zh-CN

ElevenLabs eleven_multilingual_v2 supports zh-CN (Mandarin, mainland China accent). This is the primary TTS choice. Google cmn-CN-Wavenet-A is available as fallback but is lower quality for mainland Putonghua. Ensure voice testing explicitly uses mainland Mandarin accent samples, not Taiwan or Hong Kong variants.

## Rollout Phase

zh-CN is Phase 5 in the locale rollout strategy (per locale_strategy.md). Planned for Months 10–18 of the multi-market expansion. Do not begin zh-CN content production until:

1. All four local platform accounts are verified and onboarded.
2. Metadata translation is complete and reviewed by mainland market expert.
3. TTS voice has been auditioned and approved.
4. Legal/compliance review of content messaging is documented.
5. Financial infrastructure is operational.

This is longer than earlier phases (Phase 1 Taiwan, Phase 2 Japan, Phase 3 Korea, Phase 4 European locales) because the distribution infrastructure must be built first.

## Connection to Registry

The zh-CN locale is already defined in `config/localization/locale_registry.yaml` with:

- `tts_provider: elevenlabs` (primary)
- `tts_fallback: google_neural2`
- `tts_locale_code: zh-CN`
- `storefront_ids: { google_play: null, findaway: null, apple_books: CN, kobo: null, local_platforms: [ximalaya, netease_cloud_music, wechat_read, dedao] }`

The zh-CN entry documents that Google Play and Findaway are unavailable and that local platforms are required. This document details what that means operationally.

## Next Steps

1. Identify or establish mainland Chinese publisher agent or partner entity.
2. Prioritize Ximalaya account setup (largest audiobook platform).
3. Engage translator for content metadata Simplified Chinese localization.
4. Request TTS samples from ElevenLabs for zh-CN accent validation.
5. Schedule legal/compliance review of wellness content messaging.
6. Plan NetEase, WeChat Read, Dedao onboarding in parallel once Ximalaya is complete.
7. Update this plan with account verification dates and contact information as accounts go live.

This is not optional infrastructure. Do not produce zh-CN audiobooks until this checklist is complete.
