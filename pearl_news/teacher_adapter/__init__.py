"""
Pearl News Teacher Adapter — derive article-ready teacher payload from Pearl Prime.

Authority: specs/PEARL_NEWS_TEACHER_ADAPTER_SPEC.md.

Flow: Pearl Prime teacher truth -> news adapter -> article.
"""
from pearl_news.teacher_adapter.adapter import (
    BuildResult,
    NewsTeacherPayload,
    build_news_payload,
    get_teacher_news_topics,
    validate_topic_fit,
)
from pearl_news.teacher_adapter.pairing import (
    teacher_story_pairing_ok,
)
from pearl_news.teacher_adapter.validation import (
    validate_adapter_payload,
    AdapterValidationResult,
)

__all__ = [
    "BuildResult",
    "NewsTeacherPayload",
    "build_news_payload",
    "get_teacher_news_topics",
    "validate_topic_fit",
    "teacher_story_pairing_ok",
    "validate_adapter_payload",
    "AdapterValidationResult",
]
