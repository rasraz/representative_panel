from typing import List

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from project.db.models import UserCoreModel

from .base import BaseRepository



class UserCoreRepository(BaseRepository[UserCoreModel]):
    async def get_by_unique_id(self, unique_id: str) -> UserCoreModel | None:
        result = await self.session.execute(
            select(UserCoreModel).where(UserCoreModel.unique_id == unique_id)
        )
        return result.scalars().first()

    async def get_by_tel_chat_id(self, tel_chat_id: str) -> UserCoreModel | None:
        result = await self.session.execute(
            select(UserCoreModel).where(UserCoreModel.tel_chat_id == tel_chat_id)
        )
        return result.scalars().all()

    async def get_downstream_user_by_unique_id(self, unique_id: str) -> UserCoreModel:
        user_obj = await self.user_repo.session.query(UserCoreModel).filter(UserCoreModel.unique_id==unique_id).first()
        return user_obj

    async def search_by_name(self, query: str, skip: int = 0, limit: int = 20) -> List[UserCoreModel] | List:
        stmt = select(UserCoreModel).where(
            (UserCoreModel.first_name.ilike(f"%{query}%")) |
            (UserCoreModel.last_name.ilike(f"%{query}%"))
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def set_repres(self, user_obj: UserCoreModel) -> UserCoreModel:
        user_obj.is_repres = True
        await self.session.commit()
        await self.session.refresh(user_obj)
        return user_obj

    async def wallet_balance_sufficient(self, unique_id: str, amount: int):
        user_obj : UserCoreModel = await self.get_by_unique_id(self, unique_id=unique_id)
        if not user_obj:
            return None
        wallet_balance = user_obj.wallet_balance
        if wallet_balance < amount:
            return False
        return True
    








