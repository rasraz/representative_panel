from typing import List
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from project.core.schemas.user_schemas import (
    UserCreateSchema, 
    UserUpdatePassword, 
    UserUpdateSchema, 
    UserActiveRepresentationSchema,
)
from project.db.models import UserCoreModel, UserAuthModel, UserTelegramModel, UserFinanceModel
from project.core.auth.auth import hash_password, generate_hash_password_by_phone_number



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
        raise HTTPException(status_code=400, detail="User with this phone number already exists.") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user.") from e


def get_user(db: Session, user_id: int, current_user: UserCoreModel) -> UserCoreModel:
    """برای دریافت یک کاربر از زیر مجموعه ها با شناسه خاص"""
    query = db.query(UserCoreModel).options(
        joinedload(UserCoreModel.auth),
        joinedload(UserCoreModel.telegram)
    ).filter(UserCoreModel.id==user_id)
    if not current_user.auth.is_admin:
        query = query.filter(UserCoreModel.upstream==current_user)
    user = query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or access denied"
        )
    return user


def get_all_users(db: Session, current_user: UserCoreModel, skip: int=0, limit: int=10) -> List[UserCoreModel]:
    """برای دریافت تمامی کاربران زیر مجموعه مستفیم"""
    query = db.query(UserCoreModel)
    if not current_user.auth.is_admin:
        query = query.filter(UserCoreModel.upstream==current_user)
    all_users = query.order_by(UserCoreModel.create_dt.desc()).offset(skip).limit(limit)
    return all_users


def update_password_subuser(db: Session, user_id: int, current_user: UserCoreModel, data: UserUpdatePassword) -> UserCoreModel:
    """برای به روزرسانی رمز عبور خود کاربر"""
    user = get_user(db, user_id, current_user)
    user.auth.password = hash_password(data.password)
    user.auth.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    return user


def update_password_selfuser(db: Session, current_user: UserCoreModel, data: UserUpdatePassword) -> UserCoreModel:
    """برای به روزرسانی رمز عبور کاربر زیرمجموعه خاص"""
    current_user.auth.password = hash_password(data.password)
    current_user.auth.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    return current_user


def update_fullname_subuser(db: Session, user_id: int, current_user: UserCoreModel, data: UserUpdateSchema) -> UserCoreModel:
    """برای به روزرسانی نام یا نام خانوادگی کاربر زیرمجموعه خاص"""
    user = get_user(db, user_id, current_user)
    user.first_name = data.first_name
    user.last_name = data.last_name
    db.commit()
    return user


def update_fullname_selfuser(db: Session, current_user: UserCoreModel, data: UserUpdateSchema) -> UserCoreModel:
    """برای به روزرسانی نام یا نام خانوادگی خود کاربر"""
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    db.commit()
    return current_user


def deactive_user(db: Session, user_id:int, current_user: UserCoreModel) -> UserCoreModel:
    """برای غیر فعال سازی حساب کاربر خاص"""
    user = get_user(db, user_id, current_user)
    user.auth.is_active = False
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id:int, current_user: UserCoreModel) -> UserCoreModel:
    """برای حذف یک کاربر خاص از زیر مجموعه‌های مستقیم"""
    user = get_user(db, user_id, current_user)
    user.delete()
    db.commit()
    return user


def activation_of_representation_user(
    db: Session, 
    user_id:int, 
    current_user: UserCoreModel, 
    data: UserActiveRepresentationSchema
) -> UserCoreModel:
    """برای ایجاد حالت نمایندگی برای یک کاربر خاص"""
    db_core_user = get_user(db, user_id, current_user)
    db_core_user.auth.is_repres = True
    db_core_user.telegram.tel_bot_token = data.tel_bot_token
    try:
        with db.begin():
            if data.base_purchase_price: price = data.base_purchase_price
            else: price = current_user.finance.base_selling_price
            db_finance_user = UserFinanceModel(
                user_core=db_core_user,
                base_purchase_price=price,
                base_selling_price=price,
                )
            db.add(db_finance_user)
            db.commit()
        db.refresh(db_core_user)
        return db_core_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to set representation user.") from e

