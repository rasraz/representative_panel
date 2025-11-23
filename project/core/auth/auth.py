from datetime import datetime, timedelta, timezone 
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from project.core.main.config import settings
 

SECRET_KEY = settings.SECRET_KEY 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        token_pwd_ts = payload.get("pwd_ts")
        if not user_id_str or token_pwd_ts is None:
            raise ValueError("Invalid token")
        
        return int(user_id_str), token_pwd_ts
    except Exception as e:
        print("Error:::", e)
        return None, None

def generate_hash_password_by_phone_number(phone_number: str):
    raw = f"password:{phone_number}/84921jflp=263"
    return pwd_context.hash(raw)
