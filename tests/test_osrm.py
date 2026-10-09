import pytest

from unittest.mock import patch, MagicMock
from static.python.osrm import get_route_osrm

OSRM_SUCCESS_RESPONSE = {
    "code": "Ok",
    "routes": [
        {
            "distance": 705659.1,
            "duration": 30038.9,
            "geometry": {
                "type": "LineString",
                "coordinates": [[37.616948, 55.756371], [30.335037, 59.934308]]
            }
        }
    ],
    "waypoints": []
}

OSRM_EMPTY_RESPONSE = {}


@pytest.mark.parametrize("lat1, lon1, lat2, lon2, status, json_data, exp_data",
    [
        ("55.7558", "37.6173", "59.9343", "30.3351", 200, OSRM_SUCCESS_RESPONSE, (705.6591, 8.344138888888889, {
                "type": "LineString",
                "coordinates": [[37.616948, 55.756371], [30.335037, 59.934308]]
            })),
        ("", "", "", "", 422, OSRM_EMPTY_RESPONSE, (None, None, None)),
        ("55.7558", "37.6173", "59.9343", "30.3351", 200, OSRM_EMPTY_RESPONSE, (None, None, None)),
        ("55.7558", "37.6173", "59.9343", "30.3351", 200, {"code": "NoRoute"}, (None, None, None)),
        ("55.7558", "37.6173", "59.9343", "30.3351", 200, {"code": "Ok", "routes": []}, (None, None, None))
    ])
def test_get_route_osrm(lat1, lon1, lat2, lon2, status, json_data, exp_data, make_mock_response):
    """
    Проверяет get_route_osrm при замоканном ответе OSRM.

    Покрывает все ветки условия: успешный маршрут, статус не 200,
    пустой ответ, ответ без ключа "routes" и пустой список "routes".

    Args:
        lat1: широта начальной точки.
        lon1: долгота начальной точки.
        lat2: широта конечной точки.
        lon2: долгота конечной точки.
        status: HTTP-статус мок-ответа.
        json_data: тело мок-ответа (результат json()).
        exp_data: ожидаемый кортеж (расстояние в км, время в часах, геометрия)
            или (None, None, None).
        make_mock_response: фикстура-фабрика мок-ответов.
    """
    response = make_mock_response(status=status, json_data=json_data)

    with patch(target="static.python.osrm.requests.get", return_value=response):
        assert get_route_osrm(lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2) == exp_data