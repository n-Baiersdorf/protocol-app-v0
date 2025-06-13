#!/usr/bin/env python3
"""
Test-Script für Ollama-Verbindung von Docker Container aus
"""

import requests
import json

def test_ollama_connection():
    test_urls = [
        'http://172.17.0.1:11434',
        'http://host.docker.internal:11434', 
        'http://localhost:11434',
        'http://172.18.0.1:11434',
        'http://192.168.65.2:11434'
    ]
    
    print("🔍 Teste Ollama-Verbindung von verschiedenen Adressen...")
    print()
    
    for url in test_urls:
        try:
            response = requests.get(f'{url}/api/version', timeout=3)
            if response.status_code == 200:
                version_info = response.json()
                print(f'✅ {url} - ERFOLGREICH!')
                print(f'   Version: {version_info.get("version", "unknown")}')
                
                # Teste auch Modell-Liste
                models_response = requests.get(f'{url}/api/tags', timeout=3)
                if models_response.status_code == 200:
                    models = models_response.json()
                    model_names = [m['name'] for m in models.get('models', [])]
                    print(f'   Modelle: {", ".join(model_names[:3])}{"..." if len(model_names) > 3 else ""}')
                
                return url  # Erste funktionierende URL zurückgeben
            else:
                print(f'❌ {url} - HTTP {response.status_code}')
                
        except requests.exceptions.Timeout:
            print(f'⏱️ {url} - Timeout')
        except requests.exceptions.ConnectionError:
            print(f'🔌 {url} - Verbindung fehlgeschlagen')
        except Exception as e:
            print(f'❌ {url} - Fehler: {str(e)[:50]}')
    
    print()
    print("❌ Keine funktionierende Ollama-Verbindung gefunden!")
    return None

if __name__ == "__main__":
    working_url = test_ollama_connection()
    if working_url:
        print(f"\n🎯 LÖSUNG: Verwende {working_url} in der Backend-Konfiguration")
    else:
        print("\n💡 Mögliche Lösungen:")
        print("   1. Ollama mit --host 0.0.0.0 starten")
        print("   2. Docker-Container im Host-Netzwerk ausführen")
        print("   3. Firewall-Einstellungen prüfen")

    test_urls = ['http://172.17.0.1:11434', 'http://host.docker.internal:11434', 'http://localhost:11434']
    print("🧪 TESTE OLLAMA-ZUGRIFF VOM BACKEND:")

    for url in test_urls:
        try:
            response = requests.get(f'{url}/api/version', timeout=2)
            if response.status_code == 200:
                print(f'✅ {url} - FUNKTIONIERT!')
                print(f'   Version: {response.json().get("version", "unknown")}')
                break
        except Exception as e:
            print(f'❌ {url} - {str(e)[:40]}...') 