#!/bin/bash

echo "🔧 Repariere Protokoll-LLM Setup..."

# Alte Container stoppen und entfernen
echo "⏹️  Stoppe alle Container..."
docker-compose down

# Prüfe ob Ollama bereits läuft
echo "🔍 Prüfe Ollama-Status..."
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama läuft bereits auf localhost:11434"
    echo "📋 Verfügbare Modelle:"
    curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "Keine Modelle gefunden"
    echo "ℹ️  Backend wird sich über 172.17.0.1:11434 verbinden"
else
    echo "❌ Ollama nicht erreichbar auf localhost:11434"
    echo "Starte Ollama mit: ollama serve"
    exit 1
fi

# Nur Backend und Frontend starten (ohne Ollama-Container)
echo "🚀 Starte Backend und Frontend..."
docker-compose up -d backend frontend db

# Warten bis Services bereit sind
echo "⏳ Warte auf Services..."
sleep 10

# Gesundheitscheck
echo "🏥 Prüfe Service-Status..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend läuft: http://localhost:5000"
else
    echo "❌ Backend-Problem - prüfe Logs mit: docker-compose logs backend"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend läuft: http://localhost:3000"
else
    echo "❌ Frontend-Problem - prüfe Logs mit: docker-compose logs frontend"
fi

# Stelle sicher, dass benötigte Modelle vorhanden sind
echo "📥 Prüfe Ollama-Modelle..."
if ! curl -s http://localhost:11434/api/tags | grep -q "llama2"; then
    echo "⬇️  Lade llama2 Modell..."
    ollama pull llama2
fi

echo "✅ Setup-Reparatur abgeschlossen!"
echo "🌐 Anwendung verfügbar unter: http://localhost:3000"
echo "🔧 API-Dokumentation: http://localhost:5000/health" 