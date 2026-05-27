from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


class DuplicateEntryError(Exception):
    """Raised when a duplicate entry is detected in the database."""
    def __init__(self, message="Duplicate entry detected"):
        super().__init__(message)


async def commit_with_integrity(session: AsyncSession):
    """
    Commit session dengan rollback otomatis jika terjadi IntegrityError.
    Raise DuplicateEntryError jika duplikat.
    """
    try:
        await session.commit()
        return True
    except IntegrityError as e:
        await session.rollback()
        if not 'prod' in settings.ENV:
            raise DuplicateEntryError(e) from e
        raise DuplicateEntryError("Data Duplikat Data") from e


