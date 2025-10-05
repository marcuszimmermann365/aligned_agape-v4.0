import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from new_api import router as api_router

app = FastAPI(title="Agape Causal Explorer V4.0")

# CORS offen für lokale Tests/Browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# --- globaler Simulationszustand ---
state = {
    "timestamp": time.time(),
    "gws": 1.0,
    "energy": 1.0,
    "rings": [1, 1, 1, 1, 1],
    "temperature": 300.0,
    "auth_status": False,
    "last_auth_result": None,
    "system_neutralized": False,
    "chronicle": []
}

# Agape-Dynamik (Stub-Werte; hier könnt ihr echte Dynamik ergänzen)
J = {"j1": 10.0, "j2": 0.0, "j3": 0.0, "j4": 10.0, "j5": 0.0}
SCM = 0.85
weights = {"j1": 0.18, "j2": 0.20, "j3": 0.22, "j4": 0.25, "j5": 0.15}

def _reset_internal_state():
    global state, J, SCM, weights
    state.update({
        "timestamp": time.time(),
        "gws": 1.0,
        "energy": 1.0,
        "rings": [1, 1, 1, 1, 1],
        "temperature": 300.0,
        "auth_status": False,
        "last_auth_result": None,
        "system_neutralized": False,
        "chronicle": []
    })
    J = {"j1": 10.0, "j2": 0.0, "j3": 0.0, "j4": 10.0, "j5": 0.0}
    SCM = 0.85
    weights = {"j1": 0.18, "j2": 0.20, "j3": 0.22, "j4": 0.25, "j5": 0.15}

@app.post("/api/system/reset")
async def system_reset():
    _reset_internal_state()
    return JSONResponse({
        "ok": True,
        "message": "Systemzustand zurückgesetzt.",
        "state": {
            "gws": state["gws"],
            "energy": state["energy"],
            "rings": state["rings"],
            "temperature": state["temperature"],
            "auth_status": state["auth_status"],
            "system_neutralized": state["system_neutralized"]
        },
        "agape": {
            "J": J,
            "SCM": SCM,
            "weights": weights
        }
    })

# API-Router (Validation/Simulation)
app.include_router(api_router, prefix="/api")
