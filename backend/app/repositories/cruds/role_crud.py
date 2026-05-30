
from datetime import datetime
import uuid

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.models.role import Role, RolePublic
from app.api.dtos.generic import Paginated
from app.models.user import User
from .crud import Crud

class RoleCrud(Crud[Role]):
    def __init__(self, session):
        super().__init__(session, Role)

    async def get_by_name_or_id(self, role: uuid.UUID | str) -> Role | None:
        stmt = select(Role).options(selectinload(Role.permissions)).where(
            Role.id == role if isinstance(role, uuid.UUID) else Role.name == role
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except:
            return None
    def transform(self, role: Role) -> RolePublic:

        return RolePublic(
            id=role.id,
            name=role.name,
            created_at=role.created_at,
            users = [p.email for p in role.users],
            permissions=[p.name for p in role.permissions],
            total_user=len(role.users),
            total_permission=len(role.permissions)
        )
    
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
        search_fields: list[str] | None = None,
    ) -> Paginated[RolePublic]:
        
        query = select(Role)

        # filter field biasa
        if filters:
            for field, value in filters.items():
                column = getattr(Role, field, None)
                if column is not None and value:
                    query = query.where(column.ilike(f"%{value}%"))

            if "email" in filters:
                query = (
                    query.join(Role.users)
                        .where(User.name.ilike(f"%{filters['email']}%"))
                )

        # search multi-field dinamis
        if search:
            if not search_fields:
                search_fields = ["name", "description"]

            conditions = []
            for field in search_fields:
                column = getattr(Role, field, None)
                if column is not None:
                    conditions.append(column.ilike(f"%{search}%"))

            conditions.append(User.email.ilike(f"%{search}%"))

            query = (
                query.outerjoin(Role.permissions)
                    .where(or_(*conditions))
            )

        # range filter
        if start_date:
            query = query.where(Role.created_at >= start_date)
        if end_date:
            query = query.where(Role.created_at <= end_date)

        # sorting
        column = getattr(Role, order_by, None)
        if column is not None:
            query = query.order_by(desc(column) if order_dir.lower() == "desc" else asc(column))

        # eager load
        query = query.options(selectinload(Role.users))
        query = query.options(selectinload(Role.permissions))

        # --- hitung total sesuai filter ---
        total_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar_one()

        # --- ambil data sesuai pagination ---
        result = await self.session.execute(
            query.offset((page - 1) * limit).limit(limit)
        )
        data = [ self.transform(x) for x in  result.scalars().all() ]

        # --- hitung total halaman ---
        total_pages = (total // limit) + (1 if total % limit else 0)
        return Paginated[RolePublic](
            data=data,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    