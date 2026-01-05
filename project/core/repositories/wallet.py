from typing import List, Any

from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy import select

from project.db.models import WalletInvoiceStatusChoices, WalletRechargeInvoiceModel, UserCoreModel, ConfigurationInvoiceModel

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
    
    async def get_upstream_user_wallet_invoice_by_id(
            self,
            wi_id: int, 
            upstream_user_obj: UserCoreModel
        ) -> WalletRechargeInvoiceModel:
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

    async def get_direct_config(self, wallet_invoice: WalletRechargeInvoiceModel) -> WalletRechargeInvoiceModel:
        try:
            seller_user_obj = await wallet_invoice.awaitable_attrs.seller_user
            if not seller_user_obj.is_repres:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller must be representative.")
            
            price = seller_user_obj.representative_core.base_selling_price
            volume = wallet_invoice.charge_amount // price
            
            async with self.session.begin():
                config_invoice = ConfigurationInvoiceModel(
                    buyer_user=wallet_invoice.buyer_user,
                    seller_user=seller_user_obj,
                    volume=volume,
                    base_price=price,
                    total_price=price * volume,
                    descriptions=wallet_invoice.descriptions,
                )
                wallet_invoice.status = WalletInvoiceStatusChoices.CONFIGURATION_DIRECTE.value
                await self.session.add(config_invoice)
            
            await self.session.refresh(wallet_invoice)
            return wallet_invoice
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create configuration invoice") from e

    async def adding_charge_to_wallet(self, wi_obj: WalletRechargeInvoiceModel) -> WalletRechargeInvoiceModel:
        try:
            buyer_user_obj = await wi_obj.awaitable_attrs.buyer_user
            buyer_user_obj.wallet_balance += wi_obj.charge_amount
            wi_obj.status = WalletInvoiceStatusChoices.PAY_WALLET.value
            async with self.session.begin():
                pass
            await self.session.refresh(wi_obj)
            return wi_obj
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add charge to wallet.") from e

    async def wallet_balance_sufficient(self, upstream_user_obj: UserCoreModel, amount: int):
        if not upstream_user_obj:
            return None
        wallet_balance = upstream_user_obj.wallet_balance
        if wallet_balance < amount:
            return False
        return True
