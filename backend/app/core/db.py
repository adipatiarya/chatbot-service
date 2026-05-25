from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.models.user import User, UserCreate
from app import crud

# URL database, bisa dari environment variable
DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

# Buat async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db(session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = result.scalars().first()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True
        )
        await crud.create_user(session=session, user_create=user_in)
    

        
       