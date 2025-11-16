from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from project.core.schemas.other.config_invoice import ConfigInvoiceCreateSchemas
from project.db.models import UserCoreModel, ConfigurationInvoiceModel


# --------------------------------------------------
def create_config_invoice(
    db: Session, 
    data: ConfigInvoiceCreateSchemas, 
    current_user: UserCoreModel
    ) -> ConfigurationInvoiceModel:
    """برای ثبت رسید دریافت کانفیگ کاربر"""
    if current_user.auth.is_repres:
        price = current_user.finance.base_purchase_price
    else:
        price = current_user.upstream.finance.base_selling_price
    if current_user.finance.wallet_balance < price:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wallet balance is insufficient"
        )
    try:
        with db.begin():
            db_config_invoice = ConfigurationInvoiceModel(
               buyer_user=current_user,
               seller_user=current_user.upstream,
               volume=data.volume,
               base_price=price,
               total_price=price,
               descriptions=data.descriptions,
            )
            db.add(db_config_invoice)
            db.commit()
        db.refresh(db_config_invoice)
        return db_config_invoice
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create configuration invoice.") from e








