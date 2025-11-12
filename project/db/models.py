from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum



class Base(DeclarativeBase):pass

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserCoreModel(BaseModel):
    """
    مدل هسته کاربری
    این مدل هسته کاربری برای مدیریت و نگهداری داده های کاربر است
    """
    __tablename__ = 'user_core'
    upstream_id = Column(Integer, ForeignKey("user_core.id")) # بالادستی
    phone_number = Column(String(11)) # شماره تلفن
    first_name = Column(String(32)) # نام
    last_name = Column(String(32)) # نام خانوادگی
    # -------------------------------------------------------------
    auth = relationship( # احرازهویت کاربر
        "UserAuthModel", 
        backref="user_auth",
        uselist=False,
        cascade="all, delete-orphan", 
        single_parent=True
    )
    finance = relationship( # حسابرسی کاربر
        "UserFinanceModel", 
        backref="user_finance",
        uselist=False,
        cascade="all, delete-orphan", 
        single_parent=True
    )
    telegram = relationship( # تلگرام کاربر
        "UserTelegramModel", 
        backref="user_telegram",
        uselist=False,
        cascade="all, delete-orphan", 
        single_parent=True
    )
    upstream = relationship( # بالادستی کاربر
        "UserCoreModel", 
        remote_side=[BaseModel.id], 
        back_populates="downstream"
    )
    downstream = relationship( # پایین‌دستی کاربر
        "UserCoreModel", 
        back_populates="upstream"
    )
    buyer_invoice = relationship( # فاکتور های خرید کاربر
        "PurchaseInvoiceModel", 
        foreign_keys="PurchaseInvoiceModel.buyer_user_id", 
        back_populates="buyer_user"
    )
    seller_invoice = relationship( # فاکتور های فروش کاربر
        "PurchaseInvoiceModel", 
        foreign_keys="PurchaseInvoiceModel.seller_user_id", 
        back_populates="seller_user"
    )
    seller_discounts = relationship( # تخفیف های فروش کاربر
        "DiscountModel", 
        foreign_keys="DiscountModel.seller_user_id", 
        back_populates="seller_user"
    )
    user_discounts = relationship( # تخفیف های خرید کاربر
        "UsersDiscountModel", 
        foreign_keys="UsersDiscountModel.user_id", 
        back_populates="user"
    )


class UserAuthModel(BaseModel):
    """
    مدل احرازهویت کاربری
    این مدل برای نگهداری داده های احرازهویت کاربر است
    """
    __tablename__ = 'user_auth'
    user_core = Column( # هسته کاربری
        Integer, 
        ForeignKey(
            'user_core.id', 
            ondelete="CASCADE"
        ), 
        unique=True, 
        index=True
    )
    password = Column(String(128)) # رمز عبور
    password_changed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    ) # زمان آخرین تغییر رمزعبور
    two_step_verification = Column(Boolean, default=False) # چک کردن امنیت 2 مرحله
    otp_code = Column(String(5), nullable=True) # کد otp 
    otp_exp = Column(DateTime(timezone=True)) # تاریخ انقضای کد otp
    is_active = Column(Boolean, default=True) # حساب کاربر فعال است
    is_admin = Column(Boolean, default=False) # حساب کاربر ادمین است
    is_repres = Column(Boolean, default=False) # حساب کاربر نماینده است


class UserFinanceModel(BaseModel):
    """
    مدل امورمالی کاربری
    این مدل برای نگهداری داده های حسابرسی کاربر است
    """
    __tablename__ = 'user_finance'
    user_core = Column( # هسته کاربری
        Integer, 
        ForeignKey(
            'user_core.id', 
            ondelete="CASCADE"
        ), 
        unique=True, 
        index=True
    )
    wallet_balance =Column(Integer) # موجودی کیف پول
    card_number = Column(String(16)) # شماره کارت
    total_volume = Column(String(16)) # حجم کل (بر حسب گیگابایت)
    sales_volume_ceiling = Column(Integer) # سقف حجم قابل فروش
    base_selling_price = Column(String(16)) # قیمت پایه فروش
    base_purchase_price = Column(String(16)) # قیمت پایه خرید


class UserTelegramModel(BaseModel):
    """
    مدل تلگرام کاربری
    این مدل برای نگهداری داده‌ها و اطلاعات تلگرام کاربر است
    """
    __tablename__ = 'user_telegram'
    user_core = Column( # هسته کاربری
        Integer, 
        ForeignKey(
            'user_core.id', 
            ondelete="CASCADE"
        ), 
        unique=True, 
        index=True
    )
    tel_chat_id = Column(String(128)) # شناسه چت تلگرام
    tel_bot_token = Column(String(128), nullable=True) # توکن بات تلگرام   
    tel_channel_id = Column(String(128), nullable=True) # شناسه کانال تلگرام
    tel_support_id = Column(String(128), nullable=True) # شناسه پشتیبان تلگرام


