import React, { useState, useRef } from 'react';

const Upload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) {
      setError('Bitte wählen Sie mindestens eine Datei aus');
      return;
    }

    setUploading(true);
    setError('');
    const formData = new FormData();
    
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload fehlgeschlagen');
      }

      const result = await response.json();
      setUploadedFiles(result.files);
      setSelectedFiles([]);
      setError('');
    } catch (err) {
      setError(err.message || 'Fehler beim Upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">📤 Datei-Upload</h1>
        <p className="text-lg text-gray-600">Laden Sie Ihre Labornotizen und Versuchsdaten hoch</p>
      </div>

      {/* Upload-Bereich */}
      <div className="bg-white rounded-xl shadow-lg border-2 border-dashed border-gray-300 p-8 mb-8 transition-all duration-200 hover:border-blue-400">
        <div
          className={`${dragActive ? 'border-blue-500 bg-blue-50' : ''} 
                     border-2 border-dashed border-gray-300 rounded-lg p-8 text-center 
                     transition-all duration-200 cursor-pointer`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="text-6xl mb-4">📁</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Dateien hier ablegen oder klicken zum Auswählen
          </h3>
          <p className="text-gray-500 mb-4">
            Unterstützte Formate: PDF, DOCX, TXT, JPG, PNG, CSV, XLS, XLSX
          </p>
          <div className="flex flex-wrap gap-2 justify-center text-sm text-gray-600">
            <span className="bg-gray-100 px-3 py-1 rounded-full">📄 Dokumente</span>
            <span className="bg-gray-100 px-3 py-1 rounded-full">📷 Bilder</span>
            <span className="bg-gray-100 px-3 py-1 rounded-full">📊 Tabellen</span>
            <span className="bg-gray-100 px-3 py-1 rounded-full">✍️ Handschrift</span>
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.jpg,.jpeg,.png,.csv,.xls,.xlsx"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Ausgewählte Dateien */}
      {selectedFiles.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            Ausgewählte Dateien ({selectedFiles.length})
          </h3>
          <div className="space-y-3">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">
                    {file.type.startsWith('image/') ? '🖼️' : 
                     file.type.includes('pdf') ? '📄' :
                     file.type.includes('sheet') || file.type.includes('csv') ? '📊' : '📋'}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700 text-xl"
                >
                  ❌
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-between items-center">
            <button
              onClick={() => setSelectedFiles([])}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Alle entfernen
            </button>
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? '⏳ Wird hochgeladen...' : `📤 ${selectedFiles.length} Dateien hochladen`}
            </button>
          </div>
        </div>
      )}

      {/* Fehler-Anzeige */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <span className="text-red-500 text-xl mr-2">⚠️</span>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Hochgeladene Dateien */}
      {uploadedFiles.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-green-800 mb-4">
            ✅ Erfolgreich hochgeladen ({uploadedFiles.length})
          </h3>
          <div className="space-y-3">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-white rounded-lg border border-green-200">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">
                    {file.type === 'image' ? '🖼️' : 
                     file.type === 'pdf' ? '📄' :
                     file.type === 'spreadsheet' ? '📊' : '📋'}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {file.size && formatFileSize(file.size)}
                      {file.extracted_text && ' • OCR-Text erkannt'}
                    </p>
                  </div>
                </div>
                <span className="text-green-600 text-xl">✅</span>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-blue-800 font-medium">🚀 Nächster Schritt:</p>
            <p className="text-blue-700 text-sm mt-1 mb-3">
              Ihre Dateien wurden erfolgreich verarbeitet. Sie können jetzt ein Protokoll generieren lassen.
            </p>
            
            <ProtocolGenerator uploadedFiles={uploadedFiles} />
          </div>
        </div>
      )}
    </div>
  );
};

// Protocol Generator Komponente
const ProtocolGenerator = ({ uploadedFiles }) => {
  const [generating, setGenerating] = useState(false);
  const [protocolTitle, setProtocolTitle] = useState('');
  const [protocolDescription, setProtocolDescription] = useState('');
  const [generatedProtocol, setGeneratedProtocol] = useState(null);

  const generateProtocol = async () => {
    if (!protocolTitle.trim()) {
      alert('Bitte geben Sie einen Protokoll-Titel ein');
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: protocolTitle,
          metadata: { description: protocolDescription },
          files: uploadedFiles.map(file => ({
            name: file.name,
            type: file.type,
            content: file.extracted_text || `Datei: ${file.name}`,
            size: file.size
          }))
        })
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedProtocol(result);
        
        // PDF automatisch generieren
        setTimeout(async () => {
          try {
            await fetch(`http://localhost:5000/test-pdf/${result.protocol_id}`, {
              method: 'POST'
            });
          } catch (e) {
            console.warn('PDF-Generierung fehlgeschlagen:', e);
          }
        }, 1000);
        
      } else {
        throw new Error('Protokoll-Generierung fehlgeschlagen');
      }
    } catch (error) {
      console.error('Fehler:', error);
      alert('Fehler bei der Protokoll-Generierung');
    } finally {
      setGenerating(false);
    }
  };

  const downloadFile = async (protocolId, fileType) => {
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
        alert('Download-Fehler - Datei wurde möglicherweise noch nicht generiert');
      }
    } catch (error) {
      console.error('Download-Fehler:', error);
      alert('Fehler beim Download');
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-blue-700 mb-2">
            Protokoll-Titel *
          </label>
          <input
            type="text"
            value={protocolTitle}
            onChange={(e) => setProtocolTitle(e.target.value)}
            className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="z.B. Säure-Base-Titration"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-blue-700 mb-2">
            Beschreibung (optional)
          </label>
          <input
            type="text"
            value={protocolDescription}
            onChange={(e) => setProtocolDescription(e.target.value)}
            className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="Kurze Beschreibung..."
          />
        </div>
      </div>

      <button
        onClick={generateProtocol}
        disabled={generating || !protocolTitle.trim()}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {generating ? '⏳ Protokoll wird generiert...' : '🚀 Protokoll aus hochgeladenen Dateien generieren'}
      </button>

      {generatedProtocol && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-semibold text-green-800 mb-2">
            ✅ Protokoll erfolgreich erstellt!
          </h4>
          <p className="text-green-700 text-sm mb-3">
            Protokoll ID: {generatedProtocol.protocol_id} | Titel: "{protocolTitle}"
          </p>
          <div className="flex space-x-3">
            <button
              onClick={() => downloadFile(generatedProtocol.protocol_id, 'pdf')}
              className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
            >
              📄 PDF herunterladen
            </button>
            <button
              onClick={() => downloadFile(generatedProtocol.protocol_id, 'latex')}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
            >
              📝 LaTeX herunterladen
            </button>
            <a
              href="/protocols"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              📋 Zu Protokoll-Verwaltung
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload; 