# TEACHER MODE INVARIANTS

Teacher Mode is a strict publishing regime. It guarantees teacher identity integrity, deterministic builds, and platform-safe scaling. When `teacher_mode=true`, the following invariants apply:

**1. No Placeholders** — All slots must resolve to real atoms. If any slot cannot resolve, build fails.

**2. No Runtime Generation** — Content must come from: teacher_native atoms; teacher_synthetic atoms (TDEL, approved); practice_fallback atoms (EXERCISE only, opt-in). No compile-time LLM generation is permitted.

**3. Doctrine Consistency** — All teacher atoms in a book must share identical: teacher_id, doctrine_version, doctrine_fingerprint (and when adopted: teacher_doctrine_epoch_id). Mixed doctrine within one book is forbidden. No wave may mix more than one doctrine_epoch_id per teacher unless explicitly allowed.

**4. Synthetic Governance** — Synthetic expansion is: offline only; fingerprinted; human approved; ratio capped. Caps: total synthetic ≤ 40%; STORY synthetic ≤ 30%; HOOK/EXERCISE synthetic ≤ 50%.

**5. Fallback Restrictions** — Fallback: EXERCISE only; explicit opt-in; teacher EXERCISE pool must be non-zero; teacher EXERCISE ≥ 60% of exercises; teacher total content ≥ 70% of book. Fallback is a temporary/debt state where possible; max fallback books per teacher per wave (e.g. ≤ 20%); sunset rule when native inventory increases.

**6. Structural Integrity** — ≥ 3 distinct STORY emotional bands per book; no atom reused within same book (Gate O); slot types must match format exactly; exercise families included in entropy checks.

**7. Determinism** — All candidate pools must be sorted by (source_priority, stable_hash(atom_id)). This ensures identical builds across machines.

**8. Doctrine Freeze** — doctrine.yaml must: match schema allowlist; declare doctrine_schema_version; be fingerprinted. Schema changes require explicit version bump.

**9. Pre-Compile Coverage Gate** — Teacher coverage must be validated before assembly. If any required slot inventory is insufficient, build fails. No partial plans are emitted.

**10. Catalog Protection** — Wave-level enforcement ensures: doctrine density caps; structural diversity; metadata entropy; synthetic debt monitoring.

Teacher Mode is designed to: prevent identity drift (doctrine epochs); prevent synthetic dominance (debt ledger + throttles); prevent nondeterministic builds; prevent schema creep; prevent silent fallback; prevent fallback as a permanent loophole (debt/sunset). It is intentionally strict. TDEL is a bridge, not a factory.
