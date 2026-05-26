
from sqlalchemy.ext.asyncio import  create_async_engine

from app.core.config import settings
# URL database, bisa dari environment variable
DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

# Buat async engine
engine = create_async_engine(DATABASE_URL)


       