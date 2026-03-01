import os
import sys

# make src importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import pytest
import requests

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.data_builders import build_unique_user
from stellar_burgers.endpoints import AUTH_REGISTER, AUTH_USER
from stellar_burgers.helpers import (
    auth_header,
    extract_ingredient_ids,
    delete_user_by_token,
    register_unique_user,
    request_ingredients,
    user_to_payload,
)


@pytest.fixture(scope="session")
def api() -> StellarApiClient:
    return StellarApiClient()


@pytest.fixture
def user_cleanup(api: StellarApiClient):
    """Collect access tokens created during a test and delete users afterwards."""
    tokens: list[str] = []

    def add(access_token: str | None) -> None:
        if access_token:
            tokens.append(access_token)

    yield add

    for token in tokens:
        # Cleanup should never break a test.
        try:
            api.delete(AUTH_USER, headers=auth_header(token))
        except requests.exceptions.RequestException:
            pass


@pytest.fixture
def registered_user(api: StellarApiClient):
    """Creates a user before test and deletes it after test."""
    user, resp = register_unique_user(api)
    token = (resp.json or {}).get("accessToken")
    if not token:
        pytest.fail("Setup failed: could not get accessToken for registered_user")

    yield {"user": user, "response": resp, "token": token}

    # Cleanup should never break a test.
    try:
        delete_user_by_token(api, token)
    except requests.exceptions.RequestException:
        pass


@pytest.fixture
def access_token(registered_user) -> str:
    """Access token for an already registered user."""
    return registered_user["token"]


@pytest.fixture
def auth_headers(access_token: str) -> dict:
    """Authorization headers for an already registered user."""
    return auth_header(access_token)


@pytest.fixture
def ingredient_ids(api: StellarApiClient) -> list[str]:
    """At least 2 valid ingredient ids."""
    resp = request_ingredients(api)
    if resp.status_code != 200 or not (resp.json or {}).get("success"):
        pytest.fail("Setup failed: could not fetch ingredients")

    ids = extract_ingredient_ids(resp.json, limit=2)
    if len(ids) < 2:
        pytest.fail("Setup failed: could not extract enough ingredient ids")

    return ids


@pytest.fixture
def create_user(api: StellarApiClient):
    """Factory for creating users; created users are deleted after the test."""
    tokens: list[str] = []

    def _create(payload: dict | None = None):
        user = build_unique_user()
        body = payload if payload is not None else user_to_payload(user)
        resp = api.post(AUTH_REGISTER, json=body)

        token = (resp.json or {}).get("accessToken")
        if token:
            tokens.append(token)

        return user, body, resp

    yield _create

    for token in tokens:
        try:
            delete_user_by_token(api, token)
        except requests.exceptions.RequestException:
            pass
