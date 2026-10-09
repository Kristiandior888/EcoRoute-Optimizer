import pytest

from unittest.mock import patch, MagicMock
from static.python.main import geocode, recommend_speed, haversine, get_gas_prices, get_fuel_price
from bs4 import BeautifulSoup


HTML_ALL_CAR_PRICES = """
<html><body>
  <div class="fuel-card border-ai80"><span itemprop="price">92.10 ₽</span></div>
  <div class="fuel-card border-ai92"><span itemprop="price">95.20 ₽</span></div>
  <div class="fuel-card border-ai95"><span itemprop="price">98.30 ₽</span></div>
  <div class="fuel-card border-diesel"><span itemprop="price">81.25 ₽</span></div>
</body></html>
"""

HTML_EMPTY = """
<html><body>
</body></html>
"""

HTML_EMPTY_DIVS = """
<html><body>
  <div class="fuel-card border-ai80"></div>
  <div class="fuel-card border-ai92"></div>
  <div class="fuel-card border-ai95"></div>
  <div class="fuel-card border-diesel"></div>
</body></html>
"""


@pytest.mark.parametrize(
    "status_code, json_data, exp_value",
    [
        (200, [{"lat": "55.7", "lon": "37.6"}], (55.7, 37.6)),
        (422, [], (None, None)),
        (200, [], (None, None))
    ]
)
def test_geocode(status_code, json_data, exp_value, make_mock_response):
    """
    Проверяет geocode при замоканном ответе Nominatim.

    Покрывает три ветки: успешный ответ с результатом, статус не 200
    и статус 200 с пустым списком результатов.

    Args:
        status_code: HTTP-статус мок-ответа.
        json_data: тело мок-ответа (результат json()).
        exp_value: ожидаемый кортеж (широта, долгота).
        make_mock_response: фикстура-фабрика мок-ответов.
    """
    response = make_mock_response(status=status_code, json_data=json_data)

    with patch(target="static.python.main.requests.get", return_value=response):
        assert geocode(location="Курган") == exp_value


@pytest.mark.parametrize(
        "distance, vehicle_type, exp_value",
        [
            (1000, "truck", (80, 100)),
            (1000, "bus", (60, 80)),
            (1000, "car", (90, 70))
        ]
)
def test_recommend_speed(distance, vehicle_type, exp_value):
    """
    Проверяет recommend_speed для каждого типа транспорта.

    Args:
        distance: расстояние, км.
        vehicle_type: тип транспорта ("truck", "bus", "car").
        exp_value: ожидаемый кортеж (рекомендуемая скорость, расход топлива, л).
    """
    assert recommend_speed(distance=distance, vehicle_type=vehicle_type) == exp_value


def test_haversine():
    """
    Проверяет haversine на паре Москва — Санкт-Петербург.

    Ожидаемое расстояние около 635 км, допустимое отклонение 2 %.
    """
    res = haversine(55.7558, 37.6173, 59.9343, 30.3351)
    exp = pytest.approx(635, rel=0.02)

    assert res == exp


@pytest.mark.parametrize(
        "html_data, status, vehicle_type, gas_amount, exp_data",
        [
            (HTML_ALL_CAR_PRICES, 200, "car", 50, 4760),
            (HTML_ALL_CAR_PRICES, 200, "truck", 200, 16250),
            (HTML_EMPTY, 200, "car", 50, 2500),
            (HTML_EMPTY, 200, "truck", 200, 11000)
        ]
)
def test_get_gas_prices(html_data, status, vehicle_type, 
                        gas_amount, exp_data, make_mock_response):
    """
    Проверяет get_gas_prices при замоканной странице с ценами на топливо.

    Покрывает расчёт по найденным ценам и использование резервных цен
    (50 для легковых, 55 для остальных), когда цены на странице не найдены.

    Args:
        html_data: HTML-страница, которую вернёт мок.
        status: HTTP-статус мок-ответа.
        vehicle_type: тип транспорта.
        gas_amount: количество топлива, л.
        exp_data: ожидаемая итоговая стоимость, округлённая до целых.
        make_mock_response: фикстура-фабрика мок-ответов.
    """
    response = make_mock_response(status=status, text=html_data)

    with patch(target="static.python.main.requests.get", return_value=response):
        assert get_gas_prices(vehicle_type=vehicle_type, gas_amount=gas_amount) == exp_data


@pytest.mark.parametrize(
        "html_data, fuel_class, exp_data",
        [
            (HTML_ALL_CAR_PRICES, "fuel-card border-ai80", 92.10),
            (HTML_EMPTY, "fuel-card border-ai80", None),
            (HTML_EMPTY_DIVS, "fuel-card border-ai80", None)
        ])
def test_get_fuel_price(html_data, fuel_class, make_mock_response, exp_data):
    """
    Проверяет парсинг цены топлива функцией get_fuel_price.

    Покрывает три случая: цена найдена, блок с нужным классом отсутствует,
    блок есть, но внутри него нет элемента с ценой.

    Args:
        html_data: HTML-страница для разбора.
        fuel_class: CSS-класс блока с нужным видом топлива.
        make_mock_response: фикстура-фабрика мок-ответов.
        exp_data: ожидаемая цена (float) или None.
    """
    response = make_mock_response(text=html_data)
    soup = BeautifulSoup(response.text, 'html.parser')

    assert get_fuel_price(fuel_class=fuel_class, soup=soup) == exp_data