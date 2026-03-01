import allure
import pytest

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.data_builders import build_unique_user
from stellar_burgers.endpoints import AUTH_REGISTER
from stellar_burgers.helpers import user_to_payload


@allure.feature("User")
@allure.story("Create user")
class TestUserCreate:
    @allure.title("Создание уникального пользователя")
    def test_create_unique_user_success(self, create_user):
        user, payload, resp = create_user()

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert "accessToken" in resp.json
        assert "refreshToken" in resp.json
        assert resp.json.get("user", {}).get("email") == payload["email"]


    @allure.title("Создание пользователя с уже существующим email возвращает 403")
    def test_create_user_that_already_exists_returns_403(self, api: StellarApiClient, registered_user):
        payload = user_to_payload(registered_user["user"])

        resp = api.post(AUTH_REGISTER, json=payload)

        assert resp.status_code == 403
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "User already exists"

    @allure.title("Создание пользователя без обязательного поля возвращает 403")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_missing_required_field_returns_403(
        self,
        api: StellarApiClient,
        missing_field: str,
    ):
        payload = dict(user_to_payload(build_unique_user()))
        payload.pop(missing_field)

        resp = api.post(AUTH_REGISTER, json=payload)

        assert resp.status_code == 403
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "Email, password and name are required fields"
