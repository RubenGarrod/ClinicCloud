import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ResultsPage.css';

const ResultsPage = ({ query, results, isLoading, onSearch, onSelectDocument, selectedDocument }) => {
  const [searchInput, setSearchInput] = useState(query);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSearch(searchInput);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Fecha no disponible';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="results-page">
      <div className="results-header">
        <h1>Resultados de Búsqueda</h1>
        <h2>"{query}"</h2>
        
        <form onSubmit={handleSubmit} className="results-search-form">
          <div className="results-search-input-container">
            <input
              type="text"
              className="results-search-input"
              placeholder="Buscar documentación clínica..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              aria-label="Campo de búsqueda"
            />
            <button 
              type="submit" 
              className="results-search-button"
              disabled={isLoading || !searchInput.trim()}
              aria-label="Buscar"
            >
              {isLoading ? (
                <span className="loader"></span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>

      <div className="results-content">
        {isLoading ? (
          <div className="results-loading">
            <span className="loader-large"></span>
            <p>Buscando documentos...</p>
          </div>
        ) : results.length === 0 ? (
          <div className="no-results">
            <p>No se encontraron resultados para tu búsqueda.</p>
            <p>Intenta con otros términos o revisa la ortografía.</p>
          </div>
        ) : (
          <div className="results-layout">
            <div className="results-list">
              {results.map((doc) => (
                <div 
                  key={doc.id} 
                  className={`result-item ${selectedDocument && selectedDocument.id === doc.id ? 'selected' : ''}`}
                  onClick={() => onSelectDocument(doc)}
                >
                  <div className="result-category">
                    {doc.categoria ? doc.categoria.nombre : 'Sin categoría'}
                  </div>
                  <h3 className="result-title">{doc.titulo}</h3>
                  <div className="result-meta">
                    <span className="result-authors">
                      {doc.autor && doc.autor.length > 0 
                        ? doc.autor.join(', ') 
                        : 'Autor desconocido'}
                    </span>
                    <span className="result-date">
                      {formatDate(doc.fecha_publicacion)}
                    </span>
                  </div>
                  <p className="result-summary">
                    {doc.texto_resumen || 'No hay resumen disponible para este documento.'}
                  </p>
                  <a 
                    href={doc.url_fuente} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="result-link"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Ir a la fuente
                  </a>
                </div>
              ))}
            </div>
            
            {/* Panel de vista previa para la versión de escritorio */}
            {selectedDocument && (
              <div className="preview-panel">
                <div className="preview-header">
                  <h3>{selectedDocument.titulo}</h3>
                  <div className="preview-meta">
                    <span className="preview-category">
                      {selectedDocument.categoria ? selectedDocument.categoria.nombre : 'Sin categoría'}
                    </span>
                    <span className="preview-date">
                      {formatDate(selectedDocument.fecha_publicacion)}
                    </span>
                  </div>
                </div>
                <div className="preview-content">
                  <p className="preview-authors">
                    <strong>Autores:</strong> {selectedDocument.autor && selectedDocument.autor.length > 0 
                      ? selectedDocument.autor.join(', ') 
                      : 'Autor desconocido'}
                  </p>
                  <div className="preview-summary">
                    <h4>Resumen:</h4>
                    <p>{selectedDocument.texto_resumen || 'No hay resumen disponible.'}</p>
                  </div>
                  <a 
                    href={selectedDocument.url_fuente} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="preview-button"
                  >
                    Ver documento completo
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;