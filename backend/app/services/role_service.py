from app.models.role import Role, RoleCreate
from app.repositories.cruds.role_crud import RoleCrud
from app.repositories.cruds.permission_crud import PermissionCrud

class RoleService:
    def __init__(self, role_crud: RoleCrud, permission_crud: PermissionCrud):
        self.role_crud = role_crud
        self.permission_crud = permission_crud

    async def create_role(self, role_create: RoleCreate) -> Role:
        role_create.name = role_create.name.lower()
        role_model = Role.model_validate(role_create)
        role = await self.role_crud.add(role_model)
        return role