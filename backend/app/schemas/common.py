"""Shared response envelopes.

``Page`` is the pagination envelope the frozen API contract (docs/api-contract.md
section 6.5) requires for list endpoints such as ``/announcements`` and
``/leaderboard``. Keeping one generic shape here means every paginated endpoint reports
totals the same way instead of inventing its own.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_more: bool
