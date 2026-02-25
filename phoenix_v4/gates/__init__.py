# Phoenix V4 — Hard entry gates (run before Stage 1).
# Tuple viability preflight: fail early, fail deterministically.

from phoenix_v4.gates.check_tuple_viability import check_tuple_viability

__all__ = ["check_tuple_viability"]
