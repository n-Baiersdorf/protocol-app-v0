"""
LLM Service - Ollama Integration für Protokoll-Generierung
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import ollama
from jinja2 import Template

logger = logging.getLogger(__name__)

class LLMService:
    """Service für LLM-Interaktionen mit Ollama"""
    
    def __init__(self):
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'http://172.17.0.1:11434')
        self.model_name = os.environ.get('OLLAMA_MODEL', 'llama2')
        self.client = ollama.Client(host=self.base_url)
        
        # Sicherstellen, dass das Modell verfügbar ist
        self._ensure_model_available()
    
    def _ensure_model_available(self):
        """Stellt sicher, dass das gewünschte Modell verfügbar ist"""
        try:
            # Verfügbare Modelle abrufen
            models = self.client.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names:
                logger.info(f"Modell {self.model_name} nicht gefunden. Lade herunter...")
                self.client.pull(self.model_name)
                logger.info(f"Modell {self.model_name} erfolgreich geladen.")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden des Modells: {str(e)}")
            # Fallback auf kleineres Modell wenn verfügbar
            self.model_name = 'llama2:7b'
    
    def is_available(self) -> bool:
        """Prüft, ob der LLM-Service verfügbar ist"""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt="Test",
                options={'num_predict': 1}
            )
            return True
        except Exception as e:
            logger.error(f"LLM-Service nicht verfügbar: {str(e)}")
            return False
    
    def generate_protocol_content(self, files: List[Dict], protocol_metadata: Dict) -> str:
        """
        Generiert den Protokoll-Inhalt basierend auf Upload-Dateien
        
        Args:
            files: Liste der hochgeladenen Dateien mit Metadaten
            protocol_metadata: Zusätzliche Metadaten für die Generierung
            
        Returns:
            Generierter Protokoll-Inhalt als String
        """
        try:
            # Eingabedaten aufbereiten
            input_context = self._prepare_input_context(files, protocol_metadata)
            
            # Prompt für Protokoll-Generierung erstellen
            prompt = self._create_protocol_prompt(input_context)
            
            # LLM-Anfrage durchführen
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.3,  # Niedrige Temperatur für konsistente Ergebnisse
                    'num_predict': 4000,  # Längere Ausgabe für vollständige Protokolle
                    'top_k': 40,
                    'top_p': 0.9
                }
            )
            
            generated_content = response['response']
            
            # Qualitätskontrolle
            validated_content = self._validate_generated_content(generated_content)
            
            return validated_content
            
        except Exception as e:
            logger.error(f"Fehler bei der Protokoll-Generierung: {str(e)}")
            return self._create_fallback_content(files, protocol_metadata)
    
    def _prepare_input_context(self, files: List[Dict], protocol_metadata: Dict) -> Dict:
        """Bereitet den Eingabekontext für das LLM auf"""
        context = {
            'files': [],
            'metadata': protocol_metadata,
            'experiment_type': protocol_metadata.get('experiment_type', 'unknown'),
            'date': protocol_metadata.get('date', 'unknown'),
            'author': protocol_metadata.get('author', 'unknown')
        }
        
        for file_info in files:
            file_context = {
                'name': file_info.get('name', 'unknown'),
                'type': file_info.get('type', 'unknown'),
                'size': file_info.get('size', 0)
            }
            
            # Extrahierte Texte hinzufügen
            if 'extracted_text' in file_info:
                file_context['content'] = file_info['extracted_text']
            elif 'content' in file_info:
                file_context['content'] = file_info['content']
            
            context['files'].append(file_context)
        
        return context
    
    def _create_protocol_prompt(self, context: Dict) -> str:
        """Erstellt den Prompt für die Protokoll-Generierung"""
        
        prompt_template = """
Du bist ein Assistent für die Erstellung wissenschaftlicher Laborprotokolle in der CTA-Ausbildung.
Erstelle basierend auf den folgenden Eingaben ein vollständiges, professionelles Laborprotokoll.

WICHTIGE REGELN:
1. Erfinde KEINE Daten oder Messwerte
2. Wenn Informationen fehlen, kennzeichne diese als [UNBEKANNT] oder [ZU ERGÄNZEN]
3. Nutze nur die bereitgestellten Informationen
4. Strukturiere das Protokoll nach wissenschaftlichen Standards
5. Verwende korrekte deutsche Rechtschreibung und Fachterminologie

