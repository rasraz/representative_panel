from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Boolean, DateTime, Enum, ForeignKey, text, CheckConstraint
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum



class Base(DeclarativeBase):pass

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserCoreModel(BaseModel):
    __tablename__ = 'user_core'
    upstream_id = Column(Integer, ForeignKey("user_core.id")) # بالادستی
    first_name = Column(String(32)) # نام
    last_name = Column(String(32)) # نام خانوادگی
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # زمان ثبت نام
    tel_user_id = Column(String(128), nullable=True) # شناسه کاربری تلگرام
    tel_chat_id = Column(String(128)) # شناسه چت تلگرام
    unique_id = Column(String(128), unique=True, index=True) #شناسه یکتا
    is_active = Column(Boolean, default=True) # حساب کاربر فعال است
    is_admin = Column(Boolean, default=False) # حساب کاربر ادمین است
    is_repres = Column(Boolean, default=False) # حساب کاربر نماینده است
    wallet_balance =Column(BigInteger, default=0, nullable=False) # موجودی کیف پول
    __table_args__ = (
        CheckConstraint('wallet_balance >= 0', name='ck_user_wallet_non_negative'),
    )
    # -------------------------------------------------------------
    representative_core = relationship( # هسته نماینده
        "RepresentativesCoreModel", 
        backref="representatives_core",
        uselist=False,
        cascade="all, delete-orphan", 
        single_parent=True
    )
    configuration_panel = relationship( # پنل کانفیگ
        "ConfigurationPanelModel", 
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan", 
        single_parent=True,
        lazy="dynamic"
    )
    upstream = relationship( # بالادستی کاربر
        "UserCoreModel", 
        remote_side=[BaseModel.id], 
        back_populates="downstream",
        lazy="dynamic"
    )
    downstream = relationship( # پایین‌دستی کاربر
        "UserCoreModel", 
        back_populates="upstream",
        lazy="dynamic"
    )
    buyer_wallet_invoice = relationship( # فاکتور های  افزایش شارژ کیف پول کاربر
        "WalletRechargeInvoiceModel", 
        foreign_keys="WalletRechargeInvoiceModel.buyer_user_id", 
        back_populates="buyer_user",
        lazy="dynamic"
    )
    seller_wallet_invoice = relationship( # فاکتور های کاهش شارژ کیف پول کاربر کاربر
        "WalletRechargeInvoiceModel", 
        foreign_keys="WalletRechargeInvoiceModel.seller_user_id", 
        back_populates="seller_user",
        lazy="dynamic"
    )
    buyer_configuration_invoice = relationship( # فاکتور های خرید کانفیگ کاربر
        "ConfigurationInvoiceModel", 
        foreign_keys="ConfigurationInvoiceModel.buyer_user_id", 
        back_populates="buyer_user",
        lazy="dynamic"
    )
    seller_configuration_invoice = relationship( # فاکتور های فروش کانفیگ کاربر
        "ConfigurationInvoiceModel", 
        foreign_keys="ConfigurationInvoiceModel.seller_user_id", 
        back_populates="seller_user",
        lazy="dynamic"
    )
    seller_discounts = relationship( # تخفیف های فروش کاربر
        "DiscountModel", 
        foreign_keys="DiscountModel.seller_user_id", 
        back_populates="seller_user",
        lazy="dynamic"
    )
    user_discounts = relationship( # تخفیف های خرید کاربر
        "UsersDiscountModel", 
        foreign_keys="UsersDiscountModel.user_id", 
        back_populates="user",
        lazy="dynamic"
    )
    buyer_configurations = relationship( # کانفیگ‌های خریداری شده کاربر
        "ConfigurationsModel", 
        foreign_keys="ConfigurationsModel.buyer_user_id", 
        back_populates="buyer_user",
        lazy="dynamic"
    )
    seller_configurations = relationship( # کانفیگ‌های فروخته شده کاربر
        "ConfigurationsModel", 
        foreign_keys="ConfigurationsModel.seller_user_id", 
        back_populates="seller_user",
        lazy="dynamic"
    )


class ConfigurationPanelModel(BaseModel):
    __tablename__ = 'configuration_panel_core'
    user_core = Column( # هسته کاربر
        Integer, 
        ForeignKey(
            'user_core.id',
            ondelete="CASCADE"
        ), 
        nullable=False,
        index=True
    )
    name = Column(String(64)) # نام
    url_address = Column(String) # آدرس
    username = Column(String) # نام کاربری
    password = Column(String) # رمز عبور
    max_volume = Column(Integer) #حداکثر حجم
    used_volume = Column(Integer) #حجم استفاده شده
    is_active = Column(Boolean, default=True) #فعال
    # -------------------------------------------------------------
    user = relationship("UserCoreModel", back_populates="configuration_panel")


class RepresentativesCoreModel(BaseModel):
    __tablename__ = 'representatives_core'
    user_core = Column( # هسته کاربر
        Integer, 
        ForeignKey(
            'user_core.id',
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True, 
        index=True
    )
    phone_number = Column(String(11)) # شماره تلفن
    password = Column(String(255)) # رمز عبور
    password_changed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    ) # زمان آخرین تغییر رمزعبور
    otp_code = Column(String(255), nullable=True) # کد otp 
    otp_exp = Column(DateTime(timezone=True)) # تاریخ انقضای کد otp
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # زمان ثبت نمایندگی
    tel_bot_token = Column(String(128), nullable=True) # توکن بات تلگرام   
    tel_channel_id = Column(String(128), nullable=True) # شناسه کانال تلگرام
    tel_support_id = Column(String(128), nullable=True) # شناسه پشتیبان تلگرام
    card_number = Column(String(16), nullable=True) # شماره کارت
    base_selling_price = Column(BigInteger, nullable=False) # قیمت پایه فروش
    base_purchase_price = Column(BigInteger, nullable=False) # قیمت پایه خرید
    __table_args__ = (
        CheckConstraint('base_selling_price > 0', name='ck_rep_selling_price_positive'),
        CheckConstraint('base_purchase_price >= 0', name='ck_rep_purchase_price_non_negative'),
    )


