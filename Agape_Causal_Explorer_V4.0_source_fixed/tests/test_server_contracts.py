import pytest
from fastapi.testclient import TestClient
import live_server

client = TestClient(live_server.app)

def test_reset_endpoint_resets_state():
    r = client.post("/api/system/reset")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Systemzustand zurückgesetzt." in data["message"]
    assert data["state"]["gws"] == 1.0
    assert data["state"]["energy"] == 1.0
    assert len(data["state"]["rings"]) == 5

def test_validate_accepts_minimal_spec():
    spec = {
        "nl_query": "Was wäre wenn eine globale Krise passiert?",
        "j_metrics_impact": {"j1": 0, "j2": 0, "j3": 0, "j4": 0, "j5": 0}
    }
    r = client.post("/api/causal/validate", json=spec)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "causal_spec" in data

def test_validate_rejects_out_of_range_gws_delta():
    spec = {
        "nl_query": "Test gws_delta > 1",
        "gws_delta": 2.0,
        "j_metrics_impact": {"j1": 0, "j2": 0, "j3": 0, "j4": 0, "j5": 0}
    }
    r = client.post("/api/causal/validate", json=spec)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "gws_delta" in data["error"]

def test_simulation_runs_and_returns_ticks():
    spec = {
        "nl_query": "Basic sim run",
        "gws_delta": 0.2,
        "duration_steps": 5,
        "j_metrics_impact": {"j1": 0, "j2": 0, "j3": 0, "j4": 0, "j5": 0}
    }
    r = client.post("/api/sim/run", json=spec)
    assert r.status_code == 200
    data = r.json()
    assert "ticks" in data
    ticks = data["ticks"]
    assert len(ticks) == 5
    assert ticks[0]["gws"] == pytest.approx(1.0)
    assert ticks[-1]["gws"] == pytest.approx(1.2)
