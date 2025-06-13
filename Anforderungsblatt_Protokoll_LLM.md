# Anforderungsblatt: LLM-basierte Protokollerstellung für CTA-Ausbildung

## 1. Einleitung und Ziele

### 1.1 Projektbeschreibung
Entwicklung einer LLM-basierten Webanwendung zur automatisierten Erstellung von professionellen LaTeX-Protokollen aus Versuchsanweisungen, Labornotizen und anderen Eingabedaten.

### 1.2 Problemstellung
- Hoher Zeitaufwand für manuelle Protokollerstellung in der CTA-Ausbildung
- Notwendigkeit konsistenter und professioneller Dokumentation
- Wiederkehrende Strukturierungs- und Formatierungsarbeit

### 1.3 Projektziele
- **Primärziel:** Drastische Zeitersparnis bei der Protokollerstellung
- **Qualitätsziel:** Erstellung abgabereifer, professioneller Protokolle
- **Sekundärziel:** Reduzierung von Formatierungsfehlern und Konsistenzproblemen
- **Lernziel:** Beibehaltung des Lerneffekts durch interaktive Kontrollelemente

### 1.4 Zielgruppe
- **Primär:** CTA-Auszubildende und Studierende in naturwissenschaftlichen Fächern
- **Sekundär:** Laborpersonal und Dozenten, die regelmäßig Protokolle erstellen oder bewerten

## 2. Funktionale Anforderungen

### 2.1 Dateneingabe

#### 2.1.1 Primäre Eingabequellen
- **Handschriftliche Labornotizen (Fotos):** 
  - Extraktion von Messwerten (Einwaagen, Messergebnisse, Beobachtungen)
  - OCR-Unterstützung für verschiedene Handschriften
  - Unterstützung für Skizzen und einfache Diagramme
- **Arbeitsanweisungen (AAW):**
  - Zentrales Dokument für Versuchskontext
  - Unterstützung für PDF, DOCX, TXT-Formate

#### 2.1.2 Sekundäre Eingabequellen
- **Messdaten:**
  - CSV-Dateien
  - Excel-Dateien (.xls, .xlsx)
  - Tabellarische Daten aus anderen Quellen
- **Zusätzliche Dokumente:**
  - Sicherheitsdatenblätter
  - Literaturquellen
  - Bilddateien von Versuchsaufbauten

#### 2.1.3 Upload-Mechanismus
- Drag & Drop-Webinterface
- Batch-Upload für mehrere Dateien
- Vorschau-Funktion für hochgeladene Inhalte

### 2.2 Datenverarbeitung & LLM-Interaktion

#### 2.2.1 Qualitätssicherung (Kernprinzip)
- **Kernziel:** Erstellung qualitativ hochwertiger, nahezu abgabereifer Protokolle
- **No-Assumptions-Regel:** Das LLM darf keine fachlichen Annahmen treffen
- **Explizite Unsicherheitsbehandlung:** Unklarheiten müssen klar kommuniziert werden

#### 2.2.2 Umgang mit Unklarheiten
- **Automatische Erkennung:** System identifiziert mehrdeutige oder unvollständige Informationen
- **Klärungsfenster:** Interaktive Dialoge zur Informationsklärung
  - Option 1: Manuelle Eingabe durch Nutzer
  - Option 2: Automodus mit LLM-Entscheidung (gekennzeichnet)
- **Rückfragen:** Strukturierte Nachfragen bei kritischen Unklarheiten

#### 2.2.3 Kalkulationshilfe
- **Automatische Berechnungen:** 
  - Molmassenberechnungen
  - Stoffmengen und Konzentrationen
  - Ausbeuten und Verluste
  - Fehlerfortpflanzung
- **Keine Zahlen-Halluzination:** Alle Berechnungen müssen nachvollziehbar und korrekt sein
- **Formel-Integration:** Automatische Einbindung relevanter Formeln in LaTeX
- **Einheiten-Konsistenz:** Überprüfung und Standardisierung von Maßeinheiten

