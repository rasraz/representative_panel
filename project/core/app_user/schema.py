from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------
class UserReadSchema(BaseModel):
    phone_number: str = Field(..., max_length=11, min_length=11)
    first_name: str = Field(..., max_length=16)
    last_name: str = Field(..., max_length=16)
    
# ---------------------------------------------------------------------
class UserActiveRepresentationSchema(BaseModel):
    base_purchase_price: str = Field(max_length=16)
    tel_bot_token: str = Field(max_length=128)

# ---------------------------------------------------------------------
class UserCreateSchema(BaseModel):
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
    
# ---------------------------------------------------------------------
class UserUpdateInfoSchema(BaseModel):
    first_name: str = Field(max_length=16)
    last_name: str = Field(max_length=16)
    
# ---------------------------------------------------------------------
class UserUpdatePasswordSchema(BaseModel):
    otp: str = Field(min_length=5, max_length=5)
    password: str = Field(min_length=8)
    password_conf: str = Field(min_length=8)

    @field_validator("otp_code")
    def _otp_code_validate(cls, v, info):
        if len(v) != 5:
            raise ValueError("otp code must be 5 character")
        return v

    @field_validator("password_conf")
    def _passwords_match(cls, v, info):
        # Checks whether the password and password confirmation match.
        password = info.data["password"]
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        if not(has_lower and has_upper):
            raise ValueError("The password must include uppercase and lowercase English letters")
        return v
    







