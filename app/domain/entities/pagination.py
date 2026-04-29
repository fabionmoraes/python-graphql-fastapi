from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PageResult(Generic[T]):
    items: list[T]
    total_count: int
    has_next_page: bool
    has_previous_page: bool
