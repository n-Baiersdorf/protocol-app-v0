import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState({
    backend: false,
    llm: false,
    database: false
  });
  const [loading, setLoading] = useState(true);
  const [protocols, setProtocols] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    files: []
  });

  // System-Status prüfen
  const checkSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/health');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus({
          backend: true,
          llm: data.services?.llm || false,
          database: data.services?.database || false
        });
      }
    } catch (error) {
      console.error('Fehler beim Status-Check:', error);
      setSystemStatus({ backend: false, llm: false, database: false });
    } finally {
      setLoading(false);
    }
  };

  // Protokolle laden
  const loadProtocols = async () => {
    try {
      const response = await fetch('http://localhost:5000/protocols');
      if (response.ok) {
        const data = await response.json();
        setProtocols(data.protocols || []);
      }
    } catch (error) {
      console.error('Fehler beim Laden der Protokolle:', error);
    }
  };

  // Protokoll erstellen
  const createProtocol = async () => {
    if (!createForm.title.trim()) {
      alert('Bitte geben Sie einen Titel ein');
      return;
    }

    setCreating(true);
    try {
      // Beispiel-Daten für die Protokoll-Erstellung
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: createForm.title,
          metadata: { description: createForm.description },
          files: [{
            name: 'labornotiz.txt',
            type: 'document',
            content: `Laborbericht: ${createForm.title}
            
${createForm.description}

Versuchsdurchführung:
- NaOH-Lösung: 0.1 M
- HCl-Lösung: unbekannte Konzentration
- Verbrauch: 23.5 mL NaOH
- Indikator: Phenolphthalein
- Umschlag: farblos zu rosa

Beobachtungen:
- Klarer Umschlag des Indikators
- Lösung blieb stabil rosa
            `
          }]
        })
      });

      if (response.ok) {
        const result = await response.json();
        setShowCreateModal(false);
        setCreateForm({ title: '', description: '', files: [] });
        loadProtocols(); // Protokolle neu laden
        alert(`Protokoll "${createForm.title}" erfolgreich erstellt!`);
      } else {
        throw new Error('Fehler bei der Protokoll-Erstellung');
      }
    } catch (error) {
      console.error('Fehler:', error);
      alert('Fehler bei der Protokoll-Erstellung');
    } finally {
      setCreating(false);
    }
  };

  // Download-Funktion
  const downloadFile = async (protocolId, fileType, protocolTitle) => {
    try {
      const response = await fetch(`http://localhost:5000/download/${protocolId}/${fileType}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${protocolTitle}_protokoll.${fileType}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Datei nicht gefunden oder Download-Fehler');
      }
    } catch (error) {
      console.error('Download-Fehler:', error);
      alert('Fehler beim Download');
    }
  };

  useEffect(() => {
    checkSystemStatus();
    loadProtocols();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">System wird überprüft...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">🧪 Protokoll-Dashboard</h1>
        <p className="text-lg text-gray-600">Übersicht über Ihre Protokoll-Erstellung</p>
      </div>

      {/* System-Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${
          systemStatus.backend ? 'border-green-500' : 'border-red-500'
        }`}>
          <div className="flex items-center">
            <div className="text-3xl mr-4">{systemStatus.backend ? '✅' : '❌'}</div>
            <div>
              <h3 className="font-semibold text-lg">Backend</h3>
              <p className={systemStatus.backend ? 'text-green-600' : 'text-red-600'}>
                {systemStatus.backend ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${
          systemStatus.llm ? 'border-green-500' : 'border-red-500'
        }`}>
          <div className="flex items-center">
            <div className="text-3xl mr-4">{systemStatus.llm ? '🤖' : '❌'}</div>
            <div>
              <h3 className="font-semibold text-lg">LLM Service</h3>
              <p className={systemStatus.llm ? 'text-green-600' : 'text-red-600'}>
                {systemStatus.llm ? 'Verfügbar' : 'Nicht verfügbar'}
              </p>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${
          systemStatus.database ? 'border-green-500' : 'border-red-500'
        }`}>
          <div className="flex items-center">
            <div className="text-3xl mr-4">{systemStatus.database ? '💾' : '❌'}</div>
            <div>
              <h3 className="font-semibold text-lg">Datenbank</h3>
              <p className={systemStatus.database ? 'text-green-600' : 'text-red-600'}>
                {systemStatus.database ? 'Verbunden' : 'Getrennt'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Schnellstart */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-8 mb-8 text-white">
        <h2 className="text-2xl font-bold mb-4">🚀 Schnellstart</h2>
        <p className="mb-6 text-blue-100">Erstellen Sie in wenigen Schritten ein professionelles Laborprotokoll</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div className="text-2xl mb-2">📤</div>
            <h3 className="font-semibold mb-1">1. Upload</h3>
            <p className="text-sm text-blue-100">Labornotizen hochladen</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div className="text-2xl mb-2">🤖</div>
            <h3 className="font-semibold mb-1">2. Generierung</h3>
            <p className="text-sm text-blue-100">KI erstellt das Protokoll</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div className="text-2xl mb-2">📄</div>
            <h3 className="font-semibold mb-1">3. Download</h3>
            <p className="text-sm text-blue-100">PDF/LaTeX herunterladen</p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg"
        >
          ✨ Neues Protokoll erstellen
        </button>
      </div>

      {/* Protokoll-Liste */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">📋 Meine Protokolle</h2>
            <button
              onClick={loadProtocols}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              🔄 Aktualisieren
            </button>
          </div>
        </div>

        {protocols.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">Noch keine Protokolle</h3>
            <p className="text-gray-500 mb-6">Erstellen Sie Ihr erstes Protokoll, um hier zu starten</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Erstes Protokoll erstellen
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {protocols.map((protocol) => (
              <div key={protocol.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-lg font-semibold text-gray-900 mr-3">
                        {protocol.title}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        protocol.status === 'completed' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {protocol.status === 'completed' ? '✅ Fertig' : '⏳ In Bearbeitung'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Erstellt: {new Date(protocol.created_at).toLocaleDateString('de-DE')}
                    </p>
                  </div>
                  
                  {protocol.status === 'completed' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => downloadFile(protocol.id, 'pdf', protocol.title)}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
                      >
                        📄 PDF
                      </button>
                      <button
                        onClick={() => downloadFile(protocol.id, 'latex', protocol.title)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                      >
                        📝 LaTeX
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Protokoll-Erstellungs-Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">✨ Neues Protokoll erstellen</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titel des Protokolls
                </label>
                <input
                  type="text"
                  value={createForm.title}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  placeholder="z.B. Säure-Base-Titration"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Beschreibung (optional)
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Kurze Beschreibung des Versuchs..."
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                disabled={creating}
              >
                Abbrechen
              </button>
              <button
                onClick={createProtocol}
                disabled={creating}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {creating ? '⏳ Erstellen...' : '🚀 Protokoll erstellen'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 