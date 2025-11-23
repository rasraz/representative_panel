# models.py
from __future__ import annotations

from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProxyProtocolSettings(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[int] = None
    enable: bool = True


class Proxies(BaseModel):
    vmess: Optional[ProxyProtocolSettings | dict] = None
    vless: Optional[ProxyProtocolSettings | dict] = None
    trojan: Optional[ProxyProtocolSettings | dict] = None
    shadowsocks: Optional[ProxyProtocolSettings | dict] = None


class Inbounds(BaseModel):
    model_config = ConfigDict(extra="allow")


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    proxies: Proxies = Field(default_factory=Proxies)
    inbounds: Optional[Inbounds] = None
    data_limit: Optional[int] = None  # bytes
    expire: Optional[int] = None      # unix timestamp
    status: Optional[Literal["active", "disabled", "limited", "expired", "on_hold"]] = "active"
    on_hold_expire_duration: Optional[int] = None
    group_ids: Optional[List[int]] = None

    @field_validator("data_limit", "expire", "on_hold_expire_duration", mode="before")
    @classmethod
    def zero_means_none(cls, v):
        return None if v == 0 else v


class UserModifyRequest(BaseModel):
    proxies: Optional[Proxies] = None
    inbounds: Optional[Inbounds] = None
    data_limit: Optional[int] = None
    expire: Optional[int] = None
    status: Optional[Literal["active", "disabled", "limited", "expired", "on_hold"]] = None
    on_hold_expire_duration: Optional[int] = None
    group_ids: Optional[List[int]] = None
    note: Optional[str] = None

    @field_validator("data_limit", "expire", "on_hold_expire_duration", mode="before")
    @classmethod
    def zero_means_none(cls, v):
        return None if v == 0 else v


class GroupCreateRequest(BaseModel):
    name: str
    inbound_tags: Optional[List[str]] = None


class SystemStats(BaseModel):
    version: str
    # سایر فیلدهای سیستم در صورت نیاز اضافه می‌شود


class UserResponse(BaseModel):
    username: str
    status: str
    used_traffic: int = 0
    data_limit: Optional[int] = None
    expire: Optional[int] = None
    subscription_url: str
    proxies: Dict[str, Any] = {}
    inbounds: Dict[str, List[str]] = {}
    on_hold_expire_duration: Optional[int] = None
    group_ids: Optional[List[int]] = None


class GroupResponse(BaseModel):
    id: int
    name: str
    inbound_tags: Optional[List[str]] = None