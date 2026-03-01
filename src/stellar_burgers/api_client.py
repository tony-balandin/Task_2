from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import allure  # type: ignore
except ImportError:  # pragma: no cover
    # Minimal fallback to keep code runnable even if allure is not installed.
    # In the project environment we run with allure-pytest.
    from typing import Callable, TypeVar

    _F = TypeVar("_F", bound=Callable[..., object])

    def _step(_: str):
        def _decorator(func: _F) -> _F:
            return func

        return _decorator

    class allure:  # type: ignore
        step = staticmethod(_step)
import requests

from .config import API_PREFIX, BASE_URL


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    json: Dict[str, Any]


class StellarApiClient:
    """Thin wrapper over requests for Stellar Burgers API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def _url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}{API_PREFIX}{path}"

    @allure.step("GET {path}")
    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        r = self._session.get(self._url(path), headers=headers)
        return ApiResponse(status_code=r.status_code, json=_safe_json(r))

    @allure.step("POST {path}")
    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        r = self._session.post(self._url(path), json=json, headers=headers)
        return ApiResponse(status_code=r.status_code, json=_safe_json(r))

    @allure.step("PATCH {path}")
    def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        r = self._session.patch(self._url(path), json=json, headers=headers)
        return ApiResponse(status_code=r.status_code, json=_safe_json(r))

    @allure.step("DELETE {path}")
    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        r = self._session.delete(self._url(path), headers=headers)
        return ApiResponse(status_code=r.status_code, json=_safe_json(r))


def _safe_json(response: requests.Response) -> Dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        return {}
