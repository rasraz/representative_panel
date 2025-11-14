from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
class UserReadSchema(BaseModel):
    phone_number: str = Field(..., max_length=11, min_length=11)
    first_name: str = Field(..., max_length=16)
    last_name: str = Field(..., max_length=16)
    
# ---------------------------------------------------------------------
class UserActiveRepresentationSchema(BaseModel):
    base_purchase_price: str = Field(max_length=16)
    tel_bot_token: str = Field(max_length=128)








