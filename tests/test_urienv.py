from __future__ import annotations

import os
from pathlib import Path

from uri_control import CapabilityRegistry, InMemoryEventStore, UriControlRuntime


def manifest_paths(schemes: list[str]) -> list[Path]:
    root = Path(__file__).resolve().parents[1].parent / "urienv"
    return [root / "manifest.yaml"] if "env" in schemes else []


def runtime():
    registry = CapabilityRegistry.from_manifest_files([str(p) for p in manifest_paths(["env"])])
    return UriControlRuntime(registry=registry, event_store=InMemoryEventStore())


def base_context():
    return {
        "env_config": {
            "public_vars": ["APP_NAME", "FEATURE_FLAG_DEMO"],
            "secret_vars": ["SMTP_PASSWORD"],
            "mutable_vars": ["FEATURE_FLAG_DEMO"],
        }
    }


def test_public_var_can_be_read(monkeypatch):
    monkeypatch.setenv("APP_NAME", "test-app")
    res = runtime().call("env://runtime/var/APP_NAME/query/value", {}, base_context())
    assert res.ok is True
    assert res.result["value"] == "test-app"


def test_non_allowlisted_var_is_blocked(monkeypatch):
    monkeypatch.setenv("PRIVATE_VAR", "secret")
    res = runtime().call("env://runtime/var/PRIVATE_VAR/query/value", {}, base_context())
    assert res.ok is False
    assert "not in public env allowlist" in (res.error or "")


def test_secret_is_masked_but_not_revealed_without_gate(monkeypatch):
    monkeypatch.setenv("SMTP_PASSWORD", "supersecret")
    rt = runtime()
    masked = rt.call("env://runtime/secret/SMTP_PASSWORD/query/masked", {}, base_context())
    assert masked.ok is True
    assert masked.result["masked"] != "supersecret"

    denied = rt.call("env://runtime/secret/SMTP_PASSWORD/query/value", {}, {**base_context(), "approved": True})
    assert denied.ok is False
    assert "allow_secret_read" in (denied.error or "")


def test_secret_can_be_revealed_with_explicit_gate(monkeypatch):
    monkeypatch.setenv("SMTP_PASSWORD", "supersecret")
    res = runtime().call(
        "env://runtime/secret/SMTP_PASSWORD/query/value",
        {},
        {**base_context(), "approved": True, "allow_secret_read": True},
    )
    assert res.ok is True
    assert res.result["value"] == "supersecret"


def test_mutable_var_is_process_local(monkeypatch):
    monkeypatch.setenv("FEATURE_FLAG_DEMO", "off")
    rt = runtime()
    res = rt.call(
        "env://runtime/var/FEATURE_FLAG_DEMO/command/set",
        {"value": "on"},
        {**base_context(), "approved": True},
    )
    assert res.ok is True
    assert os.environ["FEATURE_FLAG_DEMO"] == "on"
