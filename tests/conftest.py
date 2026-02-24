import os
import sys

# make src importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import pytest

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.endpoints import AUTH_USER
from stellar_burgers.helpers import (
    auth_header,
    delete_user_by_token,
    register_unique_user,
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
        api.delete(AUTH_USER, headers=auth_header(token))


@pytest.fixture
def registered_user(api: StellarApiClient):
    """Creates a user before test and deletes it after test."""
    user, resp = register_unique_user(api)
    yield {"user": user, "response": resp}

    delete_user_by_token(api, resp.json.get("accessToken"))
