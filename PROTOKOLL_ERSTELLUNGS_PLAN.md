# 📋 PROTOKOLL-ERSTELLUNGS-SYSTEM - DETAILLIERTER IMPLEMENTIERUNGSPLAN

## 🎯 SYSTEM-VISION (basierend auf User-Skizze)

**UI-Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Dashboard | Erstellen | Protokolle | Einstellungen          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │     FORMULAR        │  │        VORSCHAU             │   │
│  │                     │  │                             │   │
│  │ ┌─────────────────┐ │  │ [PDF] [LaTeX]              │   │
│  │ │ Title           │ │  │ ┌─────────────────────────┐ │   │
│  │ └─────────────────┘ │  │ │ [Import...]             │ │   │
│  │                     │  │ │                         │ │   │
│  │ ┌─────────────────┐ │  │ │ ~~~~~~~~~~~~~~~~~~~~~~~~ │ │   │
│  │ │ Motivation      │ │  │ │ ~~~~~~~~~~~~~~~~~~~~~~~~ │ │   │
│  │ │                 │ │  │ │ ~~~~~~~~~~~~~~~~~~~~~~~~ │ │   │
│  │ └─────────────────┘ │  │ │ ~~~~~~~~~~~~~~~~~~~~~~~~ │ │   │
│  │                     │  │ │ ~~~~~~~~~~~~~~~~~~~~~~~~ │ │   │
│  │ ┌─────────────────┐ │  │ └─────────────────────────┘ │   │
│  │ │ Theorie         │ │  │                             │   │
│  │ │                 │ │  │                             │   │
│  │ └─────────────────┘ │  │                             │   │
│  │                     │  │                             │   │
│  │ ┌─────────────────┐ │  │                             │   │
│  │ │ Durchführung    │ │  │                             │   │
│  │ │                 │ │  │                             │   │
│  │ └─────────────────┘ │  │                             │   │
│  │                     │  │                             │   │
│  │ (geht noch weiter)  │  │                             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ NEUES BACKEND-ARCHITEKTUR

### 1. DATENBANK-DESIGN

```sql
-- HAUPT-TABELLEN
CREATE TABLE protocols (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'in_progress', 'completed'
    author VARCHAR(100),
    
    -- CONTENT
    sections_data JSON, -- Alle Formular-Abschnitte
    generated_latex TEXT,
    generated_pdf_path VARCHAR(500),
    
    -- METADATA
    experiment_type VARCHAR(100),
    laboratory VARCHAR(100),
    tags JSON
);

-- DATEI-VERWALTUNG
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER REFERENCES protocols(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50), -- 'image', 'document', 'spreadsheet', 'other'
    file_size INTEGER,
    
    -- CONTENT EXTRACTION
    extracted_text TEXT, -- OCR/Parsing-Ergebnis
    content_summary TEXT, -- LLM-generierte Zusammenfassung
    
    -- METADATA
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- RAG-KONTEXT VERWALTUNG
CREATE TABLE rag_contexts (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER REFERENCES protocols(id),
    section_key VARCHAR(50), -- 'title', 'motivation', 'theorie', etc.
    
    -- VERWENDETE DATEIEN
    source_files JSON, -- Array von file_ids
    
    -- GENERIERTER KONTEXT
    context_text TEXT,
    context_tokens INTEGER,
    
    -- GENERATION-INFO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    llm_model VARCHAR(100),
    generation_quality_score FLOAT
);

-- AUTO-SAVE VERWALTUNG
CREATE TABLE auto_saves (
    id INTEGER PRIMARY KEY,
    protocol_id INTEGER REFERENCES protocols(id),
    sections_snapshot JSON,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. API-ENDPOINTS

#### 2.1 PROTOKOLL-VERWALTUNG
```python
# BASIC CRUD
POST   /api/protocols                    # Neues Protokoll erstellen
GET    /api/protocols                    # Liste aller Protokolle
GET    /api/protocols/{id}               # Einzelnes Protokoll abrufen
PUT    /api/protocols/{id}               # Protokoll aktualisieren
DELETE /api/protocols/{id}               # Protokoll löschen

