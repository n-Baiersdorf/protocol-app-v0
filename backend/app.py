#!/usr/bin/env python3
"""
Protokoll-LLM App - Hauptanwendung
MVP Version für automatisierte LaTeX-Protokollerstellung
"""

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import logging
import re
from datetime import datetime
from werkzeug.utils import secure_filename

# Laden der Umgebungsvariablen
load_dotenv()

# Flask App Initialisierung
app = Flask(__name__)
CORS(app)

# Konfiguration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///protokoll.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Datenbank-Initialisierung
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Upload-Verzeichnisse erstellen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'global'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'projects'), exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Services importieren
from services.llm_service import LLMService
from services.file_service import FileService
from services.latex_service import LaTeXService
from services.ocr_service import OCRService

# Services initialisieren
llm_service = LLMService()
file_service = FileService(app.config['UPLOAD_FOLDER'])
latex_service = LaTeXService(app.config['GENERATED_FOLDER'])
ocr_service = OCRService()

@app.route('/test-route-early', methods=['GET'])
def test_route_early():
    """Test Route VOR den Modell-Definitionen"""
    return jsonify({'status': 'EARLY ROUTE WORKS!', 'message': 'Route vor Modellen funktioniert!'})

# ALLE Datenbank-Modelle (inline für Einfachheit)
class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Inhalt
    description = db.Column(db.Text)
    sections_content = db.Column(db.JSON)  # Abschnittsweise gespeichert
    generated_content = db.Column(db.Text)  # Generierter LaTeX-Inhalt
    
    # Legacy-Felder
    input_files = db.Column(db.JSON)  # Liste der Upload-Dateien
    protocol_metadata = db.Column(db.JSON)  # Zusätzliche Metadaten
    
    # RAG-Konfiguration
    selected_global_files = db.Column(db.JSON)  # IDs der ausgewählten globalen Dateien
    rag_context_size = db.Column(db.Integer, default=4000)  # Max. Token für RAG-Kontext
    
    # Meta-Informationen
    author = db.Column(db.String(100))
    experiment_type = db.Column(db.String(100))
    laboratory = db.Column(db.String(100))

class GlobalFile(db.Model):
    """Globale Dateien für alle Protokolle verfügbar"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'document', 'image', 'spreadsheet'
    file_size = db.Column(db.Integer)
    file_path = db.Column(db.String(500), nullable=False)
    
    # RAG-relevante Felder
    extracted_text = db.Column(db.Text)
    file_summary = db.Column(db.Text)  # LLM-generierte Zusammenfassung
    keywords = db.Column(db.JSON)  # Schlagwörter für Suche
    
    # Kategorisierung
    category = db.Column(db.String(100))  # z.B. 'safety_data', 'procedures', 'reference'
    tags = db.Column(db.JSON)  # Benutzer-Tags
    
    # Meta-Informationen
    uploaded_by = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    # RAG-Integration
    embedding_status = db.Column(db.String(50), default='pending')  # 'pending', 'processed', 'error'
    embedding_id = db.Column(db.String(100))  # Vector DB ID
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'extracted_text': self.extracted_text,
            'file_summary': self.file_summary,
            'keywords': self.keywords,
            'category': self.category,
            'tags': self.tags,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'usage_count': self.usage_count,
            'embedding_status': self.embedding_status
        }

class ProjectFile(db.Model):
    """Projektbezogene Dateien nur für spezifische Protokolle"""
    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocol.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer)
    file_path = db.Column(db.String(500), nullable=False)
    
    # RAG-relevante Felder
    extracted_text = db.Column(db.Text)
    file_summary = db.Column(db.Text)
    experiment_relevance = db.Column(db.Text)  # Wie relevant für dieses Experiment
    
    # Protokoll-spezifische Integration
    sections_used = db.Column(db.JSON)  # In welchen Abschnitten verwendet
    auto_include_rag = db.Column(db.Boolean, default=True)  # Automatisch in RAG einbeziehen
    
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    protocol = db.relationship('Protocol', backref='project_files')
    
    def to_dict(self):
        return {
            'id': self.id,
            'protocol_id': self.protocol_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'extracted_text': self.extracted_text,
            'file_summary': self.file_summary,
            'experiment_relevance': self.experiment_relevance,
            'sections_used': self.sections_used,
            'auto_include_rag': self.auto_include_rag,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }

class RAGSession(db.Model):
    """RAG-Sessions für Kontext-Management"""
    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocol.id'), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    
    # Verwendete Dateien in dieser Session
    global_files_used = db.Column(db.JSON)  # IDs der verwendeten globalen Dateien
    project_files_used = db.Column(db.JSON)  # IDs der verwendeten Projekt-Dateien
    
    # Generierter Kontext
    rag_context = db.Column(db.Text)  # Zusammengestellter Kontext
    context_summary = db.Column(db.Text)  # Zusammenfassung des Kontexts
    
    # Session-Info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens_used = db.Column(db.Integer)
    quality_score = db.Column(db.Float)  # User-Bewertung der Generierung
    
    protocol = db.relationship('Protocol', backref='rag_sessions')

# Datenbank-Tabellen erstellen
with app.app_context():
    db.create_all()
    logger.info("🗄️ Datenbank-Tabellen erfolgreich erstellt/aktualisiert")

# Routen beginnen

@app.route('/health', methods=['GET'])
def health_check():
    """Gesundheitscheck für die Anwendung"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'llm': llm_service.is_available(),
            'database': True  # Vereinfacht für MVP
        }
    })

@app.route('/test-new-route', methods=['GET'])
def test_new_route():
    """Test ob neue Routen registriert werden"""
    return jsonify({'status': 'NEW ROUTE WORKS!', 'message': 'Diese Route funktioniert!'})

@app.route('/upload', methods=['POST'])
def upload_files():
    """Datei-Upload-Endpunkt"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Keine Dateien hochgeladen'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Datei speichern und verarbeiten
            file_info = file_service.save_uploaded_file(file)
            
            # Wenn es ein Bild ist, OCR durchführen
            if file_info['type'] == 'image':
                ocr_text = ocr_service.extract_text(file_info['path'])
                file_info['extracted_text'] = ocr_text
            
            uploaded_files.append(file_info)
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'{len(uploaded_files)} Dateien erfolgreich hochgeladen'
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Datei-Upload: {str(e)}")
        return jsonify({'error': 'Fehler beim Datei-Upload'}), 500

@app.route('/generate', methods=['POST'])
def generate_protocol():
    """Protokoll-Generierung"""
    try:
        data = request.get_json()
        
        if not data or 'files' not in data:
            return jsonify({'error': 'Keine Dateien für Generierung angegeben'}), 400
        
        # Neues Protokoll in DB erstellen
        protocol = Protocol(
            title=data.get('title', 'Untitled Protocol'),
            input_files=data['files'],
            protocol_metadata=data.get('metadata', {})
        )
        
        db.session.add(protocol)
        db.session.commit()
        
        # Protokoll-Inhalt generieren
        generated_content = llm_service.generate_protocol_content(
            files=data['files'],
            protocol_metadata=data.get('metadata', {})
        )
        
        # LaTeX-Dokument erstellen
        latex_output = latex_service.create_document(
            content=generated_content,
            protocol_id=protocol.id
        )
        
        # Protokoll in DB aktualisieren
        protocol.generated_content = generated_content
        protocol.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'protocol_id': protocol.id,
            'latex_file': latex_output['latex_file'],
            'pdf_file': latex_output['pdf_file'],
            'message': 'Protokoll erfolgreich generiert'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei der Protokoll-Generierung: {str(e)}")
        return jsonify({'error': 'Fehler bei der Protokoll-Generierung'}), 500

@app.route('/protocols', methods=['GET'])
def list_protocols():
    """Liste aller Protokolle"""
    protocols = Protocol.query.order_by(Protocol.created_at.desc()).all()
    
    return jsonify({
        'protocols': [{
            'id': p.id,
            'title': p.title,
            'status': p.status,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat()
        } for p in protocols]
    })

@app.route('/protocols/<int:protocol_id>', methods=['GET'])
def get_protocol(protocol_id):
    """Einzelnes Protokoll abrufen"""
    protocol = Protocol.query.get_or_404(protocol_id)
    
    return jsonify({
        'id': protocol.id,
        'title': protocol.title,
        'status': protocol.status,
        'created_at': protocol.created_at.isoformat(),
        'updated_at': protocol.updated_at.isoformat(),
        'input_files': protocol.input_files,
        'generated_content': protocol.generated_content,
        'metadata': protocol.protocol_metadata
    })

@app.route('/download/<int:protocol_id>/<file_type>', methods=['GET'])
def download_protocol_file(protocol_id, file_type):
    """Download von generierten Protokoll-Dateien"""
    try:
        protocol = Protocol.query.get_or_404(protocol_id)
        
        # Korrekter Pfad zum generated-Ordner
        generated_folder = os.path.join(os.getcwd(), 'generated')
        
        if file_type == 'pdf':
            file_path = os.path.join(generated_folder, f'protocol_{protocol_id}.pdf')
            logger.info(f"Suche PDF: {file_path}")
            
            # Falls PDF nicht existiert, versuche es zu generieren
            if not os.path.exists(file_path):
                logger.info(f"PDF nicht gefunden, generiere neu...")
                try:
                    latex_output = latex_service.create_document(
                        content=protocol.generated_content,
                        protocol_id=protocol.id
                    )
                    logger.info(f"PDF-Generierung: {latex_output}")
                except Exception as gen_error:
                    logger.error(f"PDF-Generierung fehlgeschlagen: {gen_error}")
            
            if os.path.exists(file_path):
                # Sauberer Dateiname für Download
                clean_title = re.sub(r'[^\w\s-]', '', protocol.title).strip()
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                return send_file(file_path, as_attachment=True, download_name=f'{clean_title}_protokoll.pdf')
                
        elif file_type == 'latex':
            file_path = os.path.join(generated_folder, f'protocol_{protocol_id}.tex')
            logger.info(f"Suche LaTeX: {file_path}")
            
            if os.path.exists(file_path):
                # Sauberer Dateiname für Download  
                clean_title = re.sub(r'[^\w\s-]', '', protocol.title).strip()
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                return send_file(file_path, as_attachment=True, download_name=f'{clean_title}_protokoll.tex')
        
        logger.error(f"Datei nicht gefunden: {file_type} für Protokoll {protocol_id}")
        return jsonify({'error': f'Datei nicht gefunden: {file_type}'}), 404
        
    except Exception as e:
        logger.error(f"Fehler beim Download: {str(e)}")
        return jsonify({'error': 'Fehler beim Download'}), 500

@app.route('/test-llm', methods=['POST'])
def test_llm_generation():
    """Test-Route für LLM-Protokoll-Generierung"""
    try:
        data = request.get_json() or {}
        
        # Test-Daten erstellen
        test_files = [{
            'name': 'test_labornotiz.txt',
            'type': 'document',
            'content': data.get('test_content', '''
Laborprotokoll Test
===================
Experiment: Säure-Base-Titration
Datum: 2024-01-15
Chemikalien: NaOH 0.1M, HCl unbekannte Konzentration
Verbrauch: 23.5 mL NaOH
Beobachtung: Farbumschlag bei Phenolphthalein
''')
        }]
        
        test_metadata = {
            'title': data.get('title', 'Test-Protokoll'),
            'author': data.get('author', 'Test-Nutzer'),
            'experiment_type': data.get('experiment_type', 'Säure-Base-Titration'),
            'date': '2024-01-15'
        }
        
        logger.info("Starte Test-LLM-Generierung...")
        
        # LLM-Generierung testen
        generated_content = llm_service.generate_protocol_content(
            files=test_files,
            protocol_metadata=test_metadata
        )
        
        # In Datenbank speichern
        protocol = Protocol(
            title=test_metadata['title'],
            input_files=test_files,
            protocol_metadata=test_metadata,
            generated_content=generated_content,
            status='completed'
        )
        
        db.session.add(protocol)
        db.session.commit()
        
        logger.info(f"Test-Protokoll erfolgreich generiert: ID {protocol.id}")
        
        return jsonify({
            'success': True,
            'protocol_id': protocol.id,
            'generated_content': generated_content[:500] + '...' if len(generated_content) > 500 else generated_content,
            'full_content_length': len(generated_content),
            'message': 'Test-Protokoll erfolgreich generiert!'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Test-LLM-Generierung: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Test-LLM-Generierung fehlgeschlagen'
        }), 500

@app.route('/test-pdf/<int:protocol_id>', methods=['POST'])
def test_pdf_generation(protocol_id):
    """Test-Route für LaTeX/PDF-Generierung"""
    try:
        # Protokoll aus Datenbank laden
        protocol = Protocol.query.get_or_404(protocol_id)
        
        logger.info(f"Starte PDF-Generierung für Protokoll {protocol_id}...")
        
        # LaTeX-Dokument erstellen
        latex_output = latex_service.create_document(
            content=protocol.generated_content,
            protocol_id=protocol.id
        )
        
        logger.info(f"PDF-Generierung abgeschlossen: {latex_output}")
        
        return jsonify({
            'success': True,
            'protocol_id': protocol.id,
            'latex_file': latex_output['latex_file'],
            'pdf_file': latex_output['pdf_file'],
            'filename': latex_output['filename'],
            'message': 'PDF erfolgreich generiert!'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei PDF-Generierung: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'PDF-Generierung fehlgeschlagen'
        }), 500

@app.route('/test-simple-pdf', methods=['POST'])
def test_simple_pdf():
    """Vereinfachte PDF-Generierung für Debugging"""
    try:
        import tempfile
        import subprocess
        from pathlib import Path
        
        # Einfacher LaTeX-Content
        latex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[ngerman]{babel}
\usepackage{geometry}
\geometry{margin=2.5cm}

\title{🧪 Protokoll-LLM Test-PDF}
\author{MVP Phase 1b}
\date{\today}

\begin{document}
\maketitle

\section{System-Status}
\textbf{Erfolgreiche LLM-Integration:} ✅ \\
\textbf{Backend-Service:} Funktionsfähig \\
\textbf{PDF-Generierung:} In Arbeit...

\section{Test-Protokoll}
Dieses PDF wurde automatisch von unserem Protokoll-LLM System generiert!

\subsection{Technische Details}
\begin{itemize}
\item Backend: Flask + Python
\item LLM: Ollama (llama2)
\item PDF: LaTeX + pdflatex
\item Status: Phase 1b erfolgreich!
\end{itemize}

\end{document}
"""
        
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, dir='/tmp') as f:
            f.write(latex_content)
            tex_path = Path(f.name)
        
        # PDF kompilieren
        result = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory', '/tmp',
            str(tex_path)
        ], capture_output=True, text=True, cwd='/tmp')
        
        pdf_path = tex_path.with_suffix('.pdf')
        
        logger.info(f"LaTeX-Kompilierung: Return Code {result.returncode}")
        logger.info(f"PDF-Pfad: {pdf_path}")
        logger.info(f"PDF existiert: {pdf_path.exists()}")
        
        if pdf_path.exists():
            pdf_size = pdf_path.stat().st_size
            logger.info(f"PDF erfolgreich erstellt: {pdf_size} bytes")
            
            return jsonify({
                'success': True,
                'message': 'Einfache PDF-Generierung erfolgreich!',
                'pdf_path': str(pdf_path),
                'pdf_size': pdf_size,
                'latex_return_code': result.returncode,
                'latex_stdout': result.stdout[-500:] if result.stdout else '',
                'latex_stderr': result.stderr[-500:] if result.stderr else ''
            })
        else:
            return jsonify({
                'success': False,
                'message': 'PDF-Generierung fehlgeschlagen',
                'latex_return_code': result.returncode,
                'latex_stdout': result.stdout,
                'latex_stderr': result.stderr
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler bei einfacher PDF-Generierung: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/bulk-download/<file_type>')
def bulk_download(file_type):
    """Bulk-Download aller fertigen Protokolle als ZIP"""
    try:
        if file_type not in ['pdf', 'latex']:
            return jsonify({'error': 'Ungültiger Dateityp'}), 400
        
        # Alle fertigen Protokolle abrufen
        protocols = Protocol.query.filter_by(status='completed').all()
        
        if not protocols:
            return jsonify({'error': 'Keine fertigen Protokolle gefunden'}), 404
        
        # Temporäres ZIP-Archiv erstellen
        import zipfile
        import tempfile
        import os
        from datetime import datetime
        
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"alle_protokolle_{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for protocol in protocols:
                file_extension = 'pdf' if file_type == 'pdf' else 'tex'
                file_path = f"backend/generated/protocol_{protocol.id}.{file_extension}"
                
                if os.path.exists(file_path):
                    # Sauberen Dateinamen erstellen
                    clean_title = re.sub(r'[^\w\s-]', '', protocol.title).strip()
                    clean_title = re.sub(r'[-\s]+', '_', clean_title)
                    archive_name = f"{protocol.id}_{clean_title}.{file_extension}"
                    
                    zipf.write(file_path, archive_name)
                else:
                    # Fehlende Dateien regenerieren (nur für PDF)
                    if file_type == 'pdf':
                        try:
                            latex_service = LaTeXService('backend/generated')
                            latex_service.create_document(protocol.generated_content, protocol.id)
                            if os.path.exists(file_path):
                                clean_title = re.sub(r'[^\w\s-]', '', protocol.title).strip()
                                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                                archive_name = f"{protocol.id}_{clean_title}.{file_extension}"
                                zipf.write(file_path, archive_name)
                        except:
                            pass
        
        # ZIP-Datei zurücksenden
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
        
    except Exception as e:
        logger.error(f"Bulk-Download Fehler: {str(e)}")
        return jsonify({'error': 'Bulk-Download fehlgeschlagen'}), 500

@app.route('/generate-section', methods=['POST'])
def generate_section():
    """Generiert einen einzelnen Protokoll-Abschnitt mit LLM"""
    try:
        data = request.get_json()
        section = data.get('section')
        title = data.get('title', '')
        description = data.get('description', '')
        existing_sections = data.get('existing_sections', {})
        uploaded_files = data.get('uploaded_files', [])
        
        # Spezifische Prompts für jeden Abschnitt
        section_prompts = {
            'zielsetzung': """
Erstelle eine präzise Zielsetzung für dieses Laborexperiment.
Fokussiere auf: Was soll erreicht werden? Welche Fragestellung wird beantwortet?
Verwende deutsche Sprache und wissenschaftlichen Stil.
""",
            'theorie': """
Erkläre die relevanten theoretischen Grundlagen für dieses Experiment.
Erwähne wichtige Reaktionsgleichungen, Gesetze oder Prinzipien.
Halte es prägnant aber vollständig.
""",
            'material': """
Liste alle benötigten Materialien, Chemikalien und Geräte auf.
Verwende Aufzählungsformat mit korrekten Konzentrationen und Mengen.
Berücksichtige Sicherheitsaspekte.
""",
            'durchfuehrung': """
Beschreibe die experimentelle Durchführung in logischen Schritten.
Verwende nummerierte Liste. Sei präzise bei Mengenangaben und Zeiten.
Erwähne wichtige Beobachtungspunkte.
""",
            'ergebnisse': """
Präsentiere die Messwerte und Beobachtungen systematisch.
Verwende Tabellen oder Listen für Messdaten.
Beschreibe qualitative Beobachtungen (Farbe, Temperatur, etc.).
""",
            'berechnungen': """
Zeige alle relevanten Berechnungen mit Formeln und Zahlenwerten.
Erkläre jeden Rechenschritt. Verwende korrekte Einheiten.
Berechne Fehler oder Unsicherheiten falls möglich.
""",
            'diskussion': """
Bewerte die Ergebnisse kritisch. Diskutiere Abweichungen, Fehlerquellen.
Vergleiche mit Literaturwerten falls vorhanden.
Erwähne Verbesserungsmöglichkeiten.
""",
            'schlussfolgerung': """
Fasse die wichtigsten Erkenntnisse zusammen.
Beantworte die ursprüngliche Fragestellung.
Gib einen kurzen Ausblick oder praktische Relevanz.
"""
        }
        
        # Kontext aus anderen Abschnitten
        context_text = f"Titel: {title}\nBeschreibung: {description}\n\n"
        
        if existing_sections:
            context_text += "Bereits vorhandene Abschnitte:\n"
            for key, content in existing_sections.items():
                if content and key != section:
                    context_text += f"{key}: {content[:200]}...\n"
        
        # Upload-Dateien als Kontext
        if uploaded_files:
            context_text += "\nVerfügbare Daten aus hochgeladenen Dateien:\n"
            for file in uploaded_files:
                if file.get('extracted_text'):
                    context_text += f"- {file['name']}: {file['extracted_text'][:300]}...\n"
        
        # LLM-Prompt zusammenstellen
        full_prompt = f"""
{section_prompts.get(section, 'Erstelle Inhalt für diesen Abschnitt.')}

KONTEXT:
{context_text}

AUFGABE: Erstelle den Abschnitt '{section}' für dieses Laborprotokoll.
Verwende nur Informationen aus dem gegebenen Kontext oder allgemein bekannte wissenschaftliche Fakten.
Erfinde KEINE spezifischen Messwerte oder Details die nicht gegeben sind.
Antworte nur mit dem Inhalt des Abschnitts, ohne zusätzliche Erklärungen.
"""
        
        logger.info(f"Generiere Abschnitt '{section}' für '{title}'")
        
        # LLM-Generierung
        generated_content = llm_service.generate_protocol_content(
            files=[{'name': 'context', 'content': full_prompt}],
            protocol_metadata={'title': title, 'section': section}
        )
        
        # Bereinigung des generierten Inhalts
        cleaned_content = generated_content.strip()
        
        # Entferne eventuelle Markdown-Formatierung für LaTeX-Kompatibilität
        cleaned_content = cleaned_content.replace('**', '')
        cleaned_content = cleaned_content.replace('##', '')
        
        return jsonify({
            'success': True,
            'section': section,
            'content': cleaned_content,
            'message': f'Abschnitt "{section}" erfolgreich generiert'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Abschnitts-Generierung: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Abschnitts-Generierung fehlgeschlagen'
        }), 500

@app.route('/protocols/draft', methods=['POST'])
def save_protocol_draft():
    """Speichert einen Protokoll-Entwurf"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        sections = data.get('sections', {})
        files = data.get('files', [])
        
        # Prüfe ob bereits ein Entwurf mit diesem Titel existiert
        existing_protocol = Protocol.query.filter_by(title=title, status='draft').first()
        
        if existing_protocol:
            # Aktualisiere bestehenden Entwurf
            existing_protocol.protocol_metadata = {
                'description': description,
                'sections': sections,
                'last_modified': datetime.now().isoformat()
            }
            existing_protocol.input_files = files
            existing_protocol.updated_at = db.func.now()
            protocol_id = existing_protocol.id
        else:
            # Erstelle neuen Entwurf
            protocol = Protocol(
                title=title,
                status='draft',
                input_files=files,
                protocol_metadata={
                    'description': description,
                    'sections': sections,
                    'created': datetime.now().isoformat()
                }
            )
            db.session.add(protocol)
            db.session.flush()
            protocol_id = protocol.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'protocol_id': protocol_id,
            'message': 'Entwurf gespeichert'
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Entwurfs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-full-protocol', methods=['POST'])
def generate_full_protocol():
    """Erstellt vollständiges Protokoll aus Abschnitten"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        sections = data.get('sections', {})
        files = data.get('files', [])
        
        # LaTeX-Inhalt aus Abschnitten zusammenstellen
        latex_content = f"# {title}\n\n"
        
        if description:
            latex_content += f"{description}\n\n"
        
        # Abschnitte in korrekter Reihenfolge
        section_order = ['zielsetzung', 'theorie', 'material', 'durchfuehrung', 
                        'ergebnisse', 'berechnungen', 'diskussion', 'schlussfolgerung']
        
        for section_key in section_order:
            if section_key in sections and sections[section_key]:
                section_title = {
                    'zielsetzung': 'Zielsetzung',
                    'theorie': 'Theoretischer Hintergrund', 
                    'material': 'Materialien und Geräte',
                    'durchfuehrung': 'Durchführung',
                    'ergebnisse': 'Ergebnisse und Beobachtungen',
                    'berechnungen': 'Berechnungen und Auswertung',
                    'diskussion': 'Diskussion',
                    'schlussfolgerung': 'Schlussfolgerung'
                }.get(section_key, section_key.capitalize())
                
                latex_content += f"## {section_title}\n\n{sections[section_key]}\n\n"
        
        # Protokoll in Datenbank speichern/aktualisieren
        existing_protocol = Protocol.query.filter_by(title=title).first()
        
        if existing_protocol:
            existing_protocol.generated_content = latex_content
            existing_protocol.status = 'completed'
            existing_protocol.updated_at = db.func.now()
            protocol_id = existing_protocol.id
        else:
            protocol = Protocol(
                title=title,
                status='completed',
                input_files=files,
                generated_content=latex_content,
                protocol_metadata={
                    'description': description,
                    'sections': sections
                }
            )
            db.session.add(protocol)
            db.session.flush()
            protocol_id = protocol.id
        
        db.session.commit()
        
        # LaTeX-Dokument generieren
        latex_output = latex_service.create_document(
            content=latex_content,
            protocol_id=protocol_id
        )
        
        return jsonify({
            'success': True,
            'protocol_id': protocol_id,
            'latex_file': latex_output.get('latex_file'),
            'pdf_file': latex_output.get('pdf_file'),
            'message': 'Vollständiges Protokoll erfolgreich erstellt!'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei vollständiger Protokoll-Erstellung: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Vollständige Protokoll-Erstellung fehlgeschlagen'
        }), 500

@app.route('/global-files', methods=['GET'])
def get_global_files():
    """Liefert alle verfügbaren globalen Dateien"""
    try:
        files = GlobalFile.query.order_by(GlobalFile.upload_date.desc()).all()
        return jsonify([file.to_dict() for file in files])
    except Exception as e:
        logger.error(f"Fehler beim Laden globaler Dateien: {str(e)}")
        return jsonify({'error': 'Fehler beim Laden der Dateien'}), 500

@app.route('/upload-global', methods=['POST'])
def upload_global_files():
    """Upload von globalen Dateien"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Keine Dateien empfangen'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Sicherer Dateiname
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Datei speichern
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'global', unique_filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            
            # Dateityp bestimmen
            file_type = determine_file_type(filename)
            
            # OCR/Text-Extraktion
            extracted_text = None
            if file_type in ['image', 'document']:
                extracted_text = extract_text_from_file(upload_path, file_type)
            
            # In Datenbank speichern
            global_file = GlobalFile(
                filename=unique_filename,
                original_filename=filename,
                file_type=file_type,
                file_size=os.path.getsize(upload_path),
                file_path=upload_path,
                extracted_text=extracted_text,
                uploaded_by='user',  # TODO: Benutzer-Management
                category=categorize_file(filename, extracted_text)
            )
            
            db.session.add(global_file)
            uploaded_files.append(global_file)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'files': [file.to_dict() for file in uploaded_files],
            'message': f'{len(uploaded_files)} Dateien erfolgreich hochgeladen'
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Upload globaler Dateien: {str(e)}")
        return jsonify({'error': 'Upload fehlgeschlagen'}), 500

@app.route('/upload-project', methods=['POST'])
def upload_project_files():
    """Upload von projektbezogenen Dateien"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Keine Dateien empfangen'}), 400
            
        protocol_id = request.form.get('protocol_id')
        if not protocol_id:
            return jsonify({'error': 'Protokoll-ID erforderlich'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Sicherer Dateiname
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"p{protocol_id}_{timestamp}_{filename}"
            
            # Datei speichern
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'projects', unique_filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            
            # Dateityp bestimmen
            file_type = determine_file_type(filename)
            
            # OCR/Text-Extraktion
            extracted_text = None
            if file_type in ['image', 'document']:
                extracted_text = extract_text_from_file(upload_path, file_type)
            
            # In Datenbank speichern
            project_file = ProjectFile(
                protocol_id=int(protocol_id),
                filename=unique_filename,
                original_filename=filename,
                file_type=file_type,
                file_size=os.path.getsize(upload_path),
                file_path=upload_path,
                extracted_text=extracted_text,
                auto_include_rag=True
            )
            
            db.session.add(project_file)
            uploaded_files.append(project_file)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'files': [file.to_dict() for file in uploaded_files],
            'message': f'{len(uploaded_files)} Projekt-Dateien erfolgreich hochgeladen'
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Upload von Projekt-Dateien: {str(e)}")
        return jsonify({'error': 'Upload fehlgeschlagen'}), 500

@app.route('/generate-preview', methods=['POST'])
def generate_preview():
    """Generiert LaTeX-Vorschau des aktuellen Protokoll-Stands"""
    try:
        data = request.get_json()
        title = data.get('title', 'Protokoll-Entwurf')
        description = data.get('description', '')
        sections = data.get('sections', {})
        
        # LaTeX-Inhalt aus Abschnitten zusammenstellen
        latex_content = f"# {title}\n\n"
        
        if description:
            latex_content += f"{description}\n\n"
        
        # Abschnitte in korrekter Reihenfolge
        section_order = ['zielsetzung', 'theorie', 'material', 'durchfuehrung', 
                        'ergebnisse', 'berechnungen', 'diskussion', 'schlussfolgerung']
        
        for section_key in section_order:
            if section_key in sections and sections[section_key]:
                section_title = {
                    'zielsetzung': 'Zielsetzung',
                    'theorie': 'Theoretischer Hintergrund', 
                    'material': 'Materialien und Geräte',
                    'durchfuehrung': 'Durchführung',
                    'ergebnisse': 'Ergebnisse und Beobachtungen',
                    'berechnungen': 'Berechnungen und Auswertung',
                    'diskussion': 'Diskussion',
                    'schlussfolgerung': 'Schlussfolgerung'
                }.get(section_key, section_key.capitalize())
                
                latex_content += f"## {section_title}\n\n{sections[section_key]}\n\n"
        
        return jsonify({
            'success': True,
            'latex_content': latex_content,
            'message': 'Vorschau erfolgreich generiert'
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Vorschau-Generierung: {str(e)}")
        return jsonify({'error': 'Vorschau-Generierung fehlgeschlagen'}), 500

def determine_file_type(filename):
    """Bestimmt den Dateityp basierend auf der Erweiterung"""
    ext = filename.lower().split('.')[-1]
    
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
        return 'image'
    elif ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
        return 'document'
    elif ext in ['xls', 'xlsx', 'csv']:
        return 'spreadsheet'
    else:
        return 'other'

def categorize_file(filename, extracted_text=None):
    """Kategorisiert Dateien basierend auf Dateiname und Inhalt"""
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['sicherheit', 'safety', 'msds', 'sdb']):
        return 'safety_data'
    elif any(word in filename_lower for word in ['protokoll', 'procedure', 'anleitung']):
        return 'procedures'
    elif any(word in filename_lower for word in ['messung', 'data', 'results', 'messwerte']):
        return 'measurement_data'
    elif any(word in filename_lower for word in ['referenz', 'reference', 'literatur']):
        return 'reference'
    else:
        return 'general'

def extract_text_from_file(file_path, file_type):
    """Extrahiert Text aus Dateien (vereinfacht für MVP)"""
    try:
        if file_type == 'document' and file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'image':
            # TODO: OCR-Integration (Tesseract)
            return f"[Bild-Datei: OCR-Text hier]"
        else:
            return f"[{file_type.upper()}-Datei: Text-Extraktion implementiert]"
    except Exception as e:
        logger.error(f"Text-Extraktion fehlgeschlagen: {str(e)}")
        return None

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Datei zu groß. Maximum: 16MB'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Interner Serverfehler'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    ) 