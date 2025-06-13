# 🧪 Protokoll-LLM: Automatisierte Laborprotokoll-Erstellung

## 📋 Projektübersicht

Dieses Projekt entwickelt eine LLM-basierte Webanwendung zur automatisierten Erstellung professioneller LaTeX-Protokolle aus Versuchsanweisungen, Labornotizen und anderen Eingabedaten für die CTA-Ausbildung.

### 🎯 MVP-Funktionen

- ✅ **Datei-Upload**: Drag & Drop für Bilder, PDFs, Word-Dokumente
- ✅ **OCR-Integration**: Texterkennung aus handschriftlichen Notizen
- ✅ **LLM-Verarbeitung**: Ollama-Integration für Protokoll-Generierung
- ✅ **LaTeX-Export**: Professionelle PDF-Protokolle
- ✅ **Benutzeroberfläche**: Moderne React-Webapplikation

## 🏗️ Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │     Ollama      │
│   (Port 3000)   │◄──►│   (Port 5000)   │◄──►│   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   (Port 5432)   │
                       └─────────────────┘
```

### 🛠️ Technology Stack

**Backend:**
- Python 3.11 + Flask
- Ollama für LLM-Integration
- Tesseract OCR für Texterkennung
- PyLaTeX für PDF-Generierung
- PostgreSQL Datenbank

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS für Styling
- Axios für API-Kommunikation
- React Router für Navigation

**DevOps:**
- Docker & Docker Compose
- Multi-Container-Setup
- Hot Reload für Development

## 🚀 Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- Git
- 8GB+ RAM (für Ollama-Modelle)

### Installation

1. **Repository klonen:**
```bash
git clone <repository-url>
cd protocol-app-v0
```

2. **Services starten:**
```bash
docker-compose up -d
```

3. **Ollama-Modell laden:**
```bash
docker exec protocol-app-v0-ollama-1 ollama pull llama2
```

4. **Anwendung öffnen:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Gesundheitscheck: http://localhost:5000/health

### 📁 Projektstruktur

```
protocol-app-v0/
├── backend/                    # Flask-Backend
│   ├── services/              # Business Logic Services
│   │   ├── llm_service.py     # Ollama-Integration
│   │   ├── file_service.py    # Datei-Management
│   │   ├── ocr_service.py     # Texterkennung
│   │   └── latex_service.py   # PDF-Generierung
│   ├── app.py                 # Haupt-Flask-App
│   ├── requirements.txt       # Python-Dependencies
│   └── Dockerfile
├── frontend/                   # React-Frontend
│   ├── src/
│   │   ├── components/        # UI-Komponenten
│   │   ├── pages/            # Seiten-Komponenten
│   │   └── App.js            # Hauptanwendung
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml         # Multi-Service-Konfiguration
└── README.md
```

## 🔧 Entwicklung

### Backend entwickeln

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend entwickeln

```bash
cd frontend
npm install
npm start
```

### Services einzeln starten

```bash
# Nur Datenbank
docker-compose up db -d

# Backend mit lokaler Entwicklung
cd backend && python app.py

# Frontend mit lokaler Entwicklung
cd frontend && npm start
```

## 📖 API-Dokumentation

### Datei-Upload
```http
POST /upload
Content-Type: multipart/form-data

files: [File1, File2, ...]
```

### Protokoll-Generierung
```http
POST /generate
Content-Type: application/json

{
  "files": [...],
  "metadata": {
    "title": "Versuchsprotokoll",
    "author": "Max Mustermann",
    "experiment_type": "Säure-Base-Titration"
  }
}
```

### Protokoll-Liste
```http
GET /protocols
```

## 🎨 Benutzeroberfläche

Das Frontend bietet eine intuitive Benutzeroberfläche mit:

- **Dashboard**: Übersicht über aktuelle Protokolle
- **Upload**: Drag & Drop für Dateien mit Vorschau
- **Protokolle**: Verwaltung generierter Dokumente
- **Einstellungen**: LLM-Parameter und Templates

## 🔒 Konfiguration

### Umgebungsvariablen

```bash
# Backend
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@db:5432/protokoll_app
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# Frontend
REACT_APP_API_URL=http://localhost:5000
```

### Ollama-Modelle

Empfohlene Modelle für verschiedene Anwendungsfälle:

```bash
# Schnell und effizient (Standard)
ollama pull llama2:7b

# Höhere Qualität
ollama pull llama2:13b

# Speziell für deutsche Texte
ollama pull neural-chat:7b
```

## 🧪 Tests

```bash
# Backend-Tests
cd backend
python -m pytest tests/

# Frontend-Tests
cd frontend
npm test
```

## 📊 Monitoring

### Gesundheitschecks

- Backend: `GET /health`
- Frontend: React Development Server Status
- Ollama: `GET http://localhost:11434/api/version`

### Logs einsehen

```bash
# Alle Services
docker-compose logs -f

# Einzelner Service
docker-compose logs -f backend
```

## 🚧 Roadmap

### Phase 1: MVP (Aktuell)
- [x] Grundarchitektur
- [x] Datei-Upload
- [x] OCR-Integration
- [x] LLM-Basis-Integration
- [x] LaTeX-Generierung
- [ ] Frontend-Komponenten
- [ ] Integration-Tests

### Phase 2: Erweiterte Features
- [ ] Verbesserte Prompt-Engineering
- [ ] Template-System
- [ ] Batch-Processing
- [ ] Qualitätskontrolle

### Phase 3: Production-Ready
- [ ] Benutzer-Management
- [ ] API-Rate-Limiting
- [ ] Monitoring & Alerting
- [ ] Backup-Strategien

## 🤝 Beitragen

1. Fork des Repositories
2. Feature-Branch erstellen: `git checkout -b feature/amazing-feature`
3. Commits: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

Bei Fragen oder Problemen:

1. **Issues**: GitHub Issues für Bug-Reports
2. **Diskussionen**: GitHub Discussions für allgemeine Fragen
3. **Dokumentation**: [Ausführliche Docs](docs/) im `docs/`-Ordner

## 🏆 Credits

Entwickelt für die CTA-Ausbildung mit Fokus auf:
- Wissenschaftliche Genauigkeit
- Benutzerfreundlichkeit
- Lerneffekt-Erhaltung
- Professionelle Dokumentation

---

**Status**: 🚧 In Entwicklung (MVP Phase)
**Version**: 1.0.0-alpha
**Letztes Update**: $(date) 