#### 2.2.4 Interaktiver Korrekturprozess
- **Pre-Generation Review:** Informationsaustausch vor finaler Dokumenterstellung
- **Selektive Korrekturen:** Gezielte Überarbeitung einzelner Passagen ohne Komplett-Neugenerierung
- **Versionierung:** Nachverfolgung von Änderungen und Korrekturen

#### 2.2.5 Qualitätskontrolle
- **Optionales Kontroll-Feature:** Zweite LLM-Instanz für Konsistenz-Prüfung
- **Konfidenz-Scoring:** Bewertung der Sicherheit einzelner Dokument-Abschnitte
- **Highlight-System:** Markierung unsicherer Passagen für manuelle Überprüfung

#### 2.2.6 Chemie-Informationsintegration
- **Stoffdatenbank-Anbindung:** Integration von Chemikalien-Informationen
- **Sicherheitsdaten:** Automatische Einbindung relevanter Sicherheitshinweise
- **Physikalische Eigenschaften:** Abruf von Standardwerten (Schmelzpunkte, Dichten, etc.)
- **Potenzielle Quellen:** PubChem API, ChemSpider, oder LLM-integriertes Wissen

### 2.3 Grafikerstellung

#### 2.3.1 Programmatische Erstellung
- **Baukasten-System:** Modulare Erstellung verschiedener Grafiktypen
- **Unterstützte Formate:**
  - Messwert-Diagramme (Plots, Histogramme)
  - Reaktionsschemata
  - Apparatur-Skizzen (einfach)
  - Strukturformeln (basic)
- **Code-basiert:** Generierung über Plot-Bibliotheken (matplotlib, plotly) statt Bildgenerierung

### 2.4 LaTeX-Generierung

#### 2.4.1 Dokumentstruktur
- **Standardgliederung:**
  - Titelseite mit Metadaten
  - Einleitung und Zielsetzung
  - Theoretischer Hintergrund
  - Materialien und Geräte
  - Durchführung (Schritt-für-Schritt)
  - Ergebnisse und Beobachtungen
  - Berechnungen und Auswertung
  - Diskussion und Fehlerbetrachtung
  - Schlussfolgerung
  - Literaturverzeichnis
  - Anhang

#### 2.4.2 Vorlagen-System
- **Dynamische Vorlagen:** Nutzer können LaTeX-Templates anpassen
- **Versuchstyp-spezifisch:** Verschiedene Vorlagen für unterschiedliche Versuchsarten
- **Modularer Aufbau:** Einzelne Sektionen können individuell angepasst werden

#### 2.4.3 Manueller Eingriff
- **LaTeX-Code-Zugriff:** Direkter Zugriff auf generierten LaTeX-Code
- **Inline-Editing:** Möglichkeit zur direkten Bearbeitung vor Kompilierung
- **Template-Upload:** Nutzer können eigene Vorlagen hochladen

### 2.5 Ausgabe und Export

#### 2.5.1 Dateiformate
- **LaTeX-Quelldatei (.tex):** Für weitere Bearbeitung
- **Kompilierte PDF:** Für direkte Nutzung
- **Beide Formate gleichzeitig:** Parallele Bereitstellung

#### 2.5.2 Download-Optionen
- **Direkter Download:** Sofortiger Zugriff auf generierte Dateien
- **Batch-Download:** Zip-Archive mit allen relevanten Dateien
- **Cloud-Integration:** Optional für Backup und Synchronisation

### 2.6 Feedback und Bewertung

#### 2.6.1 Nutzer-Feedback
- **Bewertungssystem:** Qualitätsbewertung generierter Protokolle
- **Supervisor-Feedback:** Spezielle Eingabe für Dozenten/Betreuer
- **Fehler-Reporting:** Strukturierte Fehlermeldungen für Verbesserungen

#### 2.6.2 Lernkontrolle (Optional)
- **Verständnis-Quiz:** Interaktive Fragen zu kritischen Protokoll-Abschnitten
- **Nicht-Kernfunktionalität:** Ergänzende Lernhilfe ohne Zwang

