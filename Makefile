# Protokoll-LLM Makefile für einfache Projektoperationen

.PHONY: help setup start stop logs clean test build

# Hilfe anzeigen
help:
	@echo "🧪 Protokoll-LLM - Verfügbare Befehle:"
	@echo "  setup     - Projekt initialisieren"
	@echo "  start     - Alle Services starten"
	@echo "  stop      - Alle Services stoppen"
	@echo "  logs      - Logs anzeigen"
	@echo "  clean     - System bereinigen"
	@echo "  test      - Tests ausführen"
	@echo "  build     - Images neu erstellen"

# Projekt Setup
setup:
	@echo "🚀 Initialisiere Protokoll-LLM..."
	docker-compose up -d
	@echo "⏳ Warte auf Services..."
	sleep 30
	@echo "📥 Lade Ollama-Modell..."
	docker exec $$(docker-compose ps -q ollama) ollama pull llama2
	@echo "✅ Setup abgeschlossen!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:5000"

# Services starten
start:
	@echo "▶️  Starte alle Services..."
	docker-compose up -d
	@echo "✅ Services gestartet!"

# Services stoppen
stop:
	@echo "⏹️  Stoppe alle Services..."
	docker-compose down
	@echo "✅ Services gestoppt!"

# Logs anzeigen
logs:
	docker-compose logs -f

# System bereinigen
clean:
	@echo "🧹 Bereinige System..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ System bereinigt!"

# Tests ausführen
test:
	@echo "🧪 Führe Tests aus..."
	docker-compose exec backend python -m pytest tests/ -v
	docker-compose exec frontend npm test -- --watchAll=false
	@echo "✅ Tests abgeschlossen!"

# Images neu erstellen
build:
	@echo "🔨 Erstelle Images neu..."
	docker-compose build --no-cache
	@echo "✅ Images erstellt!"

# Development-Mode
dev:
	@echo "💻 Starte Development-Mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Nur Backend starten (für Frontend-Entwicklung)
backend-only:
	docker-compose up -d db ollama backend

# Nur Frontend starten (für Backend-Entwicklung)
frontend-only:
	docker-compose up -d frontend

# Gesundheitscheck
health:
	@echo "🏥 Prüfe Service-Status..."
	@curl -f http://localhost:5000/health || echo "❌ Backend nicht erreichbar"
	@curl -f http://localhost:3000 || echo "❌ Frontend nicht erreichbar"
	@curl -f http://localhost:11434/api/version || echo "❌ Ollama nicht erreichbar" 