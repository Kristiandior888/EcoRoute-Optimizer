import pytest

from static.python.driver_schedule import plan_driver_schedule


@pytest.mark.parametrize("total_distance, speed, exp_action", [
    (100, 50, "drive"),
    (500, 100, "break"),
    (2000, 100, 'overnight_rest')
])
def test_plan_driver_schedule(total_distance, speed, exp_action):
    result = plan_driver_schedule(total_distance=total_distance, speed=speed)
    actions = {item["action"] for item in result}

    assert exp_action in actions

