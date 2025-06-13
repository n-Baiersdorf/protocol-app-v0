import React from 'react';

const Upload = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Datei-Upload</h1>
        <p className="text-gray-600">Laden Sie Ihre Labornotizen und Versuchsdaten hoch</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <div className="text-6xl mb-4">📤</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload-Funktion</h2>
        <p className="text-gray-600 mb-4">
          Diese Funktion wird in der nächsten Entwicklungsphase implementiert.
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Geplante Features:</h3>
          <ul className="text-sm text-blue-800 text-left space-y-1">
            <li>• Drag & Drop für Bilder und Dokumente</li>
            <li>• OCR-Texterkennung aus handschriftlichen Notizen</li>
            <li>• PDF, Word, Excel-Support</li>
            <li>• Batch-Upload mehrerer Dateien</li>
            <li>• Live-Vorschau der erkannten Daten</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Upload; 