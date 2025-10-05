# Agape Causal Explorer – V4.0

Vom Live-Demonstrator (V3.0) zum **Agape Causal Explorer** mit:
- **CME (Causal Mapping Engine)** via LLM Function-Calling
- **Constraints/Validation**
- **Experten-Panel** (Radar J1–J5) & Reset-Endpoint
- **Tests** (Unit/Property + Server-Contracts)

## Quickstart

```bash
# 1) Setup
python -m venv .venv
source .venv/bin/activate         # 
Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Server starten
uvicorn live_server:app --host 127.0.0.1 --port 8000 --reload

# 3) Dashboard öffnen
# Öffne die Datei ./dashboard.html im Browser (lokal laden reicht).

# 4) Tests
pytest -q
```

### Orchestrator (optional)

Für die LLM/CME-Pipeline: 

```bash
export OPENAI_API_KEY=sk-...
python orchestrator.py
# Eingabe: "Was wäre wenn eine globale Krise mittlerer Stärke passiert?"
```
Struktur 

```
Agape_Causal_Explorer_V4.0/
│-- README.md
│-- requirements.txt
│-- Makefile
│-- schema.json
│-- live_server.py
│-- new_api.py
│-- orchestrator.py
│-- dashboard.html
└── tests/
    │-- test_cme_constraints.py
    │-- test_server_contracts.py
    └── fixtures/
        │-- crisis_mid.json
        │-- empowerment_without_coop.json
        │-- tampering.json
        │-- ahimsa_violation.json
        └── j_budget_over.json
```
