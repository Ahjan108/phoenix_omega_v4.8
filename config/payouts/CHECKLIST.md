# PHOENIX PAYOUT — WHAT YOU MUST GIVE ME

## 1. Plaid credentials (from dashboard.plaid.com)

- [ ] **client_id**
- [ ] **secret**

Put in `config/payouts/credentials.yaml` under `plaid:`

---

## 2. Bank connections (24 churches)

Connect each church's Bluevine account via Plaid Link.

Run: `python -m payouts.link_server` → open http://localhost:5000

- [ ] CHURCH_01 through CHURCH_24

---

## 3. Bluevine account last 4 digits (24 churches)

- [ ] CHURCH_01: ____  …  CHURCH_24: ____

Put in `churches.yaml` (bluevine_account_last4) or `fill_template.csv` (bluevine_last4).

---

## 4. Payee info (24 payees — who gets the 90%)

- [ ] PAYEE_01: name ____  bank_last4 ____  …  PAYEE_24

Put in `payees.yaml` (display_name, bank_last4) or `fill_template.csv` (payee_name, payee_bank_last4).

---

## Summary

| # | What | Where |
|---|------|-------|
| 1 | Plaid client_id, secret | credentials.yaml |
| 2 | 24 bank connections | credentials.yaml (auto when you connect) |
| 3 | 24 Bluevine last4 | churches.yaml or fill_template.csv |
| 4 | 24 payee names + bank last4 | payees.yaml or fill_template.csv |
