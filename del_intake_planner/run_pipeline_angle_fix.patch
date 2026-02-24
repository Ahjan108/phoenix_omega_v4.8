# PATCH: run_pipeline.py
# Problem: run_pipeline.py never passes angle_id to produce_single.
#          With _derive_angle() now in catalog_planner, this is partially fixed.
#          But expose angle_id as an explicit CLI arg so power users can override.
#
# Changes:
# 1. Add --angle optional CLI argument
# 2. Pass angle_id to produce_single
# 3. Add --series requirement warning if angle matters for naming

# ─── ADD TO ARGUMENT PARSER ─────────────────────────────────────────────────

    # Existing args assumed: --topic, --persona, --seed, --series, --installment
    # ADD:
    parser.add_argument(
        "--angle",
        type=str,
        default=None,
        help=(
            "Angle ID for this book (e.g. 'at_work', 'public_speaking'). "
            "If not supplied, angle is derived from topic + persona via series config. "
            "Required for deterministic naming engine output."
        ),
    )

# ─── ADD TO produce_single CALL ─────────────────────────────────────────────

    # BEFORE (never passed angle_id):
    # book_spec = planner.produce_single(
    #     topic_id=topic_id,
    #     persona_id=persona_id,
    #     teacher_id="default_teacher",
    #     brand_id="phoenix",
    #     seed=seed,
    #     series_id=series_id,
    #     installment_number=installment_number,
    # )

    # AFTER (passes angle_id):
    book_spec = planner.produce_single(
        topic_id=topic_id,
        persona_id=persona_id,
        teacher_id="default_teacher",
        brand_id="phoenix",
        seed=seed,
        series_id=series_id,
        installment_number=installment_number,
        angle_id=args.angle,            # NEW — None triggers _derive_angle() fallback
    )

# ─── ADD VALIDATION WARNING ─────────────────────────────────────────────────
# After produce_single, before any downstream use:

    if book_spec.angle_id.endswith("_general"):
        import warnings
        warnings.warn(
            f"angle_id resolved to fallback '{book_spec.angle_id}' for "
            f"topic='{topic_id}', persona='{persona_id}'. "
            f"Naming engine will produce a less-specific title. "
            f"Pass --series <id> or --angle <id> for a precise angle.",
            UserWarning,
            stacklevel=2,
        )