class InvoiceStatus_choices(enum.Enum):
    """
    حالت های وضعیت برای فاکتور‌ها
    """
    WAITING = "waiting" # در انتظار
    CONFIRMED = "confirmed" # تایید شده
    REJECTED = "rejected" # رد شده


class PurchaseInvoiceModel(BaseModel):
    """
    مدل فاکتورهای خرید
    این مدل برای ثبت تاریخچه خرید ها و تراکنش هایانجام شده هر کاربر است
    """
    __tablename__ = 'purchase_invoices'
    buyer_user_id = Column(Integer, ForeignKey('user_core.id')) # شناسه کاربر خریدار
    seller_user_id = Column(Integer, ForeignKey('user_core.id')) # شناسه کاربر فروشنده
    volume = Column(String(16)) # حجم
    create_dt = Column(DateTime(timezone=True), server_default=func.now()) # تاریخ ثبت
    expiration_dt = Column(DateTime(timezone=True)) # تاریخ انقضاي
    status = Column(
        Enum(InvoiceStatus_choices), 
        nullable=False, 
        default=InvoiceStatus_choices.WAITING,
        server_default=text("'waiting'")
    ) # وضعیت
    base_price = Column(String(16)) # قیمت پایه
    discount_amount = Column(String(16)) # مقدار تخفیف
    total_price = Column(String(16)) # قیمت کل
    descriptions = Column(String) # توضیحات
    config_output = Column(Boolean, default=False) # خروجی کانفیگ
    # --------------------------------------------------------------------
    buyer_user = relationship( # کاربر خریدار
        "UserCoreModel",
        foreign_keys=[buyer_user_id],
        back_populates="buyer_invoice"
    )
    seller_user = relationship( # کاربر فروشنده
        "UserCoreModel",
        foreign_keys=[seller_user_id],
        back_populates="seller_invoice"
    )


class DiscountModel(BaseModel):
    """
    مدل تخفیف ها
    این مدل برای تعریف تخفیف های پیشرفته برای کاربران فروشنده است
    """
    __tablename__ = 'discount'
    seller_user_id = Column(Integer, ForeignKey('user_core.id')) # شناسه کاربر فروشنده
    code = Column(String(16)) # کد تخفیف
    percent = Column(String(16)) # درصد تخفیف
    volume = Column(String(16)) # حجم
    expired_dt = Column(DateTime(timezone=True), server_default=func.now()) # تاریخ انقضائ
    usage_ceiling = Column(Integer) # محدودیت استفاده
    maximum_discount_amount = Column(String(16)) # حداکثر مبلغ
    minimum_purchase_amount = Column(String(16)) # حداقل مبلغ خرید
    number_uses_per_user = Column(String(16)) # محدودیت استفاده برای هر کاربر
    refund = Column(Boolean, default=False) # بازگشت وجه
    synchronicity = Column(Boolean, default=False) # همزمانی
    # -------------------------------------------------------------------------
    seller_user = relationship( # کاربر فروشنده
        "UserCoreModel",
        foreign_keys=[seller_user_id],
        back_populates="seller_discounts"
    )
    user_discounts = relationship( # تخفیف های خرید کاربر
        "UsersDiscountModel", 
        foreign_keys="UsersDiscountModel.discount_id", 
        back_populates="discount",
        cascade="all, delete-orphan"
    )


class UserDiscountType_choices(enum.Enum):
    """
    نوع کاربر برای تخفیف
    """
    USED_BY_USERS = "used_by_users" # کاربران استفاده کرده
    AUTHORIZED_USERS_FOR_USE = "authorized_users_for_use" # کاربران مجاز به استفاده

class UsersDiscountModel(BaseModel):
    """
    مدل کاربران تخفیف ها
    این مدل بر اساس نوع انتخاب شده تعریف میکند که چه کاربرانی چند بار شامل تخفیف هستند و
    چه کاربرانی چند بار تا الان از آن استفاده کرده اند
    """
    __tablename__ = 'user_discount'
    user_id = Column(Integer, ForeignKey('user_core.id')) # شناسه کاربر
    discount_id = Column(Integer, ForeignKey('discount.id')) # شناسه تخفیف
    count_uses = Column(Integer) # تعداد استفاده
    user_type = Column(Enum(UserDiscountType_choices), nullable=False) # نوع کاربر
    # --------------------------------------------------------------------------
    user = relationship( # کاربر
        "UserCoreModel",
        foreign_keys=[user_id],
        back_populates="user_discounts",
        cascade="all, delete-orphan"
    )
    discount = relationship( # تخفیف
        "DiscountModel",
        foreign_keys=[discount_id],
        back_populates="user_discounts",
        cascade="all, delete-orphan"
    )

