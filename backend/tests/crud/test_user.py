import uuid

from fastapi.encoders import jsonable_encoder
import pytest
from tests.helpers.util import random_email, random_lower_string
from app.models.user import UserCreate, User, UserUpdate
from app.core.security import verify_password
from sqlmodel import Session
from pwdlib.hashers.bcrypt import BcryptHasher
from app import crud

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_user(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")

@pytest.mark.asyncio
async def test_authenticate_user(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    authenticate_user = await crud.authenticate(session=async_db, email=email, password=password)
    assert authenticate_user
    assert user.email == authenticate_user.email

@pytest.mark.asyncio
async def test_not_authenticate_user(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user = await crud.authenticate(session=async_db, email=email, password=password)
    assert user is None

@pytest.mark.asyncio
async def test_check_user_is_active_inactive(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    assert user.is_active is False

@pytest.mark.asyncio
async def test_check_user_is_superuser(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True,role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    assert user.is_superuser is True

@pytest.mark.asyncio
async def test_check_user_is_normal_user(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    assert user.is_superuser is False

@pytest.mark.asyncio
async def test_get_user(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    user_2 = await async_db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)

@pytest.mark.asyncio
async def test_update_user(async_db: AsyncSession, role_id:uuid.UUID) -> None :
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await crud.create_user(session=async_db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
       await  crud.update_user(session= async_db, db_user=user, user_in=user_in_update)
    user_2 = await async_db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    verified, _ = verify_password(plain_password= new_password, hashed_password=user_2.hashed_password)
    assert verified


# def test_authenticate_user_with_bcrypt_upgrades_to_argon2(sess: Session) -> None:
#     """Uji bahwa pengguna dengan hash kata sandi bcrypt ditingkatkan menjadi argon2 saat login."""
#     email = random_email()
#     password = random_lower_string()

#     #Buat hash bcrypt secara langsung (mensimulasikan kata sandi lama).
#     bcrypt_hasher = BcryptHasher()
#     bcrypt_hash = bcrypt_hasher.hash(password)
#     assert bcrypt_hash.startswith("$2")

#     # Membuat user dengan bcrypt secara langsung di database

#     user = User(email=email, hashed_password=bcrypt_hash)
#     sess.add(user)
#     sess.commit()
#     sess.refresh(user)

#     # Pastikan hasnya adalah bcrypt sebelum di authentikasi
#     assert user.hashed_password.startswith("$2")

#     #Autentikasi – ini seharusnya meningkatkan hash menjadi argon2.
#     authenticated_user = crud.authenticate(session=sess, email=email, password=password)
#     assert authenticated_user
#     assert authenticated_user.email == email

#     sess.refresh(authenticated_user)
#     # Pastikan hashnya sudah ditingkatkan ke argon2
#     assert authenticated_user.hashed_password.startswith("$argon2")

#     verified, update_hash = verify_password(plain_password=password, hashed_password=authenticated_user.hashed_password)
#     assert verified
#     assert update_hash is None