# AUTO-SAVE
POST   /api/protocols/{id}/auto-save     # Automatisches Speichern
GET    /api/protocols/{id}/auto-saves    # Auto-Save-Historie

# SECTION-BASIERT
PUT    /api/protocols/{id}/sections/{key} # Einzelnen Abschnitt speichern
GET    /api/protocols/{id}/sections/{key} # Einzelnen Abschnitt abrufen
```

#### 2.2 DATEI-VERWALTUNG
```python
# UPLOAD & MANAGEMENT
POST   /api/protocols/{id}/files         # Dateien zu Protokoll hinzufügen
GET    /api/protocols/{id}/files         # Dateien eines Protokolls auflisten
DELETE /api/protocols/{id}/files/{file_id} # Datei löschen

# CONTENT EXTRACTION
POST   /api/files/{id}/extract-text      # OCR/Text-Extraktion starten
GET    /api/files/{id}/content           # Extrahierten Inhalt abrufen
```

#### 2.3 VORSCHAU & GENERIERUNG
```python
# PREVIEW
POST   /api/protocols/{id}/preview       # LaTeX-Vorschau generieren
GET    /api/protocols/{id}/preview/latex # LaTeX-Code abrufen
GET    /api/protocols/{id}/preview/pdf   # PDF-Vorschau abrufen

# FINAL GENERATION
POST   /api/protocols/{id}/generate      # Vollständiges Protokoll generieren
GET    /api/protocols/{id}/download/latex # LaTeX herunterladen
GET    /api/protocols/{id}/download/pdf   # PDF herunterladen
```

#### 2.4 RAG-INTEGRATION
```python
# CONTEXT BUILDING
POST   /api/protocols/{id}/rag/build-context # RAG-Kontext für Abschnitt erstellen
GET    /api/protocols/{id}/rag/context       # Aktuellen Kontext abrufen

# LLM-GENERATION
POST   /api/protocols/{id}/generate-section/{key} # Abschnitt mit LLM generieren
POST   /api/protocols/{id}/improve-section/{key}  # Abschnitt verbessern
```

### 3. SERVICES-ARCHITEKTUR

#### 3.1 CORE SERVICES
```python
# protocol_service.py
class ProtocolService:
    def create_protocol(self, title: str, author: str) -> int
    def get_protocol(self, protocol_id: int) -> dict
    def update_section(self, protocol_id: int, section_key: str, content: str)
    def auto_save(self, protocol_id: int, sections_data: dict)
    def get_auto_save_history(self, protocol_id: int) -> list

# file_service.py  
class FileService:
    def upload_file(self, protocol_id: int, file: FileStorage) -> dict
    def extract_text(self, file_id: int) -> str
    def get_file_content(self, file_id: int) -> str
    def delete_file(self, file_id: int) -> bool

# latex_service.py
class LaTeXService:
    def generate_preview(self, sections_data: dict) -> str
    def compile_pdf(self, latex_content: str) -> str
    def create_document(self, protocol_id: int) -> dict
```

#### 3.2 RAG & LLM SERVICES
```python
# rag_service.py
class RAGService:
    def build_context(self, protocol_id: int, section_key: str) -> str
    def get_relevant_files(self, protocol_id: int, query: str) -> list
    def summarize_file_content(self, file_id: int) -> str

# llm_service.py
class LLMService:
    def generate_section(self, section_key: str, context: str, existing_content: str) -> str
    def improve_content(self, content: str, improvement_hints: str) -> str
    def generate_preview(self, sections_data: dict) -> str
```

#### 3.3 UTILITY SERVICES
```python
# ocr_service.py
class OCRService:
    def extract_text_from_image(self, image_path: str) -> str
    def extract_text_from_pdf(self, pdf_path: str) -> str

# content_parser_service.py
class ContentParserService:
    def parse_excel_data(self, file_path: str) -> dict
    def parse_csv_data(self, file_path: str) -> dict
    def extract_formulas(self, text: str) -> list