## 3. Nicht-funktionale Anforderungen

### 3.1 Benutzeroberfläche (UI/UX)

#### 3.1.1 Usability-Prinzipien
- **Einfachheit:** Intuitive Bedienung ohne Schulungsbedarf
- **Geschwindigkeit:** Reaktionsschnelle Benutzeroberfläche
- **Klarheit:** Übersichtliche Darstellung komplexer Informationen

#### 3.1.2 Komplexitätsstufen
- **Einfacher Modus:** 
  - Minimale Einstellungen
  - Automatisierte Standardprozesse
  - Ideal für Gelegenheitsnutzer
- **Experten-Modus:**
  - Detaillierte Konfigurationsmöglichkeiten
  - Erweiterte Kontrolle über LLM-Parameter
  - Anpassbare Workflows

#### 3.1.3 Responsive Design
- **Multi-Device-Support:** Funktionsfähigkeit auf Desktop, Tablet, Smartphone
- **Accessibility:** Barrierefreie Gestaltung nach WCAG-Standards

### 3.2 Performance

#### 3.2.1 Leistungsanforderungen
- **Generierungszeit:** Angemessene Wartezeiten (5-10 Minuten akzeptabel)
- **Priorisierung:** Qualität vor Geschwindigkeit
- **Skalierbarkeit:** Handhabung mehrerer gleichzeitiger Nutzer

#### 3.2.2 Ressourcen-Management
- **Token-Optimierung:** Effiziente Nutzung von LLM-APIs
- **Caching:** Zwischenspeicherung häufig verwendeter Daten
- **Batch-Processing:** Optimierung für mehrere Protokolle

### 3.3 Zuverlässigkeit und Genauigkeit

#### 3.3.1 Höchste Priorität
- **Wissenschaftliche Integrität:** Keine Erfindung oder Verfälschung von Daten
- **Berechnungsgenauigkeit:** Mathematische Korrektheit aller Kalkulationen
- **Konsistenz:** Wiederholbare Ergebnisse bei gleichen Eingaben

#### 3.3.2 Fehlerbehandlung
- **Graceful Degradation:** Funktionsfähigkeit auch bei Teilfehlern
- **Logging:** Detaillierte Protokollierung für Debugging
- **Recovery:** Automatische Wiederherstellung bei Systemfehlern

### 3.4 Sicherheit und Datenschutz

#### 3.4.1 Datenschutz
- **Lokale Verarbeitung:** Persönliche Daten werden nicht an externe APIs gesendet
- **Anonymisierung:** Entfernung persönlicher Informationen vor LLM-Verarbeitung
- **Datensparsamkeit:** Minimale Datensammlung und -speicherung

#### 3.4.2 Sicherheit
- **Verschlüsselung:** Sichere Übertragung und Speicherung
- **Authentifizierung:** Sichere Nutzeranmeldung
- **API-Key-Management:** Sichere Verwaltung von LLM-API-Schlüsseln

### 3.5 Skalierbarkeit

#### 3.5.1 Architektur-Vision
- **Phase 1:** Lokale Webanwendung (Self-Hosting)
- **Phase 2:** Zentrale Server-Lösung für breitere Nutzung
- **Modularität:** Einzelne Komponenten können unabhängig skaliert werden

#### 3.5.2 Nutzer-Modell
- **Self-Hosting:** Nutzer verwenden eigene API-Keys und Infrastruktur
- **Managed Service:** Optionale zentrale Bereitstellung
- **Hybrid:** Kombination beider Ansätze

### 3.6 Wartbarkeit

#### 3.6.1 Code-Qualität
- **Modularität:** Klare Trennung von Funktionalitäten
- **Dokumentation:** Umfassende Code- und API-Dokumentation
- **Testing:** Automatisierte Tests für kritische Komponenten

#### 3.6.2 Konfigurierbarkeit
- **Template-Management:** Einfache Anpassung von LaTeX-Vorlagen
- **Parameter-Tuning:** Anpassbare LLM-Parameter
- **Plugin-System:** Erweiterbarkeit durch Module

