from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------
class ConfigInvoiceCreateSchemas(BaseModel):
    volume: str = Field(..., max_length=16)
    descriptions: Optional[str] = Field(default=None)

    model_config = ConfigDict(use_enum_values=True)





