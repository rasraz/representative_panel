from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from project.core.schemas.other.user import UserCreateSchema, UserUpdatePasswordSchema, UserUpdateInfoSchema
from project.db.models import UserCoreModel, UserAuthModel, UserTelegramModel
from project.core.auth.auth import hash_password, generate_hash_password_by_phone_number


# ----------------------------------------------------------------------------------------------------------------
def create_user(db: Session, data: UserCreateSchema, current_user: UserCoreModel | None = None) -> UserCoreModel:
    """برای ثبت نام اولیه یک کاربر جدید"""
    hashed_password = generate_hash_password_by_phone_number(data.phone_number)
    try:
        with db.begin():
            db_core_user = UserCoreModel(upstream=current_user, **data.model_dump()) 
            db_auth_user = UserAuthModel(user_core=db_core_user, password=hashed_password, password_changed_at=datetime.now(timezone.utc))
            db_tel_user = UserTelegramModel(user_core=db_core_user, tel_chat_id=data.tel_chat_id)
            db.add(db_core_user, db_auth_user, db_tel_user)
            db.commit()
        db.refresh(db_core_user)
        return db_core_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this phone number already exists.") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user.") from e

# ----------------------------------------------------------------------------------------------------------------
def update_password_selfuser(db: Session, current_user: UserCoreModel, data: UserUpdatePasswordSchema) -> UserCoreModel:
    """برای به روزرسانی رمز عبور کاربر زیرمجموعه خاص"""
    current_user.auth.password = hash_password(data.password)
    current_user.auth.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    return current_user

# ----------------------------------------------------------------------------------------------------------------
def update_fullname_selfuser(db: Session, current_user: UserCoreModel, data: UserUpdateInfoSchema) -> UserCoreModel:
    """برای به روزرسانی نام یا نام خانوادگی خود کاربر"""
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    db.commit()
    return current_user

