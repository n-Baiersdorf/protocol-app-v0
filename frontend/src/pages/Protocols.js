import React, { useState, useEffect } from 'react';

const Protocols = () => {
  const [protocols, setProtocols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest');

  // Protokolle laden
  const loadProtocols = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/protocols');
      if (response.ok) {
        const data = await response.json();
        setProtocols(data.protocols || []);
      }
    } catch (error) {
      console.error('Fehler beim Laden der Protokolle:', error);
    } finally {
      setLoading(false);
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
        // Versuche PDF zu regenerieren falls nicht vorhanden
        if (fileType === 'pdf') {
          const regenerateResponse = await fetch(`http://localhost:5000/test-pdf/${protocolId}`, {
            method: 'POST'
          });
          if (regenerateResponse.ok) {
            // Versuche Download erneut nach kurzer Wartezeit
            setTimeout(() => downloadFile(protocolId, fileType, protocolTitle), 2000);
            return;
          }
        }
        alert('Datei nicht gefunden oder Download-Fehler');
      }
    } catch (error) {
      console.error('Download-Fehler:', error);
      alert('Fehler beim Download');
    }
  };

  // Bulk-Download-Funktionen
  const downloadAllPDFs = async () => {
    try {
      const response = await fetch('http://localhost:5000/bulk-download/pdf');
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `alle_protokolle_pdfs_${new Date().toISOString().slice(0,10)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Fehler beim Bulk-Download der PDFs');
      }
    } catch (error) {
      console.error('Bulk-Download-Fehler:', error);
      alert('Fehler beim Bulk-Download');
    }
  };

  const downloadAllLaTeX = async () => {
    try {
      const response = await fetch('http://localhost:5000/bulk-download/latex');
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `alle_protokolle_latex_${new Date().toISOString().slice(0,10)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Fehler beim Bulk-Download der LaTeX-Dateien');
      }
    } catch (error) {
      console.error('Bulk-Download-Fehler:', error);
      alert('Fehler beim Bulk-Download');
    }
  };

  // Protokolle filtern und sortieren
  const getFilteredProtocols = () => {
    let filtered = protocols;

    // Nach Suchbegriff filtern
    if (searchTerm) {
      filtered = filtered.filter(protocol =>
        protocol.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Nach Status filtern
    if (filterStatus !== 'all') {
      filtered = filtered.filter(protocol => protocol.status === filterStatus);
    }

    // Sortieren
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  useEffect(() => {
    loadProtocols();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Protokolle werden geladen...</p>
        </div>
      </div>
    );
  }

  const filteredProtocols = getFilteredProtocols();

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">📋 Protokoll-Verwaltung</h1>
        <p className="text-lg text-gray-600">Verwalten Sie Ihre generierten Laborprotokolle</p>
      </div>

      {/* Statistiken */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="text-3xl mr-4">📄</div>
            <div>
              <h3 className="font-semibold text-lg">Gesamt</h3>
              <p className="text-2xl font-bold text-blue-600">{protocols.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="text-3xl mr-4">✅</div>
            <div>
              <h3 className="font-semibold text-lg">Fertig</h3>
              <p className="text-2xl font-bold text-green-600">
                {protocols.filter(p => p.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500">
          <div className="flex items-center">
            <div className="text-3xl mr-4">⏳</div>
            <div>
              <h3 className="font-semibold text-lg">In Arbeit</h3>
              <p className="text-2xl font-bold text-yellow-600">
                {protocols.filter(p => p.status === 'draft').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="text-3xl mr-4">📅</div>
            <div>
              <h3 className="font-semibold text-lg">Heute</h3>
              <p className="text-2xl font-bold text-purple-600">
                {protocols.filter(p => 
                  new Date(p.created_at).toDateString() === new Date().toDateString()
                ).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter und Suche */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Suche */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🔍 Suche
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Protokoll-Titel suchen..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Status-Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🎯 Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Alle Status</option>
              <option value="completed">✅ Fertig</option>
              <option value="draft">⏳ In Arbeit</option>
            </select>
          </div>

          {/* Sortierung */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🔄 Sortierung
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="newest">Neueste zuerst</option>
              <option value="oldest">Älteste zuerst</option>
              <option value="title">Alphabetisch</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <p className="text-sm text-gray-600">
            {filteredProtocols.length} von {protocols.length} Protokollen angezeigt
          </p>
          <button
            onClick={loadProtocols}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            🔄 Aktualisieren
          </button>
        </div>
      </div>

      {/* Protokoll-Liste */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {filteredProtocols.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              {searchTerm || filterStatus !== 'all' 
                ? 'Keine Protokolle gefunden' 
                : 'Noch keine Protokolle'}
            </h3>
            <p className="text-gray-500 mb-6">
              {searchTerm || filterStatus !== 'all'
                ? 'Versuchen Sie andere Suchkriterien'
                : 'Erstellen Sie Ihr erstes Protokoll im Dashboard'}
            </p>
            {!(searchTerm || filterStatus !== 'all') && (
              <a
                href="/dashboard"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
              >
                Erstes Protokoll erstellen
              </a>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredProtocols.map((protocol) => (
              <div key={protocol.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-xl font-semibold text-gray-900 mr-3">
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
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                      <div className="flex items-center">
                        <span className="mr-2">📅</span>
                        <span>Erstellt: {formatDate(protocol.created_at)}</span>
                      </div>
                      <div className="flex items-center">
                        <span className="mr-2">🔄</span>
                        <span>Aktualisiert: {formatDate(protocol.updated_at)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {protocol.status === 'completed' && (
                    <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 ml-4">
                      <button
                        onClick={() => downloadFile(protocol.id, 'pdf', protocol.title)}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors flex items-center"
                      >
                        📄 PDF
                      </button>
                      <button
                        onClick={() => downloadFile(protocol.id, 'latex', protocol.title)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center"
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

      {/* Bulk-Aktionen für fertige Protokolle */}
      {protocols.filter(p => p.status === 'completed').length > 1 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="font-semibold text-blue-900 mb-4">📦 Bulk-Aktionen</h3>
          <p className="text-blue-800 text-sm mb-4">
            Sie haben {protocols.filter(p => p.status === 'completed').length} fertige Protokolle
          </p>
          <div className="flex space-x-4">
            <button
              onClick={downloadAllPDFs}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              📥 Alle PDFs herunterladen
            </button>
            <button
              onClick={downloadAllLaTeX}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
            >
              📋 Alle LaTeX-Dateien herunterladen
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Protocols; 