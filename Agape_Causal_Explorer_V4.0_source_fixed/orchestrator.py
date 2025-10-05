import os
import json
import requests
import openai

SERVER = os.getenv("AGAPE_SERVER", "http://127.0.0.1:8000")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setze hier deinen ausführlichen System-Prompt ein (siehe 
# vorherige Antworten)
SYSTEM_PROMPT = "You are the Causal Mapping Engine (CME) for the Agape Causal Explorer..."

CREATE_CAUSAL_SPEC_TOOL = {
  "name": "create_causal_spec",
  "description": "Create a causally consistent intervention spec for the Agape Causal Explorer simulation.",
  "parameters": {
    "type": "object",
    "properties": {
      "nl_query": {"type": "string"}
    },
    "required": ["nl_query"]
  }
}

def ask_cme(nl_query: str):
    """Call LLM with function-calling. For demo, we only pass nl_query."""
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":nl_query}],
        functions=[CREATE_CAUSAL_SPEC_TOOL],
        function_call={"name":"create_causal_spec"}
    )
    args = resp["choices"][0]["message"]["function_call"]["arguments"]
    return json.loads(args)

def validate_on_server(spec: dict):
    r = requests.post(f"{SERVER}/api/causal/validate", json=spec, timeout=15)
    r.raise_for_status()
    return r.json()

def run_simulation(spec: dict):
    r = requests.post(f"{SERVER}/api/sim/run", json=spec, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    nl_query = input("Agape Causal Explorer > ").strip()
    if not nl_query:
        print("Bitte einen Was-wäre-wenn-Text eingeben.")
        return
    # Demo: wenn kein echtes LLM verfügbar, ersetze ask_cme durch Minimal-Stub:
    try:
        tool_args = ask_cme(nl_query)
    except Exception:
        # Fallback: minimaler Spec nur mit Query
        tool_args = {"nl_query": nl_query, "j_metrics_impact": {"j1":0,"j2":0,"j3":0,"j4":0,"j5":0}}

    if "error" in tool_args:
        print("[REJECTED]", tool_args["error"])
        return

    print("[CME Spec draft]", json.dumps(tool_args, indent=2, ensure_ascii=False))
    v = validate_on_server(tool_args)
    if not v.get("ok", False):
        print("[VALIDATION FAILED]", v)
        return

    spec = v["causal_spec"]
    print("[VALIDATED Spec]", json.dumps(spec, indent=2, ensure_ascii=False))
    sim = run_simulation(spec)
    print("[SIM TICKS] count:", len(sim.get("ticks", [])))
    if sim.get("ticks"):
        print("[LAST TICK]", json.dumps(sim["ticks"][-1], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
