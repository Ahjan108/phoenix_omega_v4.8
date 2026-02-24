# PATCH: catalog_planner.py
# Problem: angle_id defaults to "default_angle" when series_id is not passed.
# Fix: add _derive_angle() to resolve a real angle from topic + persona
#      when series_id is absent. produce_single calls this as fallback.
# Authority: SYSTEMS_DOCUMENTATION §29 — catalog planning hierarchy.

# ─── REPLACE produce_single METHOD ─────────────────────────────────────────

    def produce_single(
        self,
        topic_id: str,
        persona_id: str,
        teacher_id: str = "default_teacher",
        brand_id: str = "phoenix",
        seed: str = "default_seed",
        series_id: Optional[str] = None,
        installment_number: Optional[int] = None,
        angle_id: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> BookSpec:
        """Produce one BookSpec. Required: topic_id, persona_id.
        
        angle_id resolution order:
        1. Caller-supplied angle_id (explicit override)
        2. Derived from series_id + series_templates config (series path)
        3. Derived from topic_id + persona_id via _derive_angle() (fallback)
        4. "default_angle" only if all above fail (should not happen in production)
        """
        if not topic_id or not persona_id:
            raise ValueError("BookSpec requires topic_id and persona_id")

        domains = self._domains.get("domains") or {}
        series_cfg = self._series.get("series") or {}

        # Path 1: Series-based angle resolution (unchanged)
        if series_id and not angle_id:
            s = series_cfg.get(series_id) or {}
            angles = s.get("angles") or []
            if angles:
                angle_id = angles[0]

        # Path 2: Series-based domain resolution (unchanged)
        if series_id and not domain_id:
            s = series_cfg.get(series_id) or {}
            domain_id = s.get("domain") or domain_id

        # NEW Path 3: Derive angle from topic + persona when series absent
        if not angle_id:
            angle_id = self._derive_angle(topic_id, persona_id, series_cfg)

        # domain_id fallback from topic mapping
        if not domain_id:
            domain_id = self._topic_to_domain(topic_id)

        return BookSpec(
            topic_id=topic_id,
            persona_id=persona_id,
            series_id=series_id,
            installment_number=installment_number,
            teacher_id=teacher_id,
            brand_id=brand_id,
            angle_id=angle_id,          # now always a real angle
            domain_id=domain_id or "default_domain",
            seed=seed,
        )

    def _derive_angle(
        self,
        topic_id: str,
        persona_id: str,
        series_cfg: dict,
    ) -> str:
        """Derive a real angle from topic_id + persona_id.
        
        Strategy:
        1. Find series in config whose domain maps to this topic_id.
        2. Among those, prefer series with persona_affinity.high containing persona_id.
        3. Return first angle from the best-matched series.
        4. If nothing matches, return topic_id + "_general" (still better than "default_angle").
        
        This gives the naming engine a real angle for single-book runs
        without requiring the caller to know the series hierarchy.
        """
        topic_to_domain = {v: k for k, v in {
            "anxiety_cluster": "relationship_anxiety",
            "grief_cluster": "grief",
            "shame_cluster": "shame",
        }.items()}
        # extend with full topic→domain mapping from config if available
        if self._domains:
            for d_id, d_cfg in (self._domains.get("domains") or {}).items():
                for t_id in (d_cfg.get("topics") or []):
                    topic_to_domain[t_id] = d_id

        target_domain = topic_to_domain.get(topic_id)

        best_series = None
        best_score = -1

        for series_id, s_cfg in series_cfg.items():
            angles = s_cfg.get("angles") or []
            if not angles:
                continue

            series_domain = s_cfg.get("domain")
            if target_domain and series_domain != target_domain:
                continue  # skip series from different domain

            # Score by persona affinity
            affinity = s_cfg.get("persona_affinity") or {}
            high = affinity.get("high") or []
            medium = affinity.get("medium") or []

            if persona_id in high:
                score = 2
            elif persona_id in medium:
                score = 1
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_series = s_cfg

        if best_series:
            angles = best_series.get("angles") or []
            if angles:
                return angles[0]

        # Last resort — still more informative than "default_angle"
        return f"{topic_id}_general"

    def _topic_to_domain(self, topic_id: str) -> str:
        """Map topic_id to domain_id. Inverse of _domain_to_topic."""
        m = {
            "relationship_anxiety": "anxiety_cluster",
            "grief": "grief_cluster",
            "shame": "shame_cluster",
        }
        return m.get(topic_id, "default_domain")


# ─── REPLACE _domain_to_topic METHOD ────────────────────────────────────────
# (existing method — no change needed, just confirming it stays)

    def _domain_to_topic(self, domain_id: str) -> str:
        """Map domain to a topic slug used by Stage 2 / atoms."""
        m = {
            "anxiety_cluster": "relationship_anxiety",
            "grief_cluster": "grief",
            "shame_cluster": "shame",
        }
        return m.get(domain_id, "relationship_anxiety")
