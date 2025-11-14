import enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------
class WalletInvoiceStatusChoices(enum.Enum):
    """
    حالت های وضعیت برای فاکتور‌های کیف پول
    """
    WAITING = "waiting" # در انتظار
    CONFIRMED = "confirmed" # تایید شده
    REJECTED = "rejected" # رد شده
    
    
    
    
    
    
    