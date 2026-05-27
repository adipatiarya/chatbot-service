import uuid

from sqlmodel import delete

from app.models.role import Role, RoleCreate,RolePermission
from app.models.permission import Permission, PermissionCreate

from app.repositories.cruds.role_crud import RoleCrud
from app.repositories.cruds.permission_crud import PermissionCrud

class RoleService:
    def __init__(self, role_crud: RoleCrud, permission_crud: PermissionCrud):
        self.role_crud = role_crud
        self.permission_crud = permission_crud

    async def assign_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> Role:        

        link = RolePermission(role_id=role_id, permission_id=permission_id)
        self.role_crud.session.add(link)
        await self.role_crud.session.commit()
        await self.role_crud.session.refresh(link)

    async def create_role(self, role_in: RoleCreate) -> Role:
        role_in.name = role_in.name.lower()
        role_model = Role.model_validate(role_in)
        user_data = role_in.model_dump(exclude_unset=True)
        
        role = await self.role_crud.add(role_model)
        if "permission" in user_data:

            #kosongkan dulu
            await self.role_crud.session.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
            await self.role_crud.session.commit()

            for m in user_data["permission"]:
                perm = await self.permission_crud.get_by_name(m)
                if perm:
                   await self.assign_permission(role.id, perm.id)
        return await self.role_crud.permissions(role.id)
    
    async def create_permissions(self, permissions: list[str]) -> list[Permission]:
        model_perms = []
        for m in permissions:
            perm_in = PermissionCreate(name=m)
            model_perms.append(perm_in)
            
        permission_objs = [Permission.model_validate(perm) for perm in model_perms]

        return await self.permission_crud.add_many( permission_objs )