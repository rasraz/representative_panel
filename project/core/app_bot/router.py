from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from project.db.database import get_session
from project.db.models import UserCoreModel
from project.core.auth.dependencies import get_current_user
from project.db.crud.user import create_user, completion_repres_user
from project.db.crud.wallet import create_wallet_invoice, accept_wallet_invoice
from project.db.crud.config import create_config_invoice

from .schema import (
    UserCreateSchema,
    UserCompletionSchema,
    UserReadSchema,
    WalletInvoiceCreateSchemas,
    WalletInvoiceReadSchemas,
    ConfigInvoiceCreateSchemas,
    ConfigInvoiceReadSchemas,
)


router = APIRouter(prefix="/bot")
# TODO: فعلا برای شناسایی کاربر از user عادی استفاده میکنیم تا بعدا سیسیتم احراز هویت ربات درخواست ارسال کننده را پیدا کنیم.

# ---------------------------------------------------
@router.post("/user/creat", response_model=UserReadSchema)
def create_user_api(data: UserCreateSchema, db: Session=Depends(get_session), user: UserCoreModel=Depends(get_current_user)):
    user_created = create_user(data, db, user)
    return user_created

# ---------------------------------------------------
@router.post("/user/completion-repres", response_model=UserReadSchema)
def create_user_api(data: UserCompletionSchema, db: Session=Depends(get_session), user: UserCoreModel=Depends(get_current_user)):
    user_repres = completion_repres_user(data, db, user)
    return user_repres

# ---------------------------------------------------
@router.post("/wallet", response_model=WalletInvoiceReadSchemas)
def wallet_charge_api(data: WalletInvoiceCreateSchemas, db: Session=Depends(get_session), user: UserCoreModel=Depends(get_current_user)):
    wallet_invoice_obj = create_wallet_invoice(db, data, user)
    return wallet_invoice_obj

# ---------------------------------------------------
@router.get("/wallet/{invoice_id}/accept/{accepted}", response_model=WalletInvoiceReadSchemas)
def wallet_charge_accept_api(invoice_id: int, accepted: bool, db: Session=Depends(get_session), user: UserCoreModel=Depends(get_current_user)):
    wallet_invoice_obj = accept_wallet_invoice(db, invoice_id, user, accepted)
    return wallet_invoice_obj

# ---------------------------------------------------
@router.post("/config", response_model=ConfigInvoiceReadSchemas)
def create_config_api(data: ConfigInvoiceCreateSchemas, db: Session=Depends(get_session), user: UserCoreModel=Depends(get_current_user)):
    config_invoice_obj = create_config_invoice(db, data, user)
    return config_invoice_obj








