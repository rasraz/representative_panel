# repositories/base.py
from typing import Generic, TypeVar, Sequence, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    # ────── CREATE ──────
    async def create(self, data: dict) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    # ────── READ ──────
    async def get_by_id(self, id: Any) -> T | None:
        return await self.session.get(self.model, id)

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
        filters: dict | None = None
    ) -> Sequence[T]:
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        if order_by:
            stmt = stmt.order_by(order_by.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ────── UPDATE ──────
    async def update(self, db_obj: T, data: dict) -> T:
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    # ────── DELETE ──────
    async def delete(self, db_obj: T) -> None:
        await self.session.delete(db_obj)
        await self.session.commit()

    # متد کمکی برای وجود داشتن
    async def exists(self, **filters) -> bool:
        stmt = select(self.model).filter_by(**filters).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None





