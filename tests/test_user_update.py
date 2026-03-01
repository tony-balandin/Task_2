import allure
import pytest

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.endpoints import AUTH_USER
from stellar_burgers.helpers import auth_header, random_email


@allure.feature("User")
@allure.story("Update user data")
class TestUserUpdate:
    @allure.title("Обновление email/имени с авторизацией")
    @pytest.mark.parametrize(
        "field,value_factory",
        [
            ("email", lambda: random_email("updated")),
            ("name", lambda: "Updated Name"),
        ],
    )
    def test_update_user_email_or_name_with_authorization_success(
        self,
        api: StellarApiClient,
        access_token: str,
        field: str,
        value_factory,
    ):
        value = value_factory()

        resp = api.patch(AUTH_USER, json={field: value}, headers=auth_header(access_token))

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert resp.json.get("user") is not None
        assert resp.json["user"].get(field) == value

    @allure.title("Обновление пароля с авторизацией")
    def test_update_user_password_with_authorization_success(
        self,
        api: StellarApiClient,
        access_token: str,
    ):
        resp = api.patch(
            AUTH_USER,
            json={"password": "UpdatedPassword123"},
            headers=auth_header(access_token),
        )

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert resp.json.get("user") is not None

    @allure.title("Обновление данных без авторизации возвращает 401")
    @pytest.mark.parametrize(
        "payload",
        [
            {"email": "unauth_email@yandex.ru"},
            {"name": "Unauth Name"},
            {"password": "UnauthPassword123"},
        ],
    )
    def test_update_user_without_authorization_returns_401(self, api: StellarApiClient, payload: dict):
        resp = api.patch(AUTH_USER, json=payload)

        assert resp.status_code == 401
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "You should be authorised"