EINGABEDATEN:
Experiment-Typ: {{ experiment_type }}
Datum: {{ date }}
Autor: {{ author }}

DATEIEN:
{% for file in files %}
- {{ file.name }} ({{ file.type }}):
  {% if file.content %}
  {{ file.content }}
  {% else %}
  [Inhalt nicht verfügbar]
  {% endif %}
{% endfor %}

ZUSÄTZLICHE METADATEN:
{{ metadata }}

Erstelle ein vollständiges Laborprotokoll mit folgender Struktur:

1. TITEL UND METADATEN
2. ZIELSETZUNG
3. THEORETISCHER HINTERGRUND
4. MATERIALIEN UND GERÄTE
5. DURCHFÜHRUNG
6. BEOBACHTUNGEN UND ERGEBNISSE
7. BERECHNUNGEN
8. DISKUSSION
9. SCHLUSSFOLGERUNG

Beginne mit der Erstellung:
"""
        
        template = Template(prompt_template)
        return template.render(**context)
    
    def _validate_generated_content(self, content: str) -> str:
        """Validiert und bereinigt den generierten Inhalt"""
        
        # Grundlegende Validierung
        if not content or len(content) < 100:
            raise ValueError("Generierter Inhalt zu kurz")
        
        # Entfernen von potentiellen LLM-Artefakten
        content = content.replace("Als KI-Assistent", "")
        content = content.replace("Ich kann nicht", "")
        
        # Sicherstellen, dass kritische Sektionen vorhanden sind
        required_sections = ["ZIELSETZUNG", "DURCHFÜHRUNG", "ERGEBNISSE"]
        for section in required_sections:
            if section not in content.upper():
                logger.warning(f"Kritische Sektion '{section}' fehlt im generierten Inhalt")
        
        return content
    
    def _create_fallback_content(self, files: List[Dict], protocol_metadata: Dict) -> str:
        """Erstellt einen Fallback-Inhalt wenn LLM-Generierung fehlschlägt"""
        
        fallback_template = """
# Laborprotokoll (Automatisch generiert)

## Metadaten
- Datum: {date}
- Autor: {author}
- Experiment: {experiment_type}

## Eingabedateien
{file_list}

## Status
⚠️ ACHTUNG: Dieses Protokoll wurde automatisch als Fallback generiert.
Die LLM-basierte Generierung ist fehlgeschlagen.
Bitte überprüfen Sie alle Inhalte und ergänzen Sie fehlende Informationen.

## Zu ergänzen
- [ ] Zielsetzung des Experiments
- [ ] Durchführung
- [ ] Messwerte und Beobachtungen  
- [ ] Berechnungen
- [ ] Diskussion der Ergebnisse
- [ ] Schlussfolgerungen

## Eingabedaten
{input_summary}
"""
        
        file_list = "\n".join([f"- {f.get('name', 'unknown')}" for f in files])
        input_summary = json.dumps(protocol_metadata, indent=2, ensure_ascii=False)
        
        return fallback_template.format(
            date=protocol_metadata.get('date', 'unbekannt'),
            author=protocol_metadata.get('author', 'unbekannt'),
            experiment_type=protocol_metadata.get('experiment_type', 'unbekannt'),
            file_list=file_list,
            input_summary=input_summary
        )
    
    def refine_section(self, section_content: str, section_type: str) -> str:
        """Verfeinert einen spezifischen Abschnitt des Protokolls"""
        
        refinement_prompt = f"""
Verbessere den folgenden Abschnitt eines Laborprotokolls:

ABSCHNITT-TYP: {section_type}
INHALT:
{section_content}

Verbessere diesen Abschnitt hinsichtlich:
- Wissenschaftlicher Genauigkeit
- Sprachlicher Klarheit
- Vollständigkeit der Informationen
- Struktur und Lesbarkeit

WICHTIG: Erfinde keine neuen Daten oder Messwerte!

Verbesserte Version:
"""
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=refinement_prompt,
                options={'temperature': 0.1, 'num_predict': 1000}
            )
            return response['response']
        except Exception as e:
            logger.error(f"Fehler bei der Abschnitts-Verfeinerung: {str(e)}")
            return section_content  # Rückgabe des ursprünglichen Inhalts 