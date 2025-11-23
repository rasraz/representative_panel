# marzban_api.py
from __future__ import annotations

import time
import re
from typing import Dict, List, Optional

import requests
from project.core.schemas.admin.marzban import (
    AdminTokenResponse, UserCreateRequest, UserModifyRequest,
    GroupCreateRequest, SystemStats, UserResponse, GroupResponse
)

session = requests.Session()
session.headers.update({"Accept": "application/json"})

_TOKEN_CACHE: Dict[int, dict] = {}


def _get_panel(location: str) -> Dict:
    raise NotImplementedError("باید _get_panel را پیاده‌سازی کنید")


def token_panel(panel: dict) -> AdminTokenResponse | dict:
    panel_id = panel["id"]
    if panel_id in _TOKEN_CACHE:
        cached = _TOKEN_CACHE[panel_id]
        if time.time() - cached["timestamp"] < 3600:
            return cached["token_data"]

    url = f"{panel['url_panel'].rstrip('/')}/api/admin/token"
    payload = {"username": panel["username_panel"], "password": panel["password_panel"]}

    try:
        resp = session.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        data = AdminTokenResponse(**resp.json())
        _TOKEN_CACHE[panel_id] = {"timestamp": time.time(), "token_data": data}
        return data
    except Exception as e:
        return {"error": str(e)}


def _auth_headers(location: str):
    panel = _get_panel(location)
    token = token_panel(panel)
    access_token = token.get("access_token") if isinstance(token, dict) else token.access_token
    return {"Authorization": f"Bearer {access_token}"}


def get_user(username: str, location: str) -> UserResponse | dict:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/user/{username}"
    resp = session.get(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return UserResponse(**resp.json())


def reset_user_data_usage(username: str, location: str) -> dict:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/user/{username}/reset"
    resp = session.post(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return resp.json()


def add_user(
    username: str,
    expire: int,
    data_limit: int,
    location: str,
    is_test: bool = False
) -> UserResponse | dict:
    panel = _get_panel(location)
    ensure_default_groups(location)

    base_payload = {
        "username": username,
        "proxies": panel.get("proxies", "{}"),
        "data_limit": data_limit if data_limit > 0 else None,
    }
    if panel.get("inbounds") and panel["inbounds"] not in ("null", ""):
        base_payload["inbounds"] = panel["inbounds"]

    payload = UserCreateRequest(**base_payload)

    if expire > 0 and panel.get("onholdstatus") == "ononhold":
        payload.expire = None
        payload.status = "on_hold"
        payload.on_hold_expire_duration = expire - int(time.time())
    else:
        payload.expire = expire if expire > 0 else None

    if is_marzban_version_above_084(location):
        group_name = "mirza_test" if is_test else "mirza_paid"
        group_id = get_group_id_by_name(location, group_name)
        if group_id:
            payload.group_ids = [group_id]

    url = f"{panel['url_panel'].rstrip('/')}/api/user"
    headers = {**_auth_headers(location), "Content-Type": "application/json"}
    resp = session.post(url, json=payload.model_dump(exclude_none=True), headers=headers, timeout=10)
    resp.raise_for_status()
    return UserResponse(**resp.json())


def modify_user(location: str, username: str, data: dict) -> dict:
    payload = UserModifyRequest(**data)
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/user/{username}"
    headers = {**_auth_headers(location), "Content-Type": "application/json"}
    resp = session.put(url, json=payload.model_dump(exclude_none=True), headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def remove_user(location: str, username: str) -> dict:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/user/{username}"
    resp = session.delete(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return resp.json()


def revoke_subscription(username: str, location: str) -> dict:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/user/{username}/revoke_sub"
    resp = session.post(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_system_stats(location: str) -> SystemStats:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/system"
    resp = session.get(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return SystemStats(**resp.json())


def is_marzban_version_above_084(location: str) -> bool:
    stats = get_system_stats(location)
    match = re.search(r"(\d+\.\d+\.\d+)", stats.version)
    return tuple(map(int, match.group(1).split("."))) > (0, 8, 4) if match else False


def get_groups(location: str) -> List[GroupResponse]:
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/groups"
    resp = session.get(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    groups = data.get("groups") or data if isinstance(data, list) else []
    return [GroupResponse(**g) for g in groups]


def get_group_id_by_name(location: str, name: str) -> Optional[int]:
    for group in get_groups(location):
        if group.name.lower() == name.lower():
            return group.id
    return None


def create_group(location: str, name: str, inbound_tags: Optional[List[str]] = None) -> dict:
    payload = GroupCreateRequest(name=name, inbound_tags=inbound_tags or [])
    panel = _get_panel(location)
    url = f"{panel['url_panel'].rstrip('/')}/api/group"
    headers = {**_auth_headers(location), "Content-Type": "application/json"}
    resp = session.post(url, json=payload.model_dump(), headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_inbound_tags(location: str) -> List[str]:
    panel = _get_panel(location)
    # روش جدید
    try:
        url = f"{panel['url_panel'].rstrip('/')}/api/cores"
        resp = session.get(url, headers=_auth_headers(location), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        tags = {i.get("tag") for c in data.get("cores", []) for i in c.get("config", {}).get("inbounds", []) if i.get("tag")}
        if tags:
            return list(tags)
    except:
        pass

    # روش قدیمی
    url = f"{panel['url_panel'].rstrip('/')}/api/inbounds"
    resp = session.get(url, headers=_auth_headers(location), timeout=10)
    resp.raise_for_status()
    return [i["tag"] for i in resp.json() if i.get("tag")]


def ensure_default_groups(location: str) -> None:
    if not is_marzban_version_above_084(location):
        return
    existing = {g.name.lower() for g in get_groups(location)}
    required = {"mirza_paid", "mirza_test"}
    tags = get_inbound_tags(location)
    for name in required - existing:
        create_group(location, name, tags)