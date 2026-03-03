# Stage 6: Plan → prose output (manuscript/ebook).
# Prose resolution and book rendering; used by pipeline and QA render_plan_to_txt.

from phoenix_v4.rendering.prose_resolver import (
    PlanContext,
    RenderResult,
    resolve_prose_for_plan,
)
from phoenix_v4.rendering.book_renderer import (
    RenderOptions,
    TxtWriter,
    render_book,
)

__all__ = [
    "PlanContext",
    "RenderResult",
    "RenderOptions",
    "resolve_prose_for_plan",
    "render_book",
    "TxtWriter",
]
