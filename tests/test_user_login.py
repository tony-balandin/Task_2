import allure

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.endpoints import AUTH_LOGIN
from stellar_burgers.helpers import user_to_payload


@allure.feature("User")
@allure.story("Login")
class TestUserLogin:
    @allure.title("Логин существующего пользователя")
    def test_login_existing_user_success(self, api: StellarApiClient, registered_user):
        user = registered_user["user"]
        payload = user_to_payload(user)
        resp = api.post(AUTH_LOGIN, json={"email": payload["email"], "password": payload["password"]})

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert "accessToken" in resp.json
        assert "refreshToken" in resp.json
        assert resp.json.get("user", {}).get("email") == payload["email"]

    @allure.title("Логин с неверным паролем возвращает 401")
    def test_login_with_wrong_credentials_returns_401(self, api: StellarApiClient, registered_user):
        user = registered_user["user"]
        payload = user_to_payload(user)
        resp = api.post(AUTH_LOGIN, json={"email": payload["email"], "password": "wrong_password"})

        assert resp.status_code == 401
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "email or password are incorrect"
