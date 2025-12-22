from datetime import datetime, timezone
from typing import List

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from project.core.repositories.user import UserCoreRepository
from project.db.models import UserCoreModel, WalletRechargeInvoiceModel


class UserCoreService:
    def __init__(self, user_repo: UserCoreRepository):
        self.user_repo = user_repo

    async def create_wallet_invoice(
        self,
        upstream_user_obj: UserCoreModel,
        downstream_user_obj: UserCoreModel,
        charge_amount: int,
        get_config: bool,
        descriptions: str,
    ) -> WalletRechargeInvoiceModel:
        return await self.user_repo.create({
            "buyer_user":downstream_user_obj,
            "seller_user":upstream_user_obj,
            "charge_amount":charge_amount,
            "get_config":get_config,
            "descriptions":descriptions,
        })