class WalletInvoiceStatusChoices(enum.Enum):
    PRE_FACTURE = "pre_factore" # پیش فاکتور
    WAITING = "waiting" # در انتظار
    CONFIRMED = "confirmed" # تایید شده
    REJECTED = "rejected" # رد شده
    PAY_WALLET = "pay_wallet" # پرداخت شده به کیف پول
    CONFIGURATION_DIRECTE = "configuration_directe" # کانفیگ مستقیم


class WalletRechargeInvoiceModel(BaseModel):
    __tablename__ = 'wallet_recharge_invoices'
    buyer_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر خریدار
    seller_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر فروشنده
    charge_amount = Column(BigInteger) # مبلغ شارژ
    get_config = Column(Boolean, default=False) # دریافت کانفیگ
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # تاریخ ایجاد
    status = Column(
        Enum(WalletInvoiceStatusChoices), 
        nullable=False, 
        default=WalletInvoiceStatusChoices.WAITING.value,
        server_default=text("'waiting'")
    ) # وضعیت
    descriptions = Column(String) # توضیحات
    # --------------------------------------------------------------------
    buyer_user = relationship( # کاربر خریدار
        "UserCoreModel",
        foreign_keys=[buyer_user_id],
        back_populates="buyer_wallet_invoice"
    )
    seller_user = relationship( # کاربر فروشنده
        "UserCoreModel",
        foreign_keys=[seller_user_id],
        back_populates="seller_wallet_invoice"
    )


class ConfigurationInvoiceModel(BaseModel):
    __tablename__ = 'configuration_invoices'
    buyer_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر خریدار
    seller_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر فروشنده
    volume = Column(Integer) # حجم
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # تاریخ ایجاد
    base_price = Column(BigInteger) # قیمت پایه
    discount_amount = Column(BigInteger, default=0, nullable=False) # مقدار تخفیف
    total_price = Column(BigInteger) # قیمت کل
    descriptions = Column(String) # توضیحات
    # --------------------------------------------------------------------
    buyer_user = relationship( # کاربر خریدار
        "UserCoreModel",
        foreign_keys=[buyer_user_id],
        back_populates="buyer_configuration_invoice"
    )
    seller_user = relationship( # کاربر فروشنده
        "UserCoreModel",
        foreign_keys=[seller_user_id],
        back_populates="seller_configuration_invoice"
    )


class DiscountModel(BaseModel):
    __tablename__ = 'discount'
    seller_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر فروشنده
    code = Column(String(16)) # کد تخفیف
    percent = Column(SmallInteger, nullable=False) # درصد تخفیف
    volume = Column(BigInteger) # حجم
    expired_dt = Column(DateTime(timezone=True), nullable=False) # تاریخ انقضائ
    usage_ceiling = Column(Integer) # محدودیت استفاده
    maximum_discount_amount = Column(BigInteger, default=0) # حداکثر مبلغ
    minimum_purchase_amount = Column(BigInteger, default=0) # حداقل مبلغ خرید
    number_uses_per_user = Column(Integer) # محدودیت استفاده برای هر کاربر
    refund = Column(Boolean, default=False) # بازگشت وجه
    synchronicity = Column(Boolean, default=False) # همزمانی
    __table_args__ = (
        CheckConstraint('percent >= 0 AND percent <= 100', name='ck_discount_percent_range'),
        CheckConstraint('usage_ceiling >= 0', name='ck_discount_usage_ceiling'),
        CheckConstraint('maximum_discount_amount <= minimum_purchase_amount', name='ck_discount_max_le_min'),
    )
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
    USED_BY_USERS = "used_by_users" # کاربران استفاده کرده
    AUTHORIZED_USERS_FOR_USE = "authorized_users_for_use" # کاربران مجاز به استفاده


class UsersDiscountModel(BaseModel):
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


class ConfigurationsModel(BaseModel):
    __tablename__ = 'configurations'
    buyer_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر خریدار
    seller_user_id = Column(Integer, ForeignKey('user_core.id'), nullable=False) # شناسه کاربر فروشنده
    total_volume_gb = Column(BigInteger) # حجم کل خریداری شده
    volume_ceiling_gb = Column(BigInteger) # سقف حجم قابل مصرف
    consumed_volume_gb = Column(BigInteger) # حجم مصرف شده
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # تاریخ ایجاد
    __table_args__ = (
        CheckConstraint('consumed_volume_gb <= volume_ceiling_gb', name='ck_conf_consumed_le_ceiling'),
        CheckConstraint('volume_ceiling_gb <= total_volume_gb', name='ck_conf_ceiling_le_total'),
    )
    # --------------------------------------------------------------------
    buyer_user = relationship( # کاربر خریدار
        "UserCoreModel",
        foreign_keys=[buyer_user_id],
        back_populates="buyer_configurations"
    )
    seller_user = relationship( # کاربر فروشنده
        "UserCoreModel",
        foreign_keys=[seller_user_id],
        back_populates="seller_configurations"
    )
