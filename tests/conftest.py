import pytest

from unittest.mock import MagicMock


@pytest.fixture()
def make_mock_response():
    """
    Возвращает фабрику мок-ответов, имитирующих объект response из requests.

    Фабрика принимает параметры:
        status: HTTP-статус ответа (по умолчанию 200).
        json_data: значение, которое вернёт response.json().
        text: значение атрибута response.text (тело ответа как строка).

    Returns:
        Функцию _make_response, создающую MagicMock с заданными
        status_code, json() и text.
    """
    def _make_response(status=200, json_data=None, text=None):
        """
        Создаёт мок-ответ с заданными статусом, JSON и текстом.

        Args:
            status: HTTP-статус ответа.
            json_data: результат вызова response.json().
            text: тело ответа как строка.

        Returns:
            MagicMock с атрибутами status_code, text и методом json().
        """
        response = MagicMock()
        response.status_code = status
        response.json.return_value = json_data
        response.text = text
        return response
    return _make_response