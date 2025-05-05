import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SearchPage.css';
import clinicLogo from '../assets/clinic-cloud-logo.png';

const SearchPage = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
      navigate('/results');
    }
  };

  return (
    <div className="search-page">
      <div className="search-container">
        <div className="logo-container">
          <img src={clinicLogo} alt="Clinic Cloud Logo" className="logo" />
          <h1 className="app-title">Clinic Cloud</h1>
        </div>
        
        <form onSubmit={handleSubmit} className="search-form">
          <div className="search-input-container">
            <input
              type="text"
              className="search-input"
              placeholder="Buscar documentación clínica..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Campo de búsqueda"
            />
            <button 
              type="submit" 
              className="search-button"
              disabled={isLoading || !query.trim()}
              aria-label="Buscar"
            >
              {isLoading ? (
                <span className="loader"></span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              )}
            </button>
          </div>
        </form>
        
        <p className="search-description">
          Accede a miles de documentos médicos desde un único punto y con resúmenes generados por IA
        </p>
      </div>
    </div>
  );
};

export default SearchPage;