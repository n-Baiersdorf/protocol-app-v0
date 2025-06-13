import React from 'react';

const Settings = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Einstellungen</h1>
        <p className="text-gray-600">Konfigurieren Sie das LLM-System und Templates</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <div className="text-6xl mb-4">⚙️</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Systemeinstellungen</h2>
        <p className="text-gray-600 mb-4">
          Erweiterte Konfigurationsoptionen werden in der nächsten Phase verfügbar sein.
        </p>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-900 mb-2">Geplante Einstellungen:</h3>
          <ul className="text-sm text-yellow-800 text-left space-y-1">
            <li>• LLM-Modell-Auswahl (llama2, llama3, etc.)</li>
            <li>• LaTeX-Template-Management</li>
            <li>• OCR-Sprachkonfiguration</li>
            <li>• Ausgabeformate und Qualitätsstufen</li>
            <li>• API-Keys und Verbindungseinstellungen</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Settings; 