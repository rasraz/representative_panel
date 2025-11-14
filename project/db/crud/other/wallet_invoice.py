from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from project.core.schemas.other import WalletInvoiceCreateSchemas
from project.db.models import UserCoreModel, WalletRechargeInvoiceModel


# --------------------------------------------------
def create_wallet_invoice(
    db: Session, 
    data: WalletInvoiceCreateSchemas, 
    current_user: UserCoreModel
    ) -> WalletRechargeInvoiceModel:
    """برای ثبت رسید شارژ کیف پول کاربر"""
    try:
        with db.begin():
            db_wallet_invoice = WalletRechargeInvoiceModel(
               buyer_user=current_user,
               seller_user=current_user.upstream,
               charge_amount=data.charge_amount,
               descriptions=data.descriptions,
            )
            db.add(db_wallet_invoice)
            db.commit()
        db.refresh(db_wallet_invoice)
        return db_wallet_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create wallet invoice.") from e