### 3.7 LLM-Integration und API-Management

#### 3.7.1 Multi-Provider-Support
- **Kommerziell:** OpenAI, Anthropic, Google, Azure
- **Open Source:** Unterstützung für Ollama und lokale Modelle DEFAULT!
- **Flexibilität:** Einfacher Wechsel zwischen Anbietern

#### 3.7.2 Kosten-Optimierung
- **Verschiedene Modi:**
  - Draft-Modus: Günstige Modelle für Vorentwürfe
  - Final-Modus: Hochwertige Modelle für finale Version
  - Economy-Modus: Optimiert für niedrige Token-Kosten
- **Token-Tracking:** Überwachung und Budgetierung des API-Verbrauchs

## 4. Technische Anforderungen

### 4.1 Systemarchitektur

#### 4.1.1 Technologie-Stack
- **Backend:** Python (Django/Flask) oder Node.js
- **Frontend:** React, Vue.js oder Angular
- **Datenbank:** PostgreSQL oder MongoDB
- **Containerisierung:** Docker für einfache Bereitstellung
- **API-Design:** RESTful oder GraphQL
- **LLM-Integration:** Ollama
- **UPLOAD-LLM-Management:** RAG mit Llamaindex

#### 4.1.2 Modularität
- **Microservices-Architektur:** Unabhängige Services für verschiedene Funktionen
- **Service-Komponenten:**
  - LLM-Gateway Service
  - OCR-Service
  - LaTeX-Rendering Service
  - File-Management Service
  - User-Management Service

### 4.2 LLM-Integration

#### 4.2.1 API-Abstraction
- **Unified Interface:** Einheitliche Schnittstelle für verschiedene LLM-Provider
- **Rate Limiting:** Schutz vor API-Überlastung
- **Fallback-Mechanismen:** Alternative Modelle bei Ausfällen

#### 4.2.2 Prompt Engineering
- **Template-System:** Strukturierte Prompt-Vorlagen
- **Context-Management:** Optimale Nutzung des Kontext-Fensters
- **Chain-of-Thought:** Mehrstufige Verarbeitungspipeline

### 4.3 LaTeX-Integration

#### 4.3.1 Rendering-Pipeline
- **Template-Engine:** Jinja2 oder ähnlich für dynamische Vorlagen
- **Compilation:** Automatische PDF-Generierung
- **Error-Handling:** LaTeX-Fehlerbehandlung und Nutzer-Feedback

#### 4.3.2 Bibliotheken
- **Python:** PyLaTeX für programmatische LaTeX-Erstellung
- **JavaScript:** Alternative Bibliotheken für Frontend-Integration

### 4.4 Deployment und Hosting

#### 4.4.1 Lokale Bereitstellung
- **Docker-Container:** Einfache Installation und Konfiguration
- **Documentation:** Detaillierte Setup-Anleitungen
- **Configuration:** Umgebungsvariablen für Anpassungen

#### 4.4.2 Cloud-Deployment
- **Container-Orchestrierung:** Kubernetes oder Docker Swarm
- **Monitoring:** Logging und Performance-Überwachung
- **Scaling:** Automatische Skalierung basierend auf Last

## 5. Risikomanagement

### 5.1 Qualitätsrisiken

#### 5.1.1 Unentdeckte Fehler in Protokollen
- **Risiko:** Nutzer übersehen LLM-Artefakte oder fachliche Fehler
- **Maßnahmen:**
  - Konfidenz-Scoring für Dokument-Abschnitte
  - Highlight-System für unsichere Passagen
  - Strukturierte Proof-Reading-Hilfen
  - Optionale Verständnis-Kontrolle durch Quiz

#### 5.1.2 Halluzination von Berechnungen
- **Risiko:** LLM erfindet Zahlen oder Berechnungen
- **Maßnahmen:**
  - Separater Kalkulationsservice mit mathematischer Validierung
  - Schritt-für-Schritt-Nachvollziehbarkeit aller Berechnungen
  - Automatische Plausibilitätsprüfungen

