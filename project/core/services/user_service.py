from typing import List

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from project.core.repositories.user import UserCoreRepository
from project.db.models import UserCoreModel
from project.core.auth import hash_unique_id



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

    async def get_downstream_user(self, upstream_user_obj: UserCoreModel, user_tel_chat_id: str) -> UserCoreModel | HTTPException:
        unique_id = hash_unique_id(upstream_id=upstream_user_obj.tel_chat_id, user_id=user_tel_chat_id)
        user_obj = await self.user_repo.get_downstream_user_by_unique_id(unique_id)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or access denied"
            )
        return user_obj

    async def all_downstream_users(self, upstream_user_obj: UserCoreModel, skip: int=0, limit: int=10) -> List[UserCoreModel] | List:
        downstream_users = await self.user_repo.get_multi(filters={"upstream_id": upstream_user_obj.id}, skip=skip, limit=limit)
        return downstream_users

    async def set_repres(self, upstream_user_obj: UserCoreModel, user_tel_chat_id: str):
        user_obj = await self.get_downstream_user(upstream_user_obj, user_tel_chat_id)
        user_obj = await self.user_repo.set_repres(user_obj)
        return True
    
    

