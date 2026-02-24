import allure

from stellar_burgers.api_client import StellarApiClient
from stellar_burgers.endpoints import ORDERS
from stellar_burgers.helpers import (
    auth_header,
    extract_ingredient_ids,
    request_ingredients,
)


@allure.feature("Orders")
@allure.story("Create order")
class TestCreateOrder:
    @allure.title("Создание заказа с авторизацией и ингредиентами")
    def test_create_order_with_authorization_and_ingredients_success(self, api: StellarApiClient, registered_user):
        token = registered_user["response"].json.get("accessToken")
        assert token is not None
        ingredients_resp = request_ingredients(api)
        assert ingredients_resp.status_code == 200
        assert ingredients_resp.json.get("success") is True
        ingredient_ids = extract_ingredient_ids(ingredients_resp.json, limit=2)
        assert len(ingredient_ids) >= 2

        resp = api.post(ORDERS, json={"ingredients": ingredient_ids}, headers=auth_header(token))

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert resp.json.get("order", {}).get("number") is not None

    @allure.title("Создание заказа без авторизации с ингредиентами")
    def test_create_order_without_authorization_and_ingredients_success(self, api: StellarApiClient):
        ingredients_resp = request_ingredients(api)
        assert ingredients_resp.status_code == 200
        assert ingredients_resp.json.get("success") is True
        ingredient_ids = extract_ingredient_ids(ingredients_resp.json, limit=2)
        assert len(ingredient_ids) >= 2

        resp = api.post(ORDERS, json={"ingredients": ingredient_ids})

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert resp.json.get("order", {}).get("number") is not None

    @allure.title("Создание заказа без ингредиентов возвращает 400")
    def test_create_order_without_ingredients_returns_400(self, api: StellarApiClient):
        resp = api.post(ORDERS, json={"ingredients": []})

        assert resp.status_code == 400
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "Ingredient ids must be provided"

    @allure.title("Создание заказа с неверным id ингредиента возвращает 400")
    def test_create_order_with_invalid_ingredient_hash_returns_400(self, api: StellarApiClient):
        # Current API version validates ingredient ids and returns 400 for incorrect values.
        resp = api.post(ORDERS, json={"ingredients": ["invalid_hash"]})

        assert resp.status_code == 400
        assert resp.json.get("success") is False
        assert "incorrect" in (resp.json.get("message") or "").lower()


@allure.feature("Orders")
@allure.story("Get user orders")
class TestGetUserOrders:
    @allure.title("Получение заказов авторизованного пользователя")
    def test_get_orders_authorized_user_success(self, api: StellarApiClient, registered_user):
        token = registered_user["response"].json.get("accessToken")
        assert token is not None

        resp = api.get(ORDERS, headers=auth_header(token))

        assert resp.status_code == 200
        assert resp.json.get("success") is True
        assert "orders" in resp.json

    @allure.title("Получение заказов без авторизации возвращает 401")
    def test_get_orders_unauthorized_user_returns_401(self, api: StellarApiClient):
        resp = api.get(ORDERS)

        assert resp.status_code == 401
        assert resp.json.get("success") is False
        assert resp.json.get("message") == "You should be authorised"
