import pytest

from unittest.mock import MagicMock


@pytest.fixture()
def make_mock_response():
    def _make_response(status=200, json_data=None, text=None):
        response = MagicMock()
        response.status_code = status
        response.json.return_value = json_data
        response.text = text
        return response
    return _make_response