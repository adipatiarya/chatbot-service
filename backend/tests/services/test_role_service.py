import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_role_service
from app.core.exception import DuplicateEntryError
from app.models.role import RoleCreate

@pytest.mark.asyncio
async def test_create_permissions(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    permission=['can_create_user','can_update_user','can_add_role'] #permission ini harus sudah ada
    await service.create_permissions(permission)


@pytest.mark.asyncio
async def test_create_permissions_with_duplicate(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    permission=['dup','dup', 'nodup']
    with pytest.raises(DuplicateEntryError):
        await service.create_permissions(permission)


@pytest.mark.asyncio
async def test_create_role_permission_with_exist_permissions(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    role_name = 'supervisor'
    
    permission=['can_create_user','can_update_user','can_add_role'] #permission ini harus sudah ada

    await service.create_permissions(permission) #dibuat buat exist

    data = RoleCreate(
        name=role_name,
        permission=permission
    )
    role = await service.create_role(data)

    #harus punya atribut permission
    assert hasattr(role, "permissions")

    #jumlah len harus sama  
    assert len(role.permissions) == len(permission)

    #value permission sesuai input
    role_perm_names = [perm.name for perm in role.permissions]
    assert set(role_perm_names) == set(permission)

@pytest.mark.asyncio
async def test_create_role_permission_with_not_exist_permissions(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    role_name = 'supervisor'
    
    permission=['can_create_user','can_update_user','can_add_role'] #permission ini harus sudah ada

    #await service.create_permissions(permission) #jangan di buat exist

    data = RoleCreate(
        name=role_name,
        permission=permission
    )
    role = await service.create_role(data)

    assert hasattr(role, "permissions")
    assert len(role.permissions) == 0

@pytest.mark.asyncio
async def test_create_role_permission_with_duplicate_roles(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    role_name = 'supervisor'
    
    permission=['can_create_user','can_update_user','can_add_role'] #permission ini harus sudah ada

    #await service.create_permissions(permission) #jangan di buat exist

    data = RoleCreate(
        name=role_name,
        permission=permission
    )
    await service.create_role(data)
    
    #buat lagi. harus error
    with pytest.raises(DuplicateEntryError):
        await service.create_role(data)

@pytest.mark.asyncio
async def test_update_role(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    #buat role dan permision dulu biar exist
    role_name = 'supervisor'
    permission=['can_create_user','can_update_user','can_add_role'] #permission ini harus sudah ada
    await service.create_permissions(permission) #dibuat buat exist
    data = RoleCreate(
        name=role_name,
        permission=permission
    )
    role = await service.create_role(data)
    #harus punya atribut permission
    assert hasattr(role, "permissions")
    #jumlah len harus sama  
    assert len(role.permissions) == len(permission)
    #value permission sesuai input
    role_perm_names = [perm.name for perm in role.permissions]
    assert set(role_perm_names) == set(permission)

    #edit_role
    #dapatkan idnnya
    role = await service.role_crud.get_by_name(role_name)
    assert role_name == role.name
