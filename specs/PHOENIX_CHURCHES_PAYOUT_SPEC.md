# Phoenix Churches Payout — Tech Spec (stub)

**Status:** Stub. Architecture, data model, workflow, and compensating controls to be expanded when payout package is implemented.

---

## Scope

- **US domestic flow:** Plaid sync, Bluevine, 24 churches, 90/10 split, human-in-the-loop execution. Config: [config/payouts/churches.yaml](../config/payouts/churches.yaml), [config/payouts/payees.yaml](../config/payouts/payees.yaml), [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md).
- **International partner payouts:** Partner choice of method (Wise USD, Wise direct, crypto, HK clearing). Config: payees.yaml schema v1.1 (payout_method, vault_ref, fallback_methods, etc.). Full options and compliance gate: [docs/PAYOUT_PARTNER_METHODS.md](../docs/PAYOUT_PARTNER_METHODS.md).

---

## Payee config

- **Domestic:** display_name, bank_last4 (no payout_method → treat as domestic).
- **International:** Optional payout_method, status, effective_from, effective_to, vault_ref only (no plain wallet/account IDs), fallback_methods, external_payout_id, last_paid_at. See payees.yaml comments and PAYOUT_PARTNER_METHODS.md.

---

## References

- [docs/PAYOUT_PARTNER_METHODS.md](../docs/PAYOUT_PARTNER_METHODS.md) — Partner payout methods, compliance gate, risk table, default fallback
- [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md) — Operational checklist; 2-person approval for method change and first payout to new payee
- [docs/CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md](../docs/CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md) — If present: VWM 90/10, bank accounts, agreements

Provider APIs (Wise, Dwolla, exchange, HK) and automation are out of scope for this stub; add when implementing the payout package.
