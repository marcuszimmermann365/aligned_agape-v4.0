import json
import os
import pytest

FIX = os.path.join(os.path.dirname(__file__), "fixtures")

def load(name):
    with open(os.path.join(FIX, name), "r", encoding="utf-8") as f:
        return json.load(f)

def j_budget(spec):
    j = spec["j_metrics_impact"]
    return sum(abs(j[k]) for k in ["j1", "j2", "j3", "j4", "j5"])

def clamp01(x): 
    return max(0.0, min(1.0, x))

def apply_server_side_constraints(spec):
    # Physics clamp
    spec["energy_throttle"] = clamp01(spec.get("energy_throttle", 1.0))
    spec["hca_rings_affected"] = int(max(0, min(5, spec.get("hca_rings_affected", 0))))
    spec["temperature_increase"] = max(0.0, spec.get("temperature_increase", 0.0))

    # Ensure J fields exist
    spec.setdefault("j_metrics_impact", {})
    for k in ["j1","j2","j3","j4","j5"]:
        spec["j_metrics_impact"].setdefault(k, 0.0)

    # Budget rescale Σ|j_k| ≤ 2.0
    B = j_budget(spec)
    if B > 2.0 and B > 0:
        s = 2.0 / B
        for k in ["j1","j2","j3","j4","j5"]:
            spec["j_metrics_impact"][k] *= s

    # Ahimsa gate (Demo-Variante)
    if spec["j_metrics_impact"]["j5"] < -0.5:
        spec["energy_throttle"] = 0.0

    # Synchronous Growth pre-check (Demo-Variante)
    if spec.get("scm_delta", 0.0) <= 0.0 and spec["j_metrics_impact"]["j4"] > 0.0:
        spec["j_metrics_impact"]["j4"] = 0.0

    return spec

def test_physics_bounds_crisis():
    spec = load("crisis_mid.json")
    v = apply_server_side_constraints(spec)
    assert 0.0 <= v["energy_throttle"] <= 1.0
    assert 0 <= v["hca_rings_affected"] <= 5
    assert v["temperature_increase"] >= 0.0

def test_synchronous_growth_blocks_j4():
    spec = load("empowerment_without_coop.json")
    # künstlich J4 > 0 setzen um Blocking zu testen
    spec["j_metrics_impact"]["j4"] = 0.6
    v = apply_server_side_constraints(spec)
    assert v["scm_delta"] <= 0
    assert v["j_metrics_impact"]["j4"] == 0.0  # blockiert

def test_ahimsa_alarm_throttles_energy():
    spec = load("ahimsa_violation.json")
    v = apply_server_side_constraints(spec)
    assert v["j_metrics_impact"]["j5"] < -0.5
    assert v["energy_throttle"] == 0.0  # erzwungene Drossel

def test_budget_rescaling():
    spec = load("j_budget_over.json")
    v = apply_server_side_constraints(spec)
    assert pytest.approx(j_budget(v), rel=1e-9) <= 2.0

def test_tampering_flags_sha():
    spec = load("tampering.json")
    assert spec["sha_trigger"] is True
    assert spec["hca_rings_affected"] == 5
