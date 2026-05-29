from typing import Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")

class DataList(BaseModel, Generic[T]):
    count: int
    data: list[T]

class Paginated(BaseModel, Generic[T]):
    data: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    limit: int = 10
    total_pages: int = 0