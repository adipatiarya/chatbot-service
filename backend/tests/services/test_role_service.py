import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import logger
from app.api.deps import get_role_service
from app.core.exception import DuplicateEntryError
from app.models.role import RoleCreate, RoleUpdate

from tests.helpers.util import random_lower_string

@pytest.mark.asyncio
async def test_create_permissions(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    permission = [random_lower_string() for _ in range(3)]

    await service.create_permissions(permission)


@pytest.mark.asyncio
async def test_create_permissions_with_duplicate(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    permission_strs=['dup','dup', 'nodup']
    with pytest.raises(DuplicateEntryError):
        await service.create_permissions(permission_strs)


@pytest.mark.asyncio
async def test_create_role_permission_with_exist_permissions(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    role_name = 'supervisor'
    
    permission = [random_lower_string() for _ in range(3)]

    await service.create_permissions(permission) #dibuat buat exist

    data = RoleCreate(
        name=role_name,
        permission_strs=permission
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
    
    permission = [random_lower_string() for _ in range(3)]

    #await service.create_permissions(permission) #jangan di buat exist

    data = RoleCreate(
        name=role_name,
        permission_strs=permission
    )
    role = await service.create_role(data)

    assert hasattr(role, "permissions")
    assert len(role.permissions) == 0

@pytest.mark.asyncio
async def test_create_role_permission_with_duplicate_roles(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)

    role_name = 'supervisor'
    
    permission = [random_lower_string() for _ in range(3)]

    #await service.create_permissions(permission) #jangan di buat exist

    data = RoleCreate(
        name=role_name,
        permission_strs=permission
    )
    await service.create_role(data)
    
    #buat lagi. harus error
    with pytest.raises(DuplicateEntryError):
        await service.create_role(data)

@pytest_asyncio.fixture(scope="function")
async def role_id(async_db: AsyncSession)->str:

    service = get_role_service(async_db)
    permission_strs=['aaa','bbb','ccc']
    await service.create_permissions(permission_strs)

    role_in = RoleCreate(name='baru', description='Hello Role', permission_strs=permission_strs)
    role = await service.create_role(role_in)
    return role.id

@pytest.mark.asyncio
async def test_update_role(async_db: AsyncSession, role_id) -> None:
    service = get_role_service(async_db)
    role_in = RoleUpdate(name='baru')
    role = await service.role_crud.get_by_name_or_id(role_id)

    if role:
        logger.info("BLOK INI DI EKSEKUSI")
        data_ret = await service.update_role(role, role_in)
        assert hasattr(data_ret, "permissions")
        assert data_ret.id == role.id
        assert data_ret.name == role_in.name

@pytest.mark.asyncio
async def test_create_role_with_exist_role(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    
    role_in = RoleUpdate(name='baru')
    await service.create_role(role_in)
    
    #buat lagi. harus error
    with pytest.raises(DuplicateEntryError):
        await service.create_role(role_in)
  
   
@pytest.mark.asyncio
async def test_update_role_with_fake_id(async_db: AsyncSession) -> None:
    service = get_role_service(async_db)
    role_in = RoleUpdate(name='jaja')
    role = await service.role_crud.get_by_name_or_id(7778)

    if role:
        logger.info("BLOK INI DI EKSEKUSI")
        data_ret = await service.update_role(role, role_in)
        assert hasattr(data_ret, "permissions")
        assert data_ret.id == role.id
        assert data_ret.name == role_in.name

    logger.info("BLOK DILEWATI")

@pytest.mark.asyncio
async def test_update_role_permission_only(async_db: AsyncSession, role_id) -> None:
    service = get_role_service(async_db)

 
    role = await service.role_crud.get_by_name_or_id(role_id)
    role_perm_names = [perm.name for perm in role.permissions]
    assert set(role_perm_names) == set(['aaa','bbb','ccc'])  #target permisi

    role_in = RoleUpdate(permission_strs=['bbb','yyy'])

    if role:
        logger.info("BLOK INI DI EKSEKUSI")
        data_ret = await service.update_role(role, role_in)
        assert data_ret

        assert hasattr(data_ret, "permissions")
        assert len(data_ret.permissions) == 1
        role_perm_names = [perm.name for perm in data_ret.permissions]
        assert set(role_perm_names) == set(['bbb'])
        assert data_ret.name == role.name


@pytest.mark.asyncio
async def test_update_role_name_only(async_db: AsyncSession, role_id) -> None:
    service = get_role_service(async_db)

    role = await service.role_crud.get_by_name_or_id(role_id)
    role_perm_names = [perm.name for perm in role.permissions]
    assert set(role_perm_names) == set(['aaa','bbb','ccc'])  #target permisi

    role_in = RoleUpdate(name='jenggot')

    if role:
        logger.info("BLOK INI DI EKSEKUSI")
        data_ret = await service.update_role(role, role_in)
        assert data_ret

        assert hasattr(data_ret, "permissions")
        assert len(data_ret.permissions) == 3
        role_perm_names = [perm.name for perm in data_ret.permissions]
        assert set(role_perm_names) == set(['aaa','bbb','ccc'])
        assert data_ret.name == 'jenggot'

@pytest.mark.asyncio
async def test_delete_role(async_db: AsyncSession, role_id) -> None:
   service = get_role_service(async_db)
   role = await service.role_crud.get_by_name_or_id(role_id)
   assert role #cek ini idnya masih ada
   if role:
       await service.role_crud.delete(role)
   
   role = await service.role_crud.get_by_name_or_id(role_id)
   assert role is None #seharusnya kosong karena sudah di hapus