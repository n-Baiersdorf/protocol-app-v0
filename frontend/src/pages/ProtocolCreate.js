import React, { useState, useEffect } from 'react';

const PROTOCOL_SECTIONS = [
  { key: 'title', label: 'Titel', placeholder: 'z.B. Säure-Base-Titration zur Konzentrationsbestimmung' },
  { key: 'motivation', label: 'Motivation/Zielsetzung', placeholder: 'Was soll mit diesem Experiment erreicht werden?', multiline: true },
  { key: 'theorie', label: 'Theoretischer Hintergrund', placeholder: 'Relevante chemische/physikalische Grundlagen...', multiline: true },
  { key: 'materialien', label: 'Materialien und Geräte', placeholder: '- Bürette (50 mL)\n- Erlenmeyerkolben (250 mL)\n- NaOH 0.1 mol/L...', multiline: true },
  { key: 'durchfuehrung', label: 'Durchführung', placeholder: '1. Bürette mit NaOH-Lösung füllen\n2. Probelösung in Erlenmeyerkolben geben...', multiline: true },
  { key: 'ergebnisse', label: 'Ergebnisse und Beobachtungen', placeholder: 'Verbrauch NaOH: 23.5 mL\nFarbumschlag: farblos → rosa...', multiline: true },
  { key: 'berechnungen', label: 'Berechnungen und Auswertung', placeholder: 'c(HCl) = c(NaOH) × V(NaOH) / V(HCl)...', multiline: true },
  { key: 'diskussion', label: 'Diskussion', placeholder: 'Die ermittelte Konzentration liegt im erwarteten Bereich...', multiline: true },
  { key: 'schlussfolgerung', label: 'Schlussfolgerung', placeholder: 'Das Experiment zeigt erfolgreich...', multiline: true }
];

const ProtocolCreate = () => {
  const [formData, setFormData] = useState({});
  const [previewMode, setPreviewMode] = useState('latex'); // 'latex' oder 'pdf'
  const [previewContent, setPreviewContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');

  // Auto-Save Funktionalität
  useEffect(() => {
    const timer = setTimeout(() => {
      if (Object.keys(formData).length > 0) {
        autoSave();
      }
    }, 2000);
    return () => clearTimeout(timer);
  }, [formData]);

  const autoSave = () => {
    setSaveStatus('💾 Automatisch gespeichert...');
    // TODO: Backend Auto-Save implementieren
    setTimeout(() => setSaveStatus(''), 2000);
  };

  const handleInputChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const generatePreview = async () => {
    setIsGenerating(true);
    try {
      // TODO: Backend-Integration für Preview-Generierung
      const mockLatex = `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[german]{babel}

\\title{${formData.title || 'Protokoll-Titel'}}
\\author{Laborprotokoll}
\\date{\\today}

\\begin{document}
\\maketitle

${formData.motivation ? `\\section{Zielsetzung}\n${formData.motivation}\n` : ''}
${formData.theorie ? `\\section{Theoretischer Hintergrund}\n${formData.theorie}\n` : ''}
${formData.materialien ? `\\section{Materialien und Geräte}\n${formData.materialien}\n` : ''}
${formData.durchfuehrung ? `\\section{Durchführung}\n${formData.durchfuehrung}\n` : ''}
${formData.ergebnisse ? `\\section{Ergebnisse}\n${formData.ergebnisse}\n` : ''}
${formData.berechnungen ? `\\section{Berechnungen}\n${formData.berechnungen}\n` : ''}
${formData.diskussion ? `\\section{Diskussion}\n${formData.diskussion}\n` : ''}
${formData.schlussfolgerung ? `\\section{Schlussfolgerung}\n${formData.schlussfolgerung}\n` : ''}

\\end{document}`;
      
      setPreviewContent(mockLatex);
    } catch (error) {
      console.error('Preview-Generierung fehlgeschlagen:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const importFiles = () => {
    // TODO: Datei-Import implementieren
    alert('Import-Funktionalität wird implementiert...');
  };

  const generateFullProtocol = () => {
    // TODO: Vollständige Protokoll-Generierung
    alert('Vollständige Protokoll-Generierung wird implementiert...');
  };

  return (
    <div className="max-w-full mx-auto h-screen flex flex-col">
      {/* TEST-INDIKATOR */}
      <div className="bg-green-500 text-white text-center py-2 font-bold">
        🎉 NEUES LAYOUT AKTIV - 2-SPALTIG WIE IN DER SKIZZE! 🎉
      </div>
      
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">✍️ Protokoll-Erstellen</h1>
            <p className="text-gray-600">Erstellen Sie Ihr Laborprotokoll mit Live-Vorschau</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">{saveStatus}</span>
            <button
              onClick={generateFullProtocol}
              className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors"
            >
              📄 Protokoll generieren
            </button>
          </div>
        </div>
      </div>

      {/* Hauptbereich - 2-spaltig */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Linke Spalte - Formular */}
        <div className="w-1/2 bg-gray-50 overflow-y-auto">
          <div className="p-6 space-y-6">
            {PROTOCOL_SECTIONS.map((section) => (
              <div key={section.key} className="bg-white rounded-lg shadow p-4">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  {section.label}
                </label>
                
                {section.multiline ? (
                  <textarea
                    value={formData[section.key] || ''}
                    onChange={(e) => handleInputChange(section.key, e.target.value)}
                    placeholder={section.placeholder}
                    className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  />
                ) : (
                  <input
                    type="text"
                    value={formData[section.key] || ''}
                    onChange={(e) => handleInputChange(section.key, e.target.value)}
                    placeholder={section.placeholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                )}
              </div>
            ))}

            {/* Import-Bereich */}
            <div className="bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-6 text-center">
              <button
                onClick={importFiles}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                📁 Import...
              </button>
              <p className="text-sm text-blue-600 mt-2">
                Labornotizen, Messdaten, Bilder importieren
              </p>
            </div>
          </div>
        </div>

        {/* Rechte Spalte - Vorschau */}
        <div className="w-1/2 bg-white border-l border-gray-200 flex flex-col">
          
          {/* Vorschau-Header */}
          <div className="border-b border-gray-200 p-4">
            <div className="flex justify-between items-center">
              <div className="flex space-x-4">
                <button
                  onClick={() => setPreviewMode('latex')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    previewMode === 'latex'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  LaTeX
                </button>
                <button
                  onClick={() => setPreviewMode('pdf')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    previewMode === 'pdf'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  PDF
                </button>
              </div>
              
              <button
                onClick={generatePreview}
                disabled={isGenerating}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {isGenerating ? '⏳ Generiere...' : '🔄 Vorschau aktualisieren'}
              </button>
            </div>
          </div>

          {/* Vorschau-Inhalt */}
          <div className="flex-1 overflow-y-auto p-4">
            {previewMode === 'latex' ? (
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                <pre className="whitespace-pre-wrap">
                  {previewContent || 'Klicken Sie auf "Vorschau aktualisieren" um LaTeX-Code zu generieren...'}
                </pre>
              </div>
            ) : (
              <div className="bg-gray-100 rounded-lg p-8 text-center">
                <div className="text-6xl text-gray-400 mb-4">📄</div>
                <p className="text-gray-600">PDF-Vorschau wird implementiert...</p>
                <p className="text-sm text-gray-500 mt-2">
                  Hier wird das kompilierte PDF angezeigt
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProtocolCreate; 