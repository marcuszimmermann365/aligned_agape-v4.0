from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

router = APIRouter()

class CausalSpec(BaseModel):
    nl_query: str = Field(..., min_length=1)
    severity: float = 0.5
    gws_delta: float = 0.0
    energy_throttle: float = 1.0
    j_metrics_impact: Dict[str, float] = Field(
        default_factory=lambda: {"j1": 0.0, "j2": 0.0, "j3": 0.0, "j4": 0.0, "j5": 0.0}
    )
    scm_delta: float = 0.0
    hca_rings_affected: int = 0
    temperature_increase: float = 0.0
    sha_trigger: bool = False
    duration_steps: int = 100
    notes: Optional[str] = None

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

@router.post("/causal/validate")
async def validate_spec(spec: CausalSpec):
    """
    Minimal-Validator (Stub) für Demo & Tests:
    - Bereichsprüfung gws_delta
    - Clamping energy_throttle [0,1]
    - hca_rings_affected [0..5]
    - temperature_increase >= 0
    """
    if abs(spec.gws_delta) > 1.0:
        return {"ok": False, "error": "gws_delta außerhalb des Bereichs [-1, +1]."}

    spec.energy_throttle = _clamp(spec.energy_throttle, 0.0, 1.0)
    spec.hca_rings_affected = int(_clamp(spec.hca_rings_affected, 0, 5))
    spec.temperature_increase = max(0.0, spec.temperature_increase)

    # Stelle sicher, dass alle J-Felder vorhanden sind
    for k in ["j1","j2","j3","j4","j5"]:
        spec.j_metrics_impact.setdefault(k, 0.0)

    return {"ok": True, "causal_spec": spec.model_dump()}

@router.post("/sim/run")
async def run_simulation(spec: CausalSpec):
    """
    Einfache deterministische Simulation (für Tests):
    - GWS steigt linear mit gws_delta
    - Energie = energy_throttle konstant
    - Ringe: aktiv = 5 - hca_rings_affected
    - Temperatur = 300 + temperature_increase
    - j/scm/sha_state direkt aus Spec
    """
    steps = max(1, int(spec.duration_steps))
    ticks: List[Dict[str, Any]] = []
    base_gws = 1.0
    for t in range(steps):
        gws_t = base_gws + (t * spec.gws_delta / max(1, steps - 1))
        tick = {
            "step": t,
            "gws": gws_t,
            "energy": spec.energy_throttle,
            "rings": [1] * (5 - spec.hca_rings_affected) + [0] * spec.hca_rings_affected,
            "temperature": 300.0 + spec.temperature_increase,
            "j": spec.j_metrics_impact,
            "scm": spec.scm_delta,
            "sha_state": "TRIGGERED" if spec.sha_trigger else "OK"
        }
        ticks.append(tick)
    return {"ticks": ticks}
