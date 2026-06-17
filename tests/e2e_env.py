from __future__ import annotations

import json
import os
import time
import urllib.request

BASE = os.environ.get("URISYS_BASE_URL", "http://127.0.0.1:8790")


def post(uri, payload=None, context=None, expect_ok=True):
    body = json.dumps({"uri": uri, "payload": payload or {}, "context": context or {}}).encode()
    req = urllib.request.Request(BASE + "/uri/call", data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        data = json.loads(err.read().decode())
    if expect_ok and not data.get("ok"):
        raise AssertionError(data)
    return data


def wait_health():
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=3) as resp:
                data = json.loads(resp.read().decode())
                if data.get("ok"):
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("health check timeout")


def main():
    wait_health()
    health = post("env://runtime/query/health")
    assert "APP_NAME" in health["result"]["public_vars"]

    app_name = post("env://runtime/var/APP_NAME/query/value")
    assert app_name["result"]["value"] == "urisys-env-demo"

    startup = post("env://runtime/config/query/startup")
    assert startup["result"]["public"]["APP_ENV"]["value"] == "docker"

    masked = post("env://runtime/secret/SMTP_PASSWORD/query/masked")
    assert masked["result"]["exists"] is True
    assert masked["result"]["masked"] != "smtp-secret-from-docker-secret"

    denied = post("env://runtime/secret/SMTP_PASSWORD/query/value", context={"approved": True}, expect_ok=False)
    assert denied["ok"] is False

    set_flag = post("env://runtime/var/FEATURE_FLAG_DEMO/command/set", {"value": "on"}, {"approved": True})
    assert set_flag["result"]["set"] is True
    flag = post("env://runtime/var/FEATURE_FLAG_DEMO/query/value")
    assert flag["result"]["value"] == "on"
    print(json.dumps({"ok": True, "message": "env:// docker e2e passed"}, indent=2))


if __name__ == "__main__":
    main()
