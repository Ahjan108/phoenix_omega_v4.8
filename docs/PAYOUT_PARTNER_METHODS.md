# Partner Payout Methods — Choice of Best Way

**Not legal or tax advice.** This document is operational and for method selection only. It is not legal or tax advice. Partners and operators should consult their own advisors for legal, tax, and compliance matters.

---

## Purpose

Partner choice of payout method for **international payees** (China, Japan, Taiwan): pay ~$5k/month from US church bank to partners, with partners choosing how they get paid. Config in [config/payouts/payees.yaml](../config/payouts/payees.yaml) (v1.1); see [CHECKLIST](../config/payouts/CHECKLIST.md) for setup and 2-person approval rules.

---

## Cost/speed estimates (last verified date)

**Cost/speed estimates last verified: 2026-03-08.** Update this date when rates or fees change. All figures below are **estimates** for ~$5k USD transfer.

---

## Four options

### 1. ACH → Wise USD (recipient has Wise account)

**Flow:** US church bank → ACH → recipient Wise USD account → recipient converts locally (CNY/JPY) and withdraws to bank or wallet.

| Step | Cost |
|------|------|
| Your cost (ACH) | $0 |
| Their cost (FX + withdrawal) | ~$25–45 |
| **Total (est.)** | **~$25–45** |

- **Speed:** 1–2 days.
- **API:** Yes (Wise Business API + Dwolla or Stripe for ACH).
- **Recipient needs:** Wise account with USD account details (routing/account); they share details with you like a US vendor.
- **Compliance:** Domestic ACH; recipient handles FX and local compliance.

---

### 2. Wise direct (USD → local bank or wallet)

**Flow:** US church bank → Wise → FX conversion → local payout to recipient bank, Alipay, or WeChat Pay.

| Step | Cost |
|------|------|
| Your cost (Wise fee + FX) | ~$30–55 |
| Their cost | $0 |
| **Total (est.)** | **~$30–55** |

- **Speed:** Minutes to 1 day (Alipay/WeChat often same day).
- **API:** Yes (Wise Business API: recipients, quotes, transfers, fund).
- **Recipient needs:** Bank account (China/Japan/Taiwan) or Alipay/WeChat Pay ID.
- **Compliance:** Wise handles FX and local rails; you provide recipient details and payment reference.

---

### 3. Crypto stablecoin (USDT/USDC)

**Flow:** US church bank → ACH to exchange → buy USDT/USDC → send on TRON/Polygon → recipient exchange or wallet → they convert to local currency.

| Step | Cost |
|------|------|
| Your cost (ACH + trade + network) | ~$6 |
| Their cost (conversion) | ~$5 |
| **Total (est.)** | **~$10–15** |

- **Speed:** Minutes.
- **API:** Yes (exchange APIs e.g. Binance.US, Kraken).
- **Recipient needs:** Wallet or exchange account; they cash out locally (P2P, exchange).
- **Compliance:** Optional and **policy-gated** for CN/JP/TW (see Compliance gate below). Volatility and regulatory risk; keep records for audit.

---

### 4. HK clearing (institutional)

**Flow:** US church bank → ACH to USD clearing account (HK fintech/bank) → FX in HK → local payout to China/Taiwan bank.

| Step | Cost |
|------|------|
| Your cost (FX + local payout) | ~$8–15 |
| **Total (est.)** | **~$8–15** |

- **Speed:** Same day (often).
- **API:** Sometimes (depends on HK provider).
- **Recipient needs:** Local bank account in China or Taiwan.
- **Compliance:** Banking rails; provider handles local requirements.

---

## Comparison table

| Method | Your cost ($5k) | Their cost | Speed | API | Risk |
|--------|------------------|------------|-------|-----|------|
| **ACH → Wise USD** | $0 | ~$25–45 | 1–2 days | Yes | Low |
| **Wise direct** | ~$30–55 | $0 | min–1 day | Yes | Low |
| **Crypto stablecoin** | ~$6 | ~$5 | Minutes | Yes | Medium |
| **HK clearing** | ~$8–15 | — | Same day | Sometimes | Low |

*Estimates last verified: 2026-03-08.*

---

## Risk table per method

| Method | Main risks | Notes |
|--------|------------|--------|
| **Crypto** | Volatility, compliance, irreversible sends, recipient must handle off-ramp | Policy-gated for CN/JP/TW; use only when allowed and documented |
| **ACH (US bank-to-bank)** | US-only (recipient must have US-style account e.g. Wise USD), timing (1–2 days) | Safest for US-domestic-style flows |
| **Wise direct** | FX spread, provider limits, dependency on Wise | Most predictable for international fiat |
| **HK clearing** | Provider availability, less common API | Good for China/Taiwan at volume |

**Default fallback method:** When the primary method fails or is unavailable (e.g. compliance block, provider outage), use the **first entry in the payee’s `fallback_methods`** in [config/payouts/payees.yaml](../config/payouts/payees.yaml). If not set, document a system default (e.g. **Wise direct**) and use that. Do not store sensitive fallback details in YAML; use `vault_ref` only.

---

## Compliance gate

Per-method **allowed: true/false** by **country** (e.g. CN, JP, TW) and **partner type** (e.g. individual vs org). Config and operations must respect this.

- **Crypto:** Explicitly **policy-gated** for CN/JP/TW corridors. Only use when your policy and config allow it for that country and partner type.
- **Wise (USD or direct):** Generally allowed for international payees; confirm per country with Wise.
- **ACH:** Allowed when recipient has US-routed account (e.g. Wise USD).
- **HK clearing:** Allowed where provider supports the corridor.

Document the current policy in config or a separate compliance matrix; do not store sensitive payout details (wallets, account numbers) in repo—use **vault_ref** only (see payees.yaml v1.1).

---

## Recommendation by recipient type

- **Individual, prefers simple:** Wise direct to local bank or Alipay/WeChat (China).
- **Individual, has Wise:** ACH → Wise USD; they convert locally (~$0 your cost).
- **Org / higher volume:** Consider HK clearing if provider and API available.
- **Tech-savvy, policy allows:** Crypto stablecoin for lowest cost and speed; ensure compliance gate and audit trail.

---

## References

- **Wise Business API:** [Wise API docs](https://wise.com/help/articles/2946485/api) — recipients, quotes, transfers, fund.
- **ACH:** Dwolla or Stripe for ACH automation (US → US or US → Wise USD).
- **Exchange APIs:** e.g. Binance.US, Kraken (trading + withdraw); use only with policy and vault_ref for credentials.
- **HK fintech:** Name TBD when chosen; use for HK clearing option.
- **Config:** [config/payouts/payees.yaml](../config/payouts/payees.yaml) (schema v1.1), [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md).
- **Governance:** For VWM 90/10, bank accounts, and church agreements, see [CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md](CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md) (if present).

No API keys or secrets in this doc; store in credentials/vault only.
