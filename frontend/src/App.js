import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './components/SearchPage';
import ResultsPage from './components/ResultsPage';
import Header from './components/Header';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setSearchQuery(query);
    
    try {
      // Conectar con la API de búsqueda
      const response = await fetch('http://localhost:8000/api/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          limit: 20,
          offset: 0
        }),
      });

      if (!response.ok) {
        throw new Error('Error en la búsqueda');
      }

      const data = await response.json();
      setSearchResults(data.results);
    } catch (error) {
      console.error('Error:', error);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={
              <SearchPage 
                onSearch={handleSearch} 
                isLoading={isLoading} 
              />
            } />
            <Route path="/results" element={
              <ResultsPage 
                query={searchQuery}
                results={searchResults}
                isLoading={isLoading}
                onSearch={handleSearch}
                onSelectDocument={setSelectedDocument}
                selectedDocument={selectedDocument}
              />
            } />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;