"""
OCR Service - Texterkennung aus handschriftlichen Notizen und Bildern
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np

logger = logging.getLogger(__name__)

class OCRService:
    """Service für Optical Character Recognition (OCR)"""
    
    def __init__(self):
        # Tesseract-Konfiguration für deutsche Texte
        self.tesseract_config = '--oem 3 --psm 6 -l deu+eng'
        
        # Prüfen ob Tesseract verfügbar ist
        self._check_tesseract_availability()
    
    def _check_tesseract_availability(self):
        """Prüft die Verfügbarkeit von Tesseract"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Tesseract nicht verfügbar: {str(e)}")
            raise RuntimeError("Tesseract OCR ist nicht verfügbar")
    
    def extract_text(self, image_path: str) -> str:
        """
        Extrahiert Text aus einem Bild
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Extrahierter Text
        """
        try:
            # Bild laden und vorverarbeiten
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            # OCR durchführen
            extracted_text = pytesseract.image_to_string(
                processed_image, 
                config=self.tesseract_config
            )
            
            # Text nachbearbeiten
            cleaned_text = self._postprocess_text(extracted_text)
            
            logger.info(f"Text erfolgreich extrahiert aus {image_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR-Fehler bei {image_path}: {str(e)}")
            return f"[OCR-FEHLER: {str(e)}]"
    
    def extract_text_with_confidence(self, image_path: str) -> Dict:
        """
        Extrahiert Text mit Konfidenz-Informationen
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dict mit Text und Konfidenz-Informationen
        """
        try:
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            # Detaillierte OCR-Daten abrufen
            data = pytesseract.image_to_data(
                processed_image,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Konfidenz-Analyse
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Text zusammenfügen
            text_parts = []
            for i, word in enumerate(data['text']):
                if int(data['conf'][i]) > 30:  # Nur Wörter mit > 30% Konfidenz
                    text_parts.append(word)
            
            extracted_text = ' '.join(text_parts)
            cleaned_text = self._postprocess_text(extracted_text)
            
            result = {
                'text': cleaned_text,
                'confidence': avg_confidence,
                'word_count': len([w for w in data['text'] if w.strip()]),
                'high_confidence_words': len([c for c in confidences if c > 70]),
                'low_confidence_areas': len([c for c in confidences if c < 50])
            }
            
            logger.info(f"OCR mit Konfidenz-Analyse abgeschlossen: {avg_confidence:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"OCR-Konfidenz-Analyse fehlgeschlagen: {str(e)}")
            return {
                'text': f"[OCR-FEHLER: {str(e)}]",
                'confidence': 0,
                'error': str(e)
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Bildvorverarbeitung für bessere OCR-Ergebnisse
        
        Args:
            image: Original PIL-Image
            
        Returns:
            Vorverarbeitetes PIL-Image
        """
        try:
            # In Graustufen konvertieren
            gray_image = image.convert('L')
            
            # Bildgröße anpassen (OCR funktioniert besser bei höherer Auflösung)
            width, height = gray_image.size
            if width < 1000:
                scale_factor = 1000 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray_image = gray_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Kontrast verbessern
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(1.5)
            
            # Schärfe verbessern
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            sharp_image = sharpness_enhancer.enhance(1.2)
            
            # Rauschen reduzieren
            filtered_image = sharp_image.filter(ImageFilter.MedianFilter(size=3))
            
            # Binarisierung (optional, für sehr schwache Bilder)
            # threshold = self._get_optimal_threshold(filtered_image)
            # binary_image = filtered_image.point(lambda x: 0 if x < threshold else 255, '1')
            
            return filtered_image
            
        except Exception as e:
            logger.warning(f"Bildvorverarbeitung fehlgeschlagen: {str(e)}")
            return image  # Fallback auf Originalbild
    
    def _get_optimal_threshold(self, image: Image.Image) -> int:
        """
        Berechnet den optimalen Schwellenwert für Binarisierung
        (Otsu's Method vereinfacht)
        """
        try:
            # Histogram erstellen
            histogram = image.histogram()
            
            # Vereinfachter Otsu-Algorithmus
            total_pixels = sum(histogram)
            sum_total = sum(i * histogram[i] for i in range(256))
            
            sum_background = 0
            weight_background = 0
            max_variance = 0
            optimal_threshold = 0
            
            for threshold in range(256):
                weight_background += histogram[threshold]
                if weight_background == 0:
                    continue
                
                weight_foreground = total_pixels - weight_background
                if weight_foreground == 0:
                    break
                
                sum_background += threshold * histogram[threshold]
                
                mean_background = sum_background / weight_background
                mean_foreground = (sum_total - sum_background) / weight_foreground
                
                variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
                
                if variance > max_variance:
                    max_variance = variance
                    optimal_threshold = threshold
            
            return optimal_threshold
            
        except Exception:
            return 128  # Fallback-Schwellenwert
    
    def _postprocess_text(self, text: str) -> str:
        """
        Nachbearbeitung des extrahierten Textes
        
        Args:
            text: Roher OCR-Text
            
        Returns:
            Bereinigter Text
        """
        if not text:
            return ""
        
        # Grundlegende Bereinigung
        cleaned = text.strip()
        
        # Mehrfache Leerzeichen entfernen
        cleaned = ' '.join(cleaned.split())
        
        # Häufige OCR-Fehler korrigieren
        corrections = {
            'rn': 'm',  # häufiger OCR-Fehler
            '0': 'O',   # in Kontexten wo Buchstaben erwartet werden
            '1': 'l',   # in Kontexten wo Buchstaben erwartet werden
            '5': 'S',   # in Kontexten wo Buchstaben erwartet werden
        }
        
        # Korrektur nur in bestimmten Kontexten anwenden
        # (Vereinfacht für MVP - könnte durch ML-Modell verbessert werden)
        
        # Zeilenumbrüche normalisieren
        cleaned = cleaned.replace('\n\n', '\n').replace('\r\n', '\n')
        
        # Chemische Formeln und Zahlen besser formatieren
        cleaned = self._format_chemical_notations(cleaned)
        
        return cleaned
    
    def _format_chemical_notations(self, text: str) -> str:
        """
        Verbessert die Formatierung von chemischen Formeln und Messwerten
        """
        # Vereinfachte Formatierung für MVP
        # Könnte durch spezialisierte chemische OCR-Nachbearbeitung erweitert werden
        
        import re
        
        # Häufige chemische Elemente richtig formatieren
        chemical_patterns = {
            r'\bH20\b': 'H2O',
            r'\bNaCl\b': 'NaCl',
            r'\bCaCl2\b': 'CaCl2',
            r'\bHCI\b': 'HCl',
            r'\bNaOH\b': 'NaOH'
        }
        
        for pattern, replacement in chemical_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Einheiten besser formatieren
        unit_patterns = {
            r'(\d+)\s*(ml|ML)\b': r'\1 mL',
            r'(\d+)\s*(mg|MG)\b': r'\1 mg',
            r'(\d+)\s*(g|G)\b(?!\w)': r'\1 g',
            r'(\d+)\s*°\s*C\b': r'\1°C',
            r'(\d+)\s*(mol|MOL)\b': r'\1 mol'
        }
        
        for pattern, replacement in unit_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def extract_structured_data(self, image_path: str) -> Dict:
        """
        Versucht strukturierte Daten aus dem Bild zu extrahieren
        (z.B. Tabellen, Listen, Messwerte)
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dict mit strukturierten Daten
        """
        try:
            text = self.extract_text(image_path)
            
            result = {
                'raw_text': text,
                'measurements': self._extract_measurements(text),
                'chemical_compounds': self._extract_chemical_compounds(text),
                'temperatures': self._extract_temperatures(text),
                'observations': self._extract_observations(text)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Strukturierte Datenextraktion fehlgeschlagen: {str(e)}")
            return {'error': str(e)}
    
    def _extract_measurements(self, text: str) -> List[Dict]:
        """Extrahiert Messwerte aus dem Text"""
        import re
        
        measurements = []
        
        # Pattern für verschiedene Messungen
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg|g|kg|ml|l|mol)',
            r'(\d+(?:\.\d+)?)\s*°C',
            r'(\d+(?:\.\d+)?)\s*(min|h|s)',
            r'pH\s*[=:]\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    value, unit = match
                    measurements.append({
                        'value': float(value),
                        'unit': unit,
                        'type': 'measurement'
                    })
        
        return measurements
    
    def _extract_chemical_compounds(self, text: str) -> List[str]:
        """Extrahiert chemische Verbindungen aus dem Text"""
        import re
        
        # Einfache Pattern für häufige chemische Verbindungen
        chemical_patterns = [
            r'\b[A-Z][a-z]?(?:\d+)?(?:[A-Z][a-z]?\d*)*\b',  # Grundlegende chemische Formeln
            r'\b(?:NaCl|H2O|HCl|NaOH|CaCl2|KOH|H2SO4|HNO3)\b'  # Häufige Verbindungen
        ]
        
        compounds = []
        for pattern in chemical_patterns:
            matches = re.findall(pattern, text)
            compounds.extend(matches)
        
        # Duplikate entfernen und filtern
        return list(set([c for c in compounds if len(c) > 1 and not c.isdigit()]))
    
    def _extract_temperatures(self, text: str) -> List[Dict]:
        """Extrahiert Temperaturen aus dem Text"""
        import re
        
        temp_patterns = [
            r'(\d+(?:\.\d+)?)\s*°C',
            r'(\d+(?:\.\d+)?)\s*°F',
            r'(\d+(?:\.\d+)?)\s*K'
        ]
        
        temperatures = []
        for pattern in temp_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                unit = 'C' if '°C' in pattern else ('F' if '°F' in pattern else 'K')
                temperatures.append({
                    'value': float(match),
                    'unit': unit,
                    'type': 'temperature'
                })
        
        return temperatures
    
    def _extract_observations(self, text: str) -> List[str]:
        """Extrahiert Beobachtungen aus dem Text"""
        import re
        
        # Keywords für Beobachtungen
        observation_keywords = [
            r'Farbe?\s*[:\-]?\s*([a-zA-ZäöüÄÖÜß\s]+)',
            r'Geruch\s*[:\-]?\s*([a-zA-ZäöüÄÖÜß\s]+)',
            r'Niederschlag\s*[:\-]?\s*([a-zA-ZäöüÄÖÜß\s]+)',
            r'Reaktion\s*[:\-]?\s*([a-zA-ZäöüÄÖÜß\s]+)',
            r'Beobachtung\s*[:\-]?\s*([a-zA-ZäöüÄÖÜß\s]+)'
        ]
        
        observations = []
        for pattern in observation_keywords:
            matches = re.findall(pattern, text, re.IGNORECASE)
            observations.extend([match.strip() for match in matches if match.strip()])
        
        return list(set(observations))  # Duplikate entfernen 