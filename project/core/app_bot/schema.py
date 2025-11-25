import enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

# ---------------------------------------------------------------------
class UserCreateSchema(BaseModel):
    phone_number: str = Field(max_length=11, min_length=11)
    first_name: str = Field(..., max_length=16)
    last_name: str = Field(..., max_length=16)
    tel_chat_id: str = Field(...)

    @field_validator("phone_number")
    def _phone_number_validate(cls, v, info):
        # Checks whether the phone number is validate.
        if len(v) != 11:
            raise ValueError("Phone number must be 11 character")
        if not v.startswith("09"):
            raise ValueError("Phone number must be started by 09")
        return v
    
# ---------------------------------------------------------------------
class UserCompletionSchema(BaseModel):
    phone_number: str = Field(..., max_length=11, min_length=11)
    first_name: str = Field(..., max_length=16)
    last_name: str = Field(..., max_length=16)
    tel_chat_id: str = Field(...)

    @field_validator("phone_number")
    def _phone_number_validate(cls, v, info):
        # Checks whether the phone number is validate.
        if len(v) != 11:
            raise ValueError("Phone number must be 11 character")
        if not v.startswith("09"):
            raise ValueError("Phone number must be started by 09")
        return v
    
# ---------------------------------------------------------------------
class UserReadSchema(BaseModel):
    phone_number: str = Field(..., max_length=11, min_length=11)
    first_name: str = Field(..., max_length=16)
    last_name: str = Field(..., max_length=16)
    
# ---------------------------------------------------
class WalletInvoiceCreateSchemas(BaseModel):
    charge_amount: str = Field(..., max_length=16)
    get_config: bool = Field(default=False)
    descriptions: Optional[str] = Field(default=None)

# ---------------------------------------------------
class WalletInvoiceReadSchemas(BaseModel):
    charge_amount: str = Field(..., max_length=16)
    get_config: bool = Field(default=False)
    descriptions: Optional[str] = Field(default=None)
    
# ---------------------------------------------------
class ConfigInvoiceCreateSchemas(BaseModel):
    volume: str = Field(..., max_length=16)
    created_at: datetime
    base_price: str = Field(..., max_length=16)
    total_price: str = Field(..., max_length=16)
    descriptions: Optional[str] = Field(default=None)
    
# ---------------------------------------------------
class WalletInvoiceStatusChoices(enum.Enum):
    """
    حالت های وضعیت برای فاکتور‌های کیف پول
    """
    WAITING = "waiting" # در انتظار
    CONFIRMED = "confirmed" # تایید شده
    REJECTED = "rejected" # رد شده
    PAY_WALLET = "pay_wallet" # پرداخت شده به کیف پول

class ConfigInvoiceReadSchemas(BaseModel):
    charge_amount: str = Field(..., max_length=16)
    get_config: bool
    created_at: datetime
    status: WalletInvoiceStatusChoices
    descriptions: Optional[str] = Field(default=None)

    model_config = ConfigDict(use_enum_values=True)
    
    
    