### 5.2 Technische Risiken

#### 5.2.1 LLM-API-Verfügbarkeit
- **Risiko:** Ausfall oder Änderung von LLM-Services
- **Maßnahmen:**
  - Multi-Provider-Unterstützung
  - Lokale Fallback-Modelle via Ollama
  - Graceful Degradation bei Service-Ausfällen

#### 5.2.2 Datenschutz und Sicherheit
- **Risiko:** Ungewollte Datenübertragung an externe Services
- **Maßnahmen:**
  - Lokale Anonymisierung vor API-Calls
  - Opt-out für sensible Daten
  - Transparente Datenverarbeitung

### 5.3 Usability-Risiken

#### 5.3.1 Überladene Benutzeroberfläche
- **Risiko:** Zu viele Optionen überfordern Nutzer
- **Maßnahmen:**
  - Klare Trennung zwischen Basis- und Experten-Modus
  - Progressive Disclosure von Funktionen
  - Intuitive Standardeinstellungen

## 6. Entwicklungsplanung

### 6.1 Zeitplan

#### 6.1.1 Ziel
- **MVP-Fertigstellung:** 2 Monate
- **Funktionale Mindestanforderungen für MVP:**
  - Basis-Upload-Funktionalität
  - Einfache LLM-Integration
  - Standard-LaTeX-Generierung
  - Grundlegende Benutzeroberfläche

#### 6.1.2 Entwicklungsphasen
- **Phase 1 (Wochen 1-2):** Architektur und Setup
- **Phase 2 (Wochen 3-4):** Kern-Backend-Entwicklung
- **Phase 3 (Wochen 5-6):** Frontend und Integration
- **Phase 4 (Wochen 7-8):** Testing, Debugging, Deployment

### 6.2 Meilensteine

#### 6.2.1 MVP-Meilensteine
1. **Funktionsfähiger File-Upload**
2. **Basis-LLM-Integration**
3. **Einfache LaTeX-Generierung**
4. **Benutzerfreundliche Oberfläche**
5. **Lokale Deployment-Fähigkeit**

#### 6.2.2 Post-MVP-Erweiterungen
- Erweiterte Kalkulationshilfe
- Grafikerstellung
- Multi-Provider-LLM-Support
- Erweiterte Qualitätskontrolle
- Template-Customization

### 6.3 Erfolgsmetriken
- **Funktionalität:** Erfolgreiche Protokoll-Generierung aus Test-Inputs
- **Qualität:** Manuell validierte Ausgabe-Qualität
- **Usability:** Erfolgreiche Nutzung durch Test-User ohne Schulung
- **Performance:** Akzeptable Generierungszeiten (<10 Minuten)

## 7. Zukünftige Erweiterungen

### 7.1 Erweiterte Features
- **Kollaboration:** Multi-User-Bearbeitung von Protokollen
- **Versionskontrolle:** Git-ähnliche Änderungsverfolgung
- **Integration:** Anbindung an Labor-Management-Systeme
- **Mobile App:** Native Smartphone-Anwendung für Vor-Ort-Nutzung

### 7.2 Fachliche Erweiterungen
- **Weitere Disziplinen:** Anpassung für Biologie, Physik, Pharmazie
- **Spezialisierung:** Fachspezifische Protokoll-Templates
- **Automatisierung:** Integration mit Messinstrumenten und LIMS

### 7.3 Technische Evolution
- **KI-Verbesserung:** Integration neuester LLM-Technologien
- **Automatisierung:** Selbstlernende Optimierung der Protokoll-Qualität
- **Skalierung:** Enterprise-Grade Deployment-Optionen

---

**Dokumentversion:** 1.0  
**Erstellt am:** 13.6.2025  
**Autor:** Noah Baiersdorf & Claude 4 Sonnet  
**Status:** Anforderungsdefinition - Bereit für technische Planung 