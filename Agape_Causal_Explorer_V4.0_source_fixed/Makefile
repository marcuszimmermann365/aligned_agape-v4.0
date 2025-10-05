PYTHON      := python
PIP         := $(PYTHON) -m pip
UVICORN     := uvicorn
SERVER_MOD  := live_server:app
HOST        := 127.0.0.1
PORT        := 8000
VENV        := .venv
ACTIVATE    := source $(VENV)/bin/activate

.PHONY: help venv install run-server orchestrator test fmt lint all clean

help:
	@echo "Targets: venv, install, run-server, orchestrator, test, fmt, lint, all, clean"

venv:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP) install --upgrade pip

install: venv
	$(ACTIVATE) && $(PIP) install -r requirements.txt

run-server:
	$(ACTIVATE) && $(UVICORN) $(SERVER_MOD) --host $(HOST) --port $(PORT) --reload

orchestrator:
	$(ACTIVATE) && OPENAI_API_KEY=$$OPENAI_API_KEY AGAPE_SERVER=http://$(HOST):$(PORT) $(PYTHON) orchestrator.py

test:
	$(ACTIVATE) && pytest -q

fmt:
	$(ACTIVATE) && black .

lint:
	$(ACTIVATE) && flake8 .

all: fmt lint test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
