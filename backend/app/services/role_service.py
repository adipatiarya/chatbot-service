import uuid

from app.models.role import Role, RoleCreate
from app.models.permission import Permission, PermissionCreate

from app.repositories.cruds.role_crud import RoleCrud
from app.repositories.cruds.permission_crud import PermissionCrud
from app.utils import logger
class RoleService:
    def __init__(self, role_crud: RoleCrud, permission_crud: PermissionCrud):
        self.role_crud = role_crud
        self.permission_crud = permission_crud

    async def assign_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> Role:
        logger.info(f"R {role_id} P = {permission_id}")

    async def create_role(self, role_in: RoleCreate) -> Role:
        role_in.name = role_in.name.lower()
        role_model = Role.model_validate(role_in)
        user_data = role_in.model_dump(exclude_unset=True)
        
        role = await self.role_crud.add(role_model)
        if "permission" in user_data:
            for m in user_data["permission"]:
                perm = await self.permission_crud.get_by_name(m)
                if perm:
                   await self.assign_permission(role.id, perm.id)
        return role
    
    async def create_permissions(self, permissions: list[str]) -> list[Permission]:
        model_perms = []
        for m in permissions:
            perm_in = PermissionCreate(name=m)
            model_perms.append(perm_in)
            
        permission_objs = [Permission.model_validate(perm) for perm in model_perms]

        return await self.permission_crud.add_many( permission_objs )