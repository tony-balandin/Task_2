from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from .api_client import ApiResponse, StellarApiClient
from .data_builders import UserCredentials, build_unique_user
from .endpoints import AUTH_REGISTER, AUTH_USER, INGREDIENTS


def user_to_payload(user: UserCredentials) -> Dict[str, str]:
    return {"email": user.email, "password": user.password, "name": user.name}


def auth_header(access_token: str) -> Dict[str, str]:
    return {"Authorization": access_token}


def random_email(prefix: str = "autotest") -> str:
    """Generate a unique email to avoid collisions on a shared test stand."""
    return f"{prefix}_{uuid4().hex}@yandex.ru"


def request_ingredients(api: StellarApiClient) -> ApiResponse:
    return api.get(INGREDIENTS)


def extract_ingredient_ids(response_json: Dict[str, Any], limit: int = 2) -> List[str]:
    data = response_json.get("data") or []
    ids = [item["_id"] for item in data if isinstance(item, dict) and "_id" in item]
    return ids[:limit]


def register_unique_user(api: StellarApiClient) -> tuple[UserCredentials, ApiResponse]:
    """Create a new unique user via API.

    No assertions here: validation belongs to tests.
    """
    user = build_unique_user()
    resp = api.post(AUTH_REGISTER, json=user_to_payload(user))
    return user, resp


def delete_user_by_token(api: StellarApiClient, access_token: str | None) -> None:
    """Delete user by access token (best-effort cleanup)."""
    if access_token:
        api.delete(AUTH_USER, headers=auth_header(access_token))
