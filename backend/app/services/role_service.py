import uuid

from sqlmodel import delete

from app.models.role import Role, RoleCreate,RolePermission, RoleUpdate
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
        role_data = role_in.model_dump(exclude_unset=True)
        
        role = await self.role_crud.add(role_model)
        if "permission_strs" in role_data:

            #kosongkan dulu
            await self.role_crud.session.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
            await self.role_crud.session.commit()

            for m in role_data["permission_strs"]:
                perm = await self.permission_crud.get_by_name_or_id(m)
                if perm:
                   await self.assign_permission(role.id, perm.id)
        return await self.role_crud.get_by_name_or_id(role.id)
    
    async def update_role(self, db_role:Role, role_in: RoleUpdate) -> Role:
        role_data = role_in.model_dump(exclude_unset=True)
        if "name" in role_data:
            role_data["name"] = role_data["name"].lower()

        if "permission_strs" in role_data:
            #kosongkan dulu
            await self.role_crud.session.execute(delete(RolePermission).where(RolePermission.role_id == db_role.id))
            await self.role_crud.session.commit()
            for m in role_data["permission_strs"]:
                perm = await self.permission_crud.get_by_name_or_id(m)
                if perm:
                   await self.assign_permission(db_role.id, perm.id)
        db_role.sqlmodel_update(role_data)
        await self.role_crud.add(db_role)
        return await self.role_crud.get_by_name_or_id(db_role.id)
    
    async def create_permissions(self, permissions: list[str]) -> list[Permission]:
        model_perms = []
        for m in permissions:
            perm_in = PermissionCreate(name=m)
            model_perms.append(perm_in)
            
        permission_objs = [Permission.model_validate(perm) for perm in model_perms]

        return await self.permission_crud.add_many( permission_objs )