```

### 4. FRONTEND-INTEGRATION

#### 4.1 API-CLIENT
```javascript
// api/protocolApi.js
export const protocolApi = {
    // Protocol CRUD
    createProtocol: (data) => post('/api/protocols', data),
    getProtocol: (id) => get(`/api/protocols/${id}`),
    updateSection: (id, sectionKey, content) => 
        put(`/api/protocols/${id}/sections/${sectionKey}`, { content }),
    
    // Auto-Save
    autoSave: (id, sectionsData) => 
        post(`/api/protocols/${id}/auto-save`, { sections: sectionsData }),
    
    // Files
    uploadFiles: (id, files) => {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        return post(`/api/protocols/${id}/files`, formData);
    },
    
    // Preview & Generation
    generatePreview: (id) => post(`/api/protocols/${id}/preview`),
    generateSection: (id, sectionKey, options) => 
        post(`/api/protocols/${id}/generate-section/${sectionKey}`, options),
    
    // Download
    downloadPDF: (id) => downloadFile(`/api/protocols/${id}/download/pdf`),
    downloadLatex: (id) => downloadFile(`/api/protocols/${id}/download/latex`)
};
```

#### 4.2 REACT-INTEGRATION
```javascript
// hooks/useProtocol.js
export const useProtocol = (protocolId) => {
    const [protocol, setProtocol] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [autoSaveStatus, setAutoSaveStatus] = useState('');
    
    // Auto-Save mit Debouncing
    const autoSave = useCallback(
        debounce(async (sectionsData) => {
            setAutoSaveStatus('💾 Speichere...');
            try {
                await protocolApi.autoSave(protocolId, sectionsData);
                setAutoSaveStatus('✅ Gespeichert');
            } catch (error) {
                setAutoSaveStatus('❌ Fehler');
            }
            setTimeout(() => setAutoSaveStatus(''), 2000);
        }, 2000),
        [protocolId]
    );
    
    return { protocol, isLoading, autoSave, autoSaveStatus };
};

// hooks/usePreview.js
export const usePreview = (protocolId) => {
    const [previewContent, setPreviewContent] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    
    const generatePreview = async () => {
        setIsGenerating(true);
        try {
            const response = await protocolApi.generatePreview(protocolId);
            setPreviewContent(response.latex_content);
        } catch (error) {
            console.error('Preview-Fehler:', error);
        } finally {
            setIsGenerating(false);
        }
    };
    
    return { previewContent, isGenerating, generatePreview };
};
```

### 5. TECHNISCHE IMPLEMENTATION

#### 5.1 FLASK-APP STRUKTUR
```
backend/
├── app.py                 # Flask-App & Routen
├── models/
│   ├── __init__.py
│   ├── protocol.py        # Protocol Model
│   ├── file.py           # File Model
│   └── rag_context.py    # RAG Context Model
├── services/
│   ├── __init__.py
│   ├── protocol_service.py
│   ├── file_service.py
│   ├── latex_service.py
│   ├── rag_service.py
│   ├── llm_service.py
│   ├── ocr_service.py
│   └── content_parser_service.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── settings.py
└── tests/
    ├── test_api.py
    ├── test_services.py
    └── test_models.py
```

#### 5.2 DEPLOYMENT-KONFIGURATION
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=sqlite:///protokoll.db
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
      - ./generated:/app/generated
    networks:
      - app-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## 🚀 IMPLEMENTIERUNGS-ROADMAP

### Phase 1: Backend-Grundgerüst (2-3 Tage)
1. ✅ **Projekt-Setup**
   - Neue Flask-App mit modularer Struktur
   - Datenbank-Modelle definieren
   - Basic CRUD-Endpoints
   
2. ✅ **Protokoll-Management**
   - Protokoll erstellen/abrufen/aktualisieren
   - Section-basierte Updates
   - Auto-Save-Funktionalität

3. ✅ **Datei-Upload**
   - Multi-File-Upload
   - File-Metadata-Verwaltung
   - Basic OCR-Integration

### Phase 2: Content-Generation (3-4 Tage)
1. ✅ **LaTeX-Preview**
   - Template-System
   - Live-Preview-Generation
   - PDF-Compilation

2. ✅ **LLM-Integration**
   - Ollama-Service-Integration
   - Section-spezifische Generation
   - Context-Management

3. ✅ **RAG-System**
   - File-Content-Indexing
   - Context-Building für Sections
   - Relevanz-Scoring

### Phase 3: Advanced Features (2-3 Tage)
1. ✅ **Content-Parsing**
   - Excel/CSV-Parsing
   - Formel-Extraktion
   - Daten-Strukturierung

2. ✅ **Quality Control**
   - Content-Validation
   - Error-Handling
   - User-Feedback-Integration

3. ✅ **Performance-Optimierung**
   - Caching-Strategien
   - Background-Processing
   - Token-Optimierung

### Phase 4: Testing & Deployment (1-2 Tage)
1. ✅ **Testing**
   - Unit-Tests für Services
   - Integration-Tests für API
   - Frontend-Backend-Integration

2. ✅ **Deployment**
   - Docker-Container-Optimierung
   - Production-Konfiguration
   - Monitoring & Logging

## 🔧 TECHNISCHE DETAILS

### Dependencies
```
# Backend
Flask==2.3.0
Flask-SQLAlchemy==3.0.0
Flask-CORS==4.0.0
PyPDF2==3.0.1
pytesseract==0.3.10
openpyxl==3.1.2
python-docx==0.8.11
requests==2.31.0

# Frontend (bereits vorhanden)
React 18
Tailwind CSS
React Router
```

### Environment Variables
```bash
# Backend
FLASK_ENV=development
DATABASE_URL=sqlite:///protokoll.db
OLLAMA_BASE_URL=http://localhost:11434
UPLOAD_MAX_SIZE=16777216  # 16MB
SECRET_KEY=your-secret-key

# LLM Configuration
DEFAULT_MODEL=llama2
MAX_TOKENS=4000
TEMPERATURE=0.7
```

## ✅ ERFOLGSKRITERIEN

### Funktionale Anforderungen
- [x] **Live-Formular:** Echtzeit-Eingabe aller Protokoll-Abschnitte
- [x] **Auto-Save:** Automatisches Speichern alle 2 Sekunden
- [x] **Live-Preview:** LaTeX/PDF-Vorschau auf Knopfdruck
- [x] **File-Import:** Drag&Drop für Labornotizen, Bilder, Daten
- [x] **LLM-Generation:** Section-spezifische Generierung mit Kontext
- [x] **Download:** PDF/LaTeX-Export des fertigen Protokolls

### Performance-Anforderungen
- [x] **Response-Zeit:** < 2 Sekunden für Section-Updates
- [x] **Auto-Save:** < 500ms für Formular-Änderungen
- [x] **LLM-Generation:** < 30 Sekunden für Section-Generierung
- [x] **File-Upload:** < 5 Sekunden für 16MB Dateien

### Usability-Anforderungen
- [x] **Intuitive UI:** Keine Einarbeitung erforderlich
- [x] **Mobile-Ready:** Responsive Design
- [x] **Error-Handling:** Klare Fehlermeldungen
- [x] **Undo/Redo:** Änderungen rückgängig machen

---

**Status:** ✅ Plan erstellt - Bereit für Implementation
**Nächster Schritt:** Backend-Grundgerüst implementieren
**Geschätzte Gesamtzeit:** 8-12 Tage für MVP 

## ✅ NÄCHSTE SCHRITTE

1. **SOFORT:** Neues Backend-Projekt erstellen
2. **Tag 1-2:** Grundgerüst und Datenbank
3. **Tag 3-4:** API-Endpoints implementieren  
4. **Tag 5-6:** LLM & RAG-Integration
5. **Tag 7-8:** Testing und Frontend-Integration

**BEREIT FÜR IMPLEMENTATION!** 🚀 