
from sqlalchemy.ext.asyncio import  create_async_engine
from app.services.user_service import UserService 

from app.core.config import settings
from app.models.user import UserCreate

# URL database, bisa dari environment variable
DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

# Buat async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db(service: UserService, role:str) -> None:
   
    user = await service.user_crud.get_by_email(settings.FIRST_SUPERUSER)

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            role=role
        )
        await service.create_user(user_in)
    

        
       