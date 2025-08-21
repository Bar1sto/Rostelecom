# tests/test_integration.py
import time
import json
import httpx

B_URL = "https://localhost:8443"
VERIFY_TLS = False 

def post_create(equipment_id: str, payload: dict) -> str:
    with httpx.Client(verify=VERIFY_TLS, timeout=30.0) as c:
        r = c.post(
            f"{B_URL}/api/v1/equipment/cpe/{equipment_id}",
            headers={"content-type": "application/json"},
            data=json.dumps(payload),
        )
        r.raise_for_status()
        body = r.json()
        assert body["code"] == 200
        assert "taskId" in body
        return body["taskId"]

def get_status(equipment_id: str, task_id: str) -> dict:
    with httpx.Client(verify=VERIFY_TLS, timeout=15.0) as c:
        r = c.get(f"{B_URL}/api/v1/equipment/cpe/{equipment_id}/task/{task_id}")
        r.raise_for_status()
        return r.json()

def wait_status(equipment_id: str, task_id: str, expect_code: int, timeout_sec: float = 20.0):
    t0 = time.time()
    last = None
    while time.time() - t0 < timeout_sec:
        last = get_status(equipment_id, task_id)
        if last.get("code") == expect_code:
            return last
        time.sleep(0.5)
    raise AssertionError(f"expected code={expect_code}, got last={last}")

PAYLOAD = {
    "timeoutInSeconds": 5,
    "parameters": {"username": "u", "password": "p", "interfaces": [1]}
}

def test_create_returns_task_id():
    task_id = post_create("ABC123", PAYLOAD)
    assert len(task_id) > 0

def test_status_soon_after_post_is_pending():
    task_id = post_create("ABC123", PAYLOAD)
    body = get_status("ABC123", task_id)
    assert body["code"] == 204
    assert "Task is still running" in body["message"]

def test_dev404_becomes_404_quickly():
    task_id = post_create("DEV404", PAYLOAD)
    body = wait_status("DEV404", task_id, expect_code=404, timeout_sec=10.0)
    assert body["code"] == 404

def test_dev500_becomes_500_after_retries():
    task_id = post_create("DEV500", PAYLOAD)
    body = wait_status("DEV500", task_id, expect_code=500, timeout_sec=20.0)
    assert body["code"] == 500