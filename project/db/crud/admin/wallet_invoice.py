from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from project.db.models import UserCoreModel, WalletRechargeInvoiceModel


# ---------------------------------------
def accept_wallet_invoice(db: Session, wallet_invoice_id: int, current_user: UserCoreModel):
    ...




