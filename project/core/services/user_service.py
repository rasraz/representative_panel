from datetime import datetime, timezone
from typing import List

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from project.core.repositories.user import UserCoreRepository
from project.db.models import UserCoreModel
from project.core.auth import hash_unique_id
from project.core.auth.auth import hash_password


class UserCoreService:
    def __init__(self, user_repo: UserCoreRepository):
        self.user_repo = user_repo

    async def register(self, upstream_user: UserCoreModel, tel_chat_id: str, 
                       tel_user_id: str|None, first_name: str, last_name: str):
        unique_id = hash_unique_id(upstream_id=upstream_user.tel_chat_id, user_id=tel_chat_id)
        return await self.user_repo.create({
            "upstream": upstream_user,
            "tel_chat_id": tel_chat_id,
            "unique_id": unique_id,
            "tel_user_id": tel_user_id,
            "first_name": first_name,
            "last_name": last_name
        })

    async def update_fullname(self, upstream_user_obj: UserCoreModel, first_name: str, last_name: str) -> UserCoreModel:
        upstream_user_obj.first_name = first_name
        upstream_user_obj.last_name = last_name
        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(upstream_user_obj)
        return upstream_user_obj

    async def wallet_balance_sufficient(self, unique_id: str, amount: int):
        user_obj: UserCoreModel = await self.user_repo.get_by_unique_id(self, unique_id=unique_id)
        if not user_obj:
            return None
        wallet_balance = user_obj.wallet_balance
        if wallet_balance < amount:
            return False
        return True

class RepresentativesCoreService(UserCoreService):
    def __init__(self, user_repo: UserCoreRepository):
        super().__init__(user_repo)

    async def get_downstream_user(self, upstream_user_obj: UserCoreModel, user_tel_chat_id: str) -> UserCoreModel:
        unique_id = hash_unique_id(upstream_id=upstream_user_obj.tel_chat_id, user_id=user_tel_chat_id)
        user_obj = await self.user_repo.get_user_by_unique_id(unique_id)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or access denied"
            )
        return user_obj

    async def all_downstream_users(self, upstream_user_obj: UserCoreModel, skip: int=0, limit: int=10) -> List[UserCoreModel]:
        downstream_users = await self.user_repo.get_multi(filters={"upstream_id": upstream_user_obj.id}, skip=skip, limit=limit)
        return downstream_users

    async def set_repres(self, upstream_user_obj: UserCoreModel, user_tel_chat_id: str):
        user_obj = await self.get_downstream_user(upstream_user_obj, user_tel_chat_id)
        user_obj = await self.user_repo.set_repres(user_obj)
        return user_obj

    async def update_password(self, upstream_user_obj: UserCoreModel, new_password: str) -> UserCoreModel:
        upstream_user_obj.representative_core.password = hash_password(new_password)
        upstream_user_obj.representative_core.password_changed_at = datetime.now(timezone.utc)
        await self.user_repo.session.commit()
        return upstream_user_obj


class AdminCoreService(RepresentativesCoreService):
    def __init__(self, user_repo: UserCoreRepository):
        super().__init__(user_repo)

    async def get_user(self, upstream_user_obj: UserCoreModel, unique_id: str) -> UserCoreModel:
        user_obj = await self.user_repo.get_user_by_unique_id(unique_id)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or access denied"
            )
        return user_obj

    async def all_downstream_users_repres(self, upstream_user_obj: UserCoreModel, unique_id: str, skip: int=0, limit: int=10) -> List[UserCoreModel]:
        repres_user_obj = self.get_user(upstream_user_obj, unique_id)
        downstream_users = await self.user_repo.get_multi(filters={"upstream_id": repres_user_obj.id}, skip=skip, limit=limit)
        return downstream_users

    async def deactive_downstream_user(self, upstream_user_obj: UserCoreModel, unique_id: str) -> UserCoreModel:
        user_obj = await self.user_repo.get_user_by_unique_id(unique_id)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or access denied"
            )
        user_obj.is_active = False
        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(user_obj)
        return user_obj

    async def delete_downstream_user(self, upstream_user_obj: UserCoreModel, unique_id: str) -> bool:
        user_obj = await self.user_repo.get_user_by_unique_id(unique_id)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or access denied"
            )
        await self.user_repo.session.delete(user_obj)
        await self.user_repo.session.commit()
        return True






