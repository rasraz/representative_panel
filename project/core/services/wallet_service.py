from fastapi import status
from fastapi.exceptions import HTTPException

from project.core.repositories.wallet import WalletInvoiceRepository
from project.db.models import UserCoreModel, WalletRechargeInvoiceModel, WalletInvoiceStatusChoices


class WalletInvoiceService:
    def __init__(self, wi_repo: WalletInvoiceRepository):
        self.wi_repo = wi_repo

    async def create_wallet_invoice(
        self,
        upstream_user_obj: UserCoreModel,
        downstream_user_obj: UserCoreModel,
        charge_amount: int,
        get_config: bool,
        descriptions: str,
    ) -> WalletRechargeInvoiceModel:
        return await self.wi_repo.create({ 
            "buyer_user":downstream_user_obj,
            "seller_user":upstream_user_obj,
            "charge_amount":charge_amount,
            "get_config":get_config,
            "descriptions":descriptions,
        })

    async def accept_wallet_invoice(self, wallet_invoice_id: int, upstream_user_obj: UserCoreModel, accepted: bool=True):
        wallet_invoice_obj = await self.wi_repo.get_upstream_user_wallet_invoice_by_id(wi_id=wallet_invoice_id, upstream_user_obj=upstream_user_obj)
        if not wallet_invoice_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="wallet invoice not found among your sub-users' receipts")
        wallet_charge_amount_invoice = wallet_invoice_obj.charge_amount
        if not await self.wi_repo.wallet_balance_sufficient(upstream_user_obj, wallet_charge_amount_invoice):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You do not have permission to approve this receipt due to insufficient funds in your wallet.")
        if accepted:
            invoice_status = WalletInvoiceStatusChoices.CONFIRMED
            if wallet_invoice_obj.get_config:
                wallet_invoice_obj = await self.wi_repo.get_direct_config(wallet_invoice=wallet_invoice_obj)
            else:
                wallet_invoice_obj = self.wi_repo.adding_charge_to_wallet(wi_obj=wallet_invoice_obj)
        else:
            invoice_status = WalletInvoiceStatusChoices.REJECTED.value
            wallet_invoice_obj.status = invoice_status
            await self.wi_repo.session.add(wallet_invoice_obj)
            await self.wi_repo.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="There is a problem with the data sent and the receipt status has changed to rejected."
                )
        return wallet_invoice_obj