import pytest
import requests
import time
import json
from datetime import datetime as dt
from datetime import timedelta
from typing import Any, Dict, List


IP: str = "192.168.0.155"
PORT: int = 5000
DEVICE_ID: str = "remote0"
FUSE_AMOUNT: int = 4

WAIT_BETWEEN_FUSES: float = 2.0
WAIT_BEFORE_TEST: float = 2.0

URL: str = f"http://{IP}:{PORT}"


@pytest.fixture
def program_name() -> str:
    return "test_program"


@pytest.fixture
def program() -> List[Dict[str, Any]]:
    return [
        {
            'name': f"fuse{i}",
            'device_id': DEVICE_ID,
            'letter': "a",
            'number': i,
            'timestamp': i * WAIT_BETWEEN_FUSES
        }
        for i in range(FUSE_AMOUNT)
    ]


def _assert_standard_response(
    response: requests.Response, status_codes: List[int]
):
    assert response.status_code in status_codes
    assert "application/json" in response.headers["Content-Type"]
    assert response.text == r"{}"


def test_discover():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/discover")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    assert 'device_id' in response.json()
    assert response.json()['device_id'] == DEVICE_ID
    assert response.json()['is_remote']


def test_index():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "<html>" in response.text


def test_favicon():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/favicon.ico", allow_redirects=False)
    _assert_standard_response(response, [301, 404])
    if response.status_code == 301:
        assert response.headers.get("Location") is not None
        assert response.headers["Location"].startswith("http://")
        assert response.headers["Location"].endswith("/favicon.ico")


def test_static():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/static/device.html")
    assert response.status_code == 200
    assert "text/plain" in response.headers["Content-Type"]
    assert "<html>" in response.text


def test_static_404():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/static/nonexistent.file")
    _assert_standard_response(response, [404])


def test_program_delete(program_name: str, program: List[Dict[str, Any]]):
    time.sleep(WAIT_BEFORE_TEST)
    requests.post(
        f"{URL}/program",
        json={'name': program_name, 'event_list': program}
    )
    response = requests.delete(f"{URL}/program")
    _assert_standard_response(response, [200])


def test_program_post(program_name: str, program: List[Dict[str, Any]]):
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program",
        json={'name': program_name, 'event_list': program}
    )
    _assert_standard_response(response, [200])


def test_program_control_schedule():
    time.sleep(WAIT_BEFORE_TEST)
    schedule_time = (dt.now() + timedelta(days=1)).isoformat()
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'schedule', 'time': schedule_time}
    )
    _assert_standard_response(response, [200])


def test_program_control_unschedule():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'unschedule'}
    )
    _assert_standard_response(response, [200])


def test_program_control_run():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'run'}
    )
    _assert_standard_response(response, [200])


def test_program_control_pause():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'pause'}
    )
    _assert_standard_response(response, [200])


def test_program_control_continue():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'continue'}
    )
    _assert_standard_response(response, [200])
    time.sleep(WAIT_BETWEEN_FUSES * (FUSE_AMOUNT // 2))


def test_program_control_stop():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/program/control",
        json={'action': 'stop'}
    )
    _assert_standard_response(response, [200])
    time.sleep(WAIT_BETWEEN_FUSES)


def test_unlock():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/lock",
        json={'is_locked': False}
    )
    _assert_standard_response(response, [501])


def test_fire():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/fire",
        json={'letter': "a", 'number': 0}
    )
    _assert_standard_response(response, [200])
    time.sleep(WAIT_BETWEEN_FUSES)


def test_lock():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(
        f"{URL}/lock",
        json={'is_locked': True}
    )
    _assert_standard_response(response, [501])


def test_testloop():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(f"{URL}/testloop")
    _assert_standard_response(response, [200])
    time.sleep(WAIT_BETWEEN_FUSES * FUSE_AMOUNT)


def test_system_time():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/system-time")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    assert 'system-time' in response.json()


def test_event_stream():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/event-stream")
    _assert_standard_response(response, [200])


def test_state():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/state")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    assert 'controller' in response.json()
    assert 'hardware' in response.json()
    assert 'config' in response.json()
    assert 'schedule' in response.json()
    assert 'program' in response.json()
    assert 'update_needed' in response.json()


def test_logs():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/logs")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    logs = response.json()
    assert all(filename.endswith(".log") for filename in logs)


def test_logs_file_get():
    time.sleep(WAIT_BEFORE_TEST)
    last_log = requests.get(f"{URL}/logs").json()[-1]
    response = requests.get(f"{URL}/logs/{last_log}")
    assert response.status_code == 200
    assert "text/plain" in response.headers["Content-Type"]
    assert response.text.startswith(">>>")


def test_logs_structured_file():
    time.sleep(WAIT_BEFORE_TEST)
    last_log = requests.get(f"{URL}/logs").json()[-1]
    response = requests.get(f"{URL}/logs/stuctured/{last_log}")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    assert all(key in event for event in response.json() for key in [
        'time', 'level', 'thread', 'file', 'line', 'message'
    ])


def test_logs_file_delete():
    time.sleep(WAIT_BEFORE_TEST)
    last_log = requests.get(f"{URL}/logs").json()[-1]
    response = requests.delete(f"{URL}/logs/{last_log}")
    _assert_standard_response(response, [200])


def test_config_get():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/config")
    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]
    config = response.json()
    assert config.get('device_id') == DEVICE_ID
    assert config.get('fuse_amount') == FUSE_AMOUNT
    assert 'time_resolution' in config
    assert 'ignition_duration' in config


def test_config_post():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(f"{URL}/config")
    _assert_standard_response(response, [501])


def test_update():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(f"{URL}/update")
    _assert_standard_response(response, [501])


def test_not_found():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.get(f"{URL}/nonexistent")
    _assert_standard_response(response, [404])


def test_method_not_allowed():
    time.sleep(WAIT_BEFORE_TEST)
    response = requests.post(f"{URL}/")
    _assert_standard_response(response, [405])
