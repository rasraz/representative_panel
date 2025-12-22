from typing import List, Any

from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy import select

from project.db.models import WalletInvoiceStatusChoices, WalletRechargeInvoiceModel, UserCoreModel

from .base import BaseRepository



class WalletInvoiceRepository(BaseRepository[WalletRechargeInvoiceModel]):
    async def all_invoices_seller_user(
            self, 
            upstream_user_obj: UserCoreModel,
            limit: int = 100, 
            skip: int = 0, 
            order_by: Any = None
            ) -> List[WalletRechargeInvoiceModel]:
        wi_objs = upstream_user_obj.seller_wallet_invoice
        if order_by:
            wi_objs = wi_objs.order_by(order_by.desc())
        return wi_objs.offset(skip).limit(limit).all()

    async def all_invoices_buyer_user(
            self,
            upstream_user_obj: UserCoreModel, 
            user_obj: UserCoreModel,
            limit: int = 100, 
            skip: int = 0, 
            order_by: Any = None
            ) -> List[WalletRechargeInvoiceModel]:
            
            filters = {
                "buyer_user_id": user_obj.id,
                "seller_user_id": upstream_user_obj.id
            }
            wi_objs = await self.get_multi(
                skip=skip,
                limit=limit,
                order_by=order_by,
                filters=filters
            )
            return wi_objs
    
    async def get_dwonstrem_user_wallet_invoice_by_id(
            self,
            wi_id: int, 
            upstream_user_obj: UserCoreModel
        ):
        wi_result = await self.session.execute(select(WalletInvoiceStatusChoices).where(
             WalletRechargeInvoiceModel.id==wi_id,
             WalletRechargeInvoiceModel.seller_user_id==upstream_user_obj.id 
        ))
        wi_obj = wi_result.scalars().first()
        if not wi_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="wallet invoice not found among your sub-users' receipts"
                )
        return wi_obj

    async def set_status(self, wi_obj: WalletRechargeInvoiceModel, status: WalletInvoiceStatusChoices) -> WalletRechargeInvoiceModel:
        wi_obj.status = status.value
        await self.session.commit()
        await self.session.refresh(wi_obj)
        return wi_obj

    async def adding_charge_to_wallet(self, wi_obj: WalletRechargeInvoiceModel) -> WalletRechargeInvoiceModel:
        try:
            buyer_user_obj = wi_obj.buyer_user.first()
            buyer_user_obj.wallet_balance = wi_obj.charge_amount
            wi_obj.status = WalletInvoiceStatusChoices.PAY_WALLET.value
            await self.session.commit()
            await self.session.refresh(wi_obj)
            return wi_obj
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to adding charge to wallet.") from e

