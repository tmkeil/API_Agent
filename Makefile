# ============================================================
# Windchill API + Frontend — Makefile
# ============================================================
# Hauptkommandos:
#   make up       - Alles starten (lokal, lädt override automatisch)
#   make up-prod  - Nur Basis-Compose (Produktion, ohne override)
#   make dev      - Nur Backend + Frontend lokal (ohne Docker)
#   make down     - Container stoppen
#   make build    - Container neu bauen
#   make logs     - Logs anzeigen

.PHONY: help up up-prod dev-hybrid down build logs dev dev-be dev-fe clean install

help:
	@echo "============================================================"
	@echo "  Windchill API + Frontend"
	@echo "============================================================"
	@echo ""
	@echo "Docker:"
	@echo "  make up          - Alle Container starten (lokal, mit override)"
	@echo "  make up-prod     - Alle Container starten (Produktion, ohne override)"
	@echo "  make dev-hybrid  - Frontend/Nginx in Docker, Backend auf Windows"
	@echo "  make down        - Container stoppen"
	@echo "  make build       - Container neu bauen + starten"
	@echo "  make logs        - Logs aller Container"
	@echo "  make logs-be     - Nur Backend-Logs"
	@echo "  make logs-fe     - Nur Frontend-Logs"
	@echo ""
	@echo "Lokal (ohne Docker):"
	@echo "  make install   - Dependencies installieren"
	@echo "  make dev       - Backend + Frontend parallel starten"
	@echo "  make dev-be    - Nur Backend starten"
	@echo "  make dev-fe    - Nur Frontend starten"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean     - Temporaere Dateien loeschen"
	@echo ""

# ============================================================
# Docker
# ============================================================

up:
	docker compose up -d --build
	@echo ""
	@echo "Modus:     Lokal (mit override)"
	@echo "Frontend:  http://localhost:5173"
	@echo "Backend:   http://localhost:8001"
	@echo "API Docs:  http://localhost:8001/docs"
	@echo "Nginx:     http://localhost"

up-prod:
	docker compose -f docker-compose.yml up -d --build
	@echo ""
	@echo "Modus:     Produktion (Bridge-Netzwerk)"
	@echo "Frontend:  http://localhost:5173"
	@echo "Backend:   http://localhost:8001"
	@echo "API Docs:  http://localhost:8001/docs"
	@echo "Nginx:     http://localhost"

dev-hybrid:
	@echo "Stoppe evtl. laufende Container..."
	docker compose down 2>/dev/null || true
	@echo ""
	@echo "Starte Frontend + Nginx in Docker..."
	WINDOWS_HOST_IP=$$(ip route | grep default | awk '{print $$3}') \
	  docker compose -f docker-compose.yml -f docker-compose.hybrid.yml up -d --build frontend nginx
	@echo ""
	@echo "============================================================"
	@echo "  Hybrid-Modus aktiv"
	@echo "============================================================"
	@echo "  Windows-Host: $$(ip route | grep default | awk '{print $$3}')"
	@echo "  Frontend (Docker):  http://localhost:5173"
	@echo "  Nginx    (Docker):  http://localhost"
	@echo ""
	@echo "  Backend muss auf Windows gestartet werden!"
	@echo "  Oeffne PowerShell und fuehre aus:"
	@echo ""
	@echo "    cd windchill-api"
	@echo "    pip install -r requirements.txt"
	@echo "    uvicorn api:app --host 0.0.0.0 --port 8001 --reload"
	@echo ""
	@echo "============================================================"

down:
	docker compose down

build:
	docker compose up -d --build

logs:
	docker compose logs -f

logs-be:
	docker compose logs -f backend

logs-fe:
	docker compose logs -f frontend

# ============================================================
# Lokal (ohne Docker)
# ============================================================

install:
	cd windchill-api && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
	cd windchill-frontend && npm install

dev-be:
	cd windchill-api && copy .env.example .env 2>NUL & .venv\Scripts\python api.py

dev-fe:
	cd windchill-frontend && npm run dev

dev:
	@echo "Starte Backend und Frontend..."
	@echo "Backend:  http://localhost:8001/docs"
	@echo "Frontend: http://localhost:5173"
	@start cmd /c "cd windchill-api && .venv\Scripts\python api.py"
	@cd windchill-frontend && npm run dev

# ============================================================
# Cleanup
# ============================================================

clean:
	@if exist windchill-api\__pycache__ rd /s /q windchill-api\__pycache__
	@if exist windchill-api\src\__pycache__ rd /s /q windchill-api\src\__pycache__
	@echo Cleaned.