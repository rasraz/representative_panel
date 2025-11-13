from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import Session

from project.db.database import get_session
from project.db.models import UserCoreModel

from .auth import decode_access_token


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)) -> UserCoreModel:
    token = credentials.credentials
    user_id, token_pwd_ts = decode_access_token(token)
    if (user_id is None) or (token_pwd_ts is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توکن نامعتبر")

    user = session.get(UserCoreModel, user_id)
    if not (user and user.is_active):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="کاربر فعال نیست")

    current_pwd_ts = user.password_changed_at.timestamp()
    if token_pwd_ts < current_pwd_ts:
        raise HTTPException(401, "این توکن دیگر معتبر نیست")

    return user


def get_current_admin(user: UserCoreModel = Depends(get_current_user)) -> UserCoreModel:
    if not (user.is_admin and user.online_status):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="فقط ادمین این دسترسی را دارد")
    
    return user


