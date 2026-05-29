from datetime import datetime
import uuid

from sqlalchemy import desc, or_
from sqlalchemy.orm import selectinload
from sqlmodel import asc, select

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from .crud import Crud

class UserCrud(Crud[User]):
    def __init__(self, session):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.roles)).where(User.email == email)
        )
        return result.scalars().first()
    
    async def roles(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id))
        user = result.scalar_one()
        return user

    async def filtered(
        self,
        page: int = 1,
        limit: int = 10,
        filters: dict[str, str] | None = None,
        search: str | None = None,
        order_by: str = "created_at",
        order_dir: str = "asc",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        search_fields: list[str] | None = None,   # <--- tambahan parameter
    ) -> list[User]:
        
        query = select(User)

        # filter field biasa
        if filters:
            for field, value in filters.items():
                column = getattr(User, field, None)
                if column is not None and value:
                    query = query.where(column.ilike(f"%{value}%"))

            # filter relasi Permission via Role
            if "permission" in filters:
                query = (
                    query.join(User.roles)
                        .join(Role.permissions)
                        .where(Permission.name.ilike(f"%{filters['permission']}%"))
                )

        # search multi-field dinamis
        if search:
            # default fields kalau tidak diberikan
            if not search_fields:
                search_fields = ["email", "full_name"]

            conditions = []
            for field in search_fields:
                column = getattr(User, field, None)
                if column is not None:
                    conditions.append(column.ilike(f"%{search}%"))

            # tambahkan Permission.name
            conditions.append(Permission.name.ilike(f"%{search}%"))

            query = (
                query.outerjoin(User.roles)
                    .outerjoin(Role.permissions)
                    .where(or_(*conditions))
            )

        # range filter
        if start_date:
            query = query.where(User.created_at >= start_date)
        if end_date:
            query = query.where(User.created_at <= end_date)

        # sorting
        column = getattr(User, order_by, None)
        if column is not None:
            query = query.order_by(desc(column) if order_dir.lower() == "desc" else asc(column))

        # eager load roles + permissions
        query = query.options(selectinload(User.roles).selectinload(Role.permissions))

        # pagination
        result = await self.session.execute(
            query.offset((page - 1) * limit).limit(limit)
        )
        return result.scalars().all()
