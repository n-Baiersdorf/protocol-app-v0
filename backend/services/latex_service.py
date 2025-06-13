"""
LaTeX Service - Generiert professionelle Laborprotokolle im LaTeX/PDF-Format
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from pylatex import Document, Section, Subsection, Command, Package
from pylatex.base_classes import Environment
from pylatex.utils import NoEscape

logger = logging.getLogger(__name__)

class LaTeXService:
    """Service für LaTeX-Dokumenterstellung und PDF-Generierung"""
    
    def __init__(self, output_folder: str):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        
        # LaTeX-Templates-Ordner
        self.templates_folder = self.output_folder / 'templates'
        self.templates_folder.mkdir(exist_ok=True)
        
        # Prüfen ob LaTeX verfügbar ist
        self._check_latex_installation()
    
    def _check_latex_installation(self):
        """Prüft die LaTeX-Installation"""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("LaTeX erfolgreich erkannt")
            else:
                logger.warning("LaTeX möglicherweise nicht verfügbar")
        except FileNotFoundError:
            logger.error("LaTeX nicht installiert")
            raise RuntimeError("LaTeX ist nicht installiert")
    
    def create_document(self, content: str, protocol_id: int) -> Dict:
        """
        Erstellt ein LaTeX-Dokument und PDF
        
        Args:
            content: Generierter Protokoll-Inhalt
            protocol_id: ID des Protokolls
            
        Returns:
            Dict mit Pfaden zu LaTeX- und PDF-Dateien
        """
        # Dokument generieren
        try:
            doc = self._create_latex_document(content)
            
            # LaTeX-Datei speichern
            latex_filename = f"protocol_{protocol_id}"
            timestamped_filename = f"protocol_{protocol_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            latex_path = self.output_folder / f"{latex_filename}.tex"
            timestamped_path = self.output_folder / f"{timestamped_filename}.tex"
            
            # Beide Dateien erstellen (für Download + Archiv)
            doc.generate_tex(str(latex_path))
            doc.generate_tex(str(timestamped_path))
            
            logger.info(f"LaTeX-Dokument erstellt: {latex_path}")
            
            # PDF generieren
            pdf_path = self._compile_to_pdf(latex_path)
            
            return {
                'success': True,
                'filename': latex_filename,
                'latex_file': f"generated/{latex_filename}.tex",
                'pdf_file': f"generated/{latex_filename}.pdf" if pdf_path and pdf_path.exists() else None,
                'message': 'LaTeX-Dokument und PDF erfolgreich erstellt!' if pdf_path and pdf_path.exists() else 'LaTeX-Dokument erstellt, PDF-Generierung fehlgeschlagen'
            }
            
        except Exception as e:
            logger.error(f"LaTeX-Generierung fehlgeschlagen: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Fehler bei der LaTeX-Generierung'
            }
    
    def _create_latex_document(self, content: str) -> Document:
        """Erstellt das LaTeX-Dokument"""
        
        # Dokument-Optionen
        geometry_options = {
            "head": "40pt",
            "margin": "2.5cm",
            "bottom": "2.5cm",
            "includeheadfoot": True
        }
        
        doc = Document(geometry_options=geometry_options)
        
        # Pakete hinzufügen
        doc.packages.append(Package('babel', options=['ngerman']))
        doc.packages.append(Package('inputenc', options=['utf8']))
        doc.packages.append(Package('fontenc', options=['T1']))
        doc.packages.append(Package('amsmath'))
        doc.packages.append(Package('amssymb'))
        doc.packages.append(Package('graphicx'))
        doc.packages.append(Package('float'))
        doc.packages.append(Package('fancyhdr'))
        doc.packages.append(Package('lastpage'))
        doc.packages.append(Package('hyperref'))
        
        # Kopf- und Fußzeile
        doc.append(Command('pagestyle', 'fancy'))
        doc.append(Command('fancyhf', ''))
        doc.append(Command('fancyhead', NoEscape(r'[L]{Laborprotokoll}')))
        doc.append(Command('fancyhead', NoEscape(r'[R]{\today}')))
        doc.append(Command('fancyfoot', NoEscape(r'[C]{\thepage\ von \pageref{LastPage}}')))
        
        # Inhalt verarbeiten und hinzufügen
        self._add_content_to_document(doc, content)
        
        return doc
    
    def _add_content_to_document(self, doc: Document, content: str):
        """Fügt den Inhalt zum LaTeX-Dokument hinzu"""
        
        # Inhalt in Abschnitte aufteilen
        sections = self._parse_content_sections(content)
        
        # Titel hinzufügen
        if 'title' in sections:
            doc.append(Command('title', sections['title']))
            doc.append(Command('author', sections.get('author', 'CTA-Azubi')))
            doc.append(Command('date', Command('today')))
            doc.append(Command('maketitle'))
        
        # Weitere Abschnitte hinzufügen
        section_order = [
            'zielsetzung', 'theorie', 'material', 'durchführung',
            'ergebnisse', 'berechnungen', 'diskussion', 'schlussfolgerung'
        ]
        
        for section_key in section_order:
            if section_key in sections:
                section_title = self._get_section_title(section_key)
                with doc.create(Section(section_title)):
                    doc.append(NoEscape(sections[section_key]))
    
    def _parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parst den Inhalt in Abschnitte"""
        
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Titel erkennen
            if line.upper().startswith('TITEL:') or line.upper().startswith('# '):
                sections['title'] = line.replace('TITEL:', '').replace('#', '').strip()
                continue
            
            # Abschnitt-Überschriften erkennen
            section_key = self._identify_section(line)
            if section_key:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section_key
                current_content = []
                continue
            
            # Inhalt sammeln
            if current_section and line:
                current_content.append(line)
        
        # Letzten Abschnitt hinzufügen
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _identify_section(self, line: str) -> Optional[str]:
        """Identifiziert Abschnitt-Überschriften"""
        
        line_upper = line.upper()
        
        section_keywords = {
            'zielsetzung': ['ZIELSETZUNG', 'ZIEL', 'AUFGABE'],
            'theorie': ['THEORIE', 'THEORETISCH', 'HINTERGRUND'],
            'material': ['MATERIAL', 'GERÄTE', 'CHEMIKALIEN'],
            'durchführung': ['DURCHFÜHRUNG', 'VERSUCH', 'METHODE'],
            'ergebnisse': ['ERGEBNISSE', 'BEOBACHTUNG', 'MESSUNG'],
            'berechnungen': ['BERECHNUNGEN', 'AUSWERTUNG', 'RECHNUNG'],
            'diskussion': ['DISKUSSION', 'BEWERTUNG', 'FEHLER'],
            'schlussfolgerung': ['SCHLUSS', 'FAZIT', 'ZUSAMMENFASSUNG']
        }
        
        for section_key, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in line_upper:
                    return section_key
        
        return None
    
    def _get_section_title(self, section_key: str) -> str:
        """Gibt den deutschen Titel für einen Abschnitt zurück"""
        
        titles = {
            'zielsetzung': 'Zielsetzung',
            'theorie': 'Theoretischer Hintergrund',
            'material': 'Materialien und Geräte',
            'durchführung': 'Durchführung',
            'ergebnisse': 'Ergebnisse und Beobachtungen',
            'berechnungen': 'Berechnungen und Auswertung',
            'diskussion': 'Diskussion',
            'schlussfolgerung': 'Schlussfolgerung'
        }
        
        return titles.get(section_key, section_key.capitalize())
    
    def _compile_to_pdf(self, latex_path: Path) -> Optional[Path]:
        """Kompiliert LaTeX zu PDF"""
        
        try:
            logger.info(f"Starte PDF-Kompilierung für: {latex_path}")
            
            # pdflatex ausführen mit ausführlicher Fehlerbehandlung
            result = subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-halt-on-error',
                '-output-directory', str(latex_path.parent),
                str(latex_path)
            ], 
            capture_output=True, text=True, cwd=latex_path.parent, timeout=30)
            
            # PDF-Pfad bestimmen
            pdf_path = latex_path.with_suffix('.pdf')
            
            logger.info(f"LaTeX Return Code: {result.returncode}")
            logger.info(f"LaTeX STDOUT: {result.stdout[-500:] if result.stdout else 'Kein STDOUT'}")
            
            if result.stderr:
                logger.warning(f"LaTeX STDERR: {result.stderr[-500:]}")
            
            # Prüfen ob PDF existiert (auch bei Warnings)
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size
                logger.info(f"✅ PDF erfolgreich erstellt: {pdf_path} ({file_size} bytes)")
                
                # Bei Erfolg zweiten Lauf für bessere Referenzen
                if result.returncode == 0 and file_size > 1000:  # Mindestgröße prüfen
                    try:
                        subprocess.run([
                            'pdflatex',
                            '-interaction=nonstopmode',
                            '-output-directory', str(latex_path.parent),
                            str(latex_path)
                        ], capture_output=True, cwd=latex_path.parent, timeout=15)
                        logger.info("Zweiter LaTeX-Lauf abgeschlossen")
                    except:
                        pass  # Zweiter Lauf ist optional
                
                return pdf_path
            else:
                logger.error(f"❌ PDF-Datei wurde nicht erstellt!")
                logger.error(f"Expected PDF path: {pdf_path}")
                logger.error(f"Working directory files: {list(latex_path.parent.glob('*'))}")
                
                # Versuche alternativen PDF-Namen zu finden
                for pdf_file in latex_path.parent.glob('*.pdf'):
                    logger.info(f"Gefundene PDF-Datei: {pdf_file}")
                    if pdf_file.stem == latex_path.stem:
                        return pdf_file
                
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("PDF-Kompilierung Timeout (30s)")
            return None
        except Exception as e:
            logger.error(f"PDF-Kompilierung Ausnahme: {str(e)}")
            return None
    
    def create_custom_template(self, template_name: str, template_content: str) -> bool:
        """
        Erstellt ein benutzerdefiniertes LaTeX-Template
        
        Args:
            template_name: Name des Templates
            template_content: LaTeX-Template-Inhalt
            
        Returns:
            True bei Erfolg
        """
        try:
            template_path = self.templates_folder / f"{template_name}.tex"
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"Template erstellt: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Template-Erstellung fehlgeschlagen: {str(e)}")
            return False
    
    def list_templates(self) -> list:
        """Listet verfügbare Templates auf"""
        
        templates = []
        
        for template_file in self.templates_folder.glob('*.tex'):
            templates.append({
                'name': template_file.stem,
                'path': str(template_file),
                'modified': template_file.stat().st_mtime
            })
        
        return templates
    
    def cleanup_old_files(self, max_age_days: int = 7) -> int:
        """Löscht alte LaTeX- und PDF-Dateien"""
        
        import time
        
        deleted_count = 0
        max_age_seconds = max_age_days * 24 * 60 * 60
        current_time = time.time()
        
        try:
            # Alle .tex, .pdf, .aux, .log Dateien durchgehen
            for file_path in self.output_folder.glob('*'):
                if file_path.is_file() and file_path.suffix in ['.tex', '.pdf', '.aux', '.log']:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"LaTeX-Cleanup: {deleted_count} Dateien gelöscht")
            return deleted_count
            
        except Exception as e:
            logger.error(f"LaTeX-Cleanup fehlgeschlagen: {str(e)}")
            return deleted_count 