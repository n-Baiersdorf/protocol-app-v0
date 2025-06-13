#!/usr/bin/env python3
"""
Protokoll-LLM App - Hauptanwendung
MVP Version für automatisierte LaTeX-Protokollerstellung
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import logging

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

# Datenbank-Modelle
class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    input_files = db.Column(db.JSON)  # Liste der Upload-Dateien
    generated_content = db.Column(db.Text)  # Generierter LaTeX-Inhalt
    protocol_metadata = db.Column(db.JSON)  # Zusätzliche Metadaten

# Routen
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