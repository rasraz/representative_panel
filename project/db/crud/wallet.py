from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from project.db.models import (
    UserCoreModel, 
    UserFinanceModel, 
    WalletInvoiceStatusChoices, 
    WalletRechargeInvoiceModel, 
    ConfigurationInvoiceModel,
)
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from project.core.app_wallet.schema import WalletInvoiceCreateSchemas
from project.db.models import UserCoreModel, WalletRechargeInvoiceModel

from .user import wallet_balance_sufficient


# ---------------------------------------
def get_direct_config(db: Session, current_user: UserCoreModel, wallet_invoice: WalletRechargeInvoiceModel):
    try:
        if current_user.auth.is_repres:
            price = current_user.finance.base_purchase_price
        else:
            price = current_user.upstream.finance.base_selling_price
        volume = int(wallet_invoice.charge_amount)//int(price)
        with db.begin():
            db_config_invoice = ConfigurationInvoiceModel(
               buyer_user=current_user,
               seller_user=current_user.upstream,
               volume=volume,
               base_price=price,
               total_price=price,
               descriptions=wallet_invoice.descriptions,
            )
            wallet_invoice.status = WalletInvoiceStatusChoices.CONFIGURATION_DIRECTE.value
            db.add(db_config_invoice)
            db.add(wallet_invoice)
            db.commit()
        db.refresh(wallet_invoice)
        return wallet_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create configuration invoice.") from e

# ---------------------------------------
def adding_charge_to_wallet(db: Session, current_user: UserCoreModel, wallet_invoice: WalletRechargeInvoiceModel) -> WalletRechargeInvoiceModel:
    try:
        user_obj = wallet_invoice.buyer_user
        db_user_finance = db.query(UserFinanceModel).filter(UserFinanceModel.user_core==user_obj).first()
        db_user_finance.wallet_balance = wallet_invoice.charge_amount
        wallet_invoice.status = WalletInvoiceStatusChoices.PAY_WALLET.value
        db.add(wallet_invoice)
        db.commit()
        db.refresh(wallet_invoice)
        return wallet_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to adding charge to wallet.") from e

# ---------------------------------------
def accept_wallet_invoice(db: Session, wallet_invoice_id: int, current_user: UserCoreModel, accepted: bool=True):
    db_wallet_invoice = db.query(WalletRechargeInvoiceModel).filter(
        WalletRechargeInvoiceModel.id == wallet_invoice_id,
        WalletRechargeInvoiceModel.seller_user == current_user
        ).first()
    if not db_wallet_invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="wallet invoice not found among your sub-users' receipts")
    wallet_charge_amount_invoice = int(db_wallet_invoice.charge_amount)
    if not wallet_balance_sufficient(current_user, wallet_charge_amount_invoice):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You do not have permission to approve this receipt due to insufficient funds in your wallet.")
    if accepted:
        invoice_status = WalletInvoiceStatusChoices.CONFIRMED.value
        if db_wallet_invoice.get_config:
            wallet_invoice_obj = get_direct_config(db, current_user, db_wallet_invoice)
        else:
            wallet_invoice_obj = adding_charge_to_wallet(db, current_user, db_wallet_invoice)
    else:
        invoice_status = WalletInvoiceStatusChoices.REJECTED.value
    wallet_invoice_obj.status = invoice_status
    db.commit()
    db.refresh(wallet_invoice_obj)
    return wallet_invoice_obj

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
                get_config=data.get_config,
                descriptions=data.descriptions,
            )
            db.add(db_wallet_invoice)
            db.commit()
        db.refresh(db_wallet_invoice)
        return db_wallet_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create wallet invoice.") from e









