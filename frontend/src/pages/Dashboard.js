import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [status, setStatus] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    // Backend-Status prüfen
    fetch('/health')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error('Backend nicht erreichbar:', err));
  }, []);

  const handleTestLLM = async () => {
    setIsGenerating(true);
    setTestResult(null);
    
    try {
      const response = await fetch('/test-llm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Dashboard Test-Protokoll',
          author: 'Frontend User',
          experiment_type: 'LLM-Funktionstest'
        })
      });
      
      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleTestPDF = async () => {
    if (!testResult?.protocol_id) return;
    
    try {
      const response = await fetch(`/test-simple-pdf`, {
        method: 'POST'
      });
      
      const result = await response.json();
      alert(result.success ? 
        `PDF erfolgreich generiert! (${Math.round(result.pdf_size/1024)}KB)` : 
        'PDF-Generierung fehlgeschlagen'
      );
    } catch (error) {
      alert('Fehler bei PDF-Generierung: ' + error.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Übersicht über Ihre Protokoll-Erstellung</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
              🖥️
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Backend</h3>
              <p className={`text-sm ${status?.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                {status?.status === 'healthy' ? '✅ Online' : '❌ Offline'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 text-purple-600 mr-4">
              🧠
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">LLM Service</h3>
              <p className={`text-sm ${status?.services?.llm ? 'text-green-600' : 'text-red-600'}`}>
                {status?.services?.llm ? '✅ Verfügbar' : '❌ Nicht verfügbar'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600 mr-4">
              🗄️
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Datenbank</h3>
              <p className={`text-sm ${status?.services?.database ? 'text-green-600' : 'text-red-600'}`}>
                {status?.services?.database ? '✅ Verbunden' : '❌ Getrennt'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* LLM Test Section */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🧪 LLM-Funktionstest</h2>
        <p className="text-gray-600 mb-4">
          Teste die Ende-zu-Ende-Protokoll-Generierung von der LLM-Erstellung bis zur PDF-Ausgabe.
        </p>
        
        <div className="flex space-x-4 mb-4">
          <button
            onClick={handleTestLLM}
            disabled={isGenerating || !status?.services?.llm}
            className={`px-4 py-2 rounded-md font-medium ${
              isGenerating || !status?.services?.llm
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isGenerating ? '🔄 Generiere...' : '📝 Protokoll generieren'}
          </button>
          
          {testResult?.success && (
            <button
              onClick={handleTestPDF}
              className="px-4 py-2 bg-green-600 text-white rounded-md font-medium hover:bg-green-700"
            >
              📄 PDF erstellen
            </button>
          )}
        </div>

        {testResult && (
          <div className={`p-4 rounded-md ${
            testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <h3 className="font-semibold mb-2">
              {testResult.success ? '✅ Erfolgreich!' : '❌ Fehler'}
            </h3>
            {testResult.success ? (
              <div>
                <p><strong>Protokoll ID:</strong> {testResult.protocol_id}</p>
                <p><strong>Inhaltslänge:</strong> {testResult.full_content_length} Zeichen</p>
                <div className="mt-2">
                  <strong>Vorschau:</strong>
                  <pre className="text-sm bg-white p-2 rounded border mt-1 overflow-x-auto">
                    {testResult.generated_content}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-red-800">{testResult.error || testResult.message}</p>
            )}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Schnellstart</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/upload"
            className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
              📤
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Neues Protokoll</h3>
              <p className="text-sm text-gray-600">Dateien hochladen und Protokoll generieren</p>
            </div>
          </a>
          
          <a
            href="/protocols"
            className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="p-3 rounded-full bg-green-100 text-green-600 mr-4">
              📄
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Protokolle verwalten</h3>
              <p className="text-sm text-gray-600">Bestehende Protokolle anzeigen und bearbeiten</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 