import React from 'react';

const Protocols = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Protokolle</h1>
        <p className="text-gray-600">Verwalten und bearbeiten Sie Ihre generierten Protokolle</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <div className="text-6xl mb-4">📄</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Protokoll-Verwaltung</h2>
        <p className="text-gray-600 mb-4">
          Noch keine Protokolle vorhanden. Erstellen Sie Ihr erstes Protokoll über den Upload-Bereich.
        </p>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-900 mb-2">Geplante Features:</h3>
          <ul className="text-sm text-green-800 text-left space-y-1">
            <li>• Liste aller generierten Protokolle</li>
            <li>• PDF-Download und LaTeX-Export</li>
            <li>• Protokoll-Bearbeitung und Korrektur</li>
            <li>• Versionskontrolle</li>
            <li>• Suchfunktion und Filter</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Protocols; 