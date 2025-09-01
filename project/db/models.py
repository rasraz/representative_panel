from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from .database import base



class BaseModel():
	_id = Column(Integer, unique=True, primary_key=True)


class UserBaseModel(BaseModel, base):
    """
    مدل کاربری پایه
    """
    __tablename__ = 'userbase'
    phone_number = Column(String(11)) # شماره تلفن
    first_name = Column(String(32)) # نام
    last_name = Column(String(32)) # نام خانوادگی
    password = Column(String(128)) # رمز عبور
    national_code = Column(String(10)) # کد ملی
    wallet_balance =Column(Integer) # موجودی کیف پول
    total_volume = Column(String(16)) # حجم کل (بر حسب گیگابایت)
    sales_volume_ceiling = Column(Integer) # سقف حجم قابل فروش
    base_price = Column(String(16))
    tel_chat_id = Column(String(128)) # شناسه چت تلگرام
    tel_bot_token = Column(String(128)) # توکن بات تلگرام   
    tel_channel_id = Column(String(128)) # شناسه کانال تلگرام
    two_step_verification = Column(Boolean, default=False) # چک کردن امنیت 2 مرحله
    is_active = Column(Boolean, default=False) # حساب کاربر فعال است
    is_repres = Column(Boolean, default=False) # حساب کاربر نماینده است


class InvoiceStatus(enum.Enum):
    """
    حالت های وضعیت برای فاکتور‌ها
    """
    WAITING = "waiting" # در انتظار
    CONFIRMED = "confirmed" # تایید شده
    REJECTED = "rejected" # رد شده

class PurchaseInvoiceModel(BaseModel, base):
    """
    مدل فاکتورهای خرید
    """
    __tablename__ = 'purchase_invoices'
    volume = Column(String(16)) # حجم
    create_dt = Column(DateTime, server_default=func.now()) # تاریخ ثبت
    expiration_dt = Column(DateTime) # تاریخ انقضاي
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.WAITING) # وضعیت
    base_price = Column(String(16)) # قیمت پایه
    discount_amount = Column(String(16)) # مقدار تخفیف
    total_price = Column(String(16)) # قیمت کل
    descriptions = Column(String) # توضیحات
    config_output = Column(Boolean, default=False) # خروجی کانفیگ


class DiscountModel(BaseModel, base):
    """
    مدل تخفیف ها
    """
    __tablename__ = 'discount'
    code = Column(String(16)) # کد تخفیف
    percent = Column(String(16)) # درصد تخفیف
    volume = Column(String(16)) # حجم
    expired_dt = Column(DateTime, server_default=func.now()) # تاریخ انقضائ
    usage_ceiling = Column(Integer) # محدودیت استفاده
    maximum_discount_amount = Column(String(16)) # حداکثر مبلغ
    minimum_purchase_amount = Column(String(16)) # حداقل مبلغ خرید
    number_uses_per_user = Column(String(16)) # محدودیت استفاده برای هر کاربر
    refund = Column(Boolean, default=False) # بازگشت وجه
    synchronicity = Column(Boolean, default=False) # همزمانی
