
from datetime import datetime
from typing import Any, Dict
import uuid

from pydantic import BaseModel

from app.utils import all_perms


class RolePermissionDto(BaseModel):
    name: str
    description: Any | None = None
    permission: Dict[str, Dict[str, bool]] = all_perms()

class RolePermissionDetail(BaseModel):
    id: uuid.UUID
    created_at: datetime
    name: str
    description: Any | None = None
    permission: Dict[str, Dict[str, bool]] = all_perms()