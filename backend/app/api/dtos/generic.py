from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class DataList(BaseModel, Generic[T]):
    count: int
    data: list[T]