import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Search } from 'lucide-react';
import Button from './ui/Button';
import clinicLogo from '../assets/clinic-cloud-logo.png';
import { sanitizeInput } from '../utils/sanitization';

const SearchPage = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();

  // Detectar si hay un parámetro de búsqueda en la URL (desde historial)
  useEffect(() => {
    const urlQuery = searchParams.get('q');
    if (urlQuery) {
      setQuery(urlQuery);
      // Ejecutar la búsqueda automáticamente
      onSearch(urlQuery);
      navigate('/results');
    }
  }, [searchParams, onSearch, navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const sanitizedQuery = sanitizeInput(query);
    if (sanitizedQuery.trim()) {
      onSearch(sanitizedQuery);
      navigate('/results');
    }
  };

  const handleQueryChange = (e) => {
    // No sanitizar mientras escribe, solo al enviar
    setQuery(e.target.value);
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-8 md:py-12">
      <div className="w-full max-w-4xl text-center">
        {/* Logo */}
        <div className="mb-8">
          <img 
            src={clinicLogo} 
            alt="Clinic Cloud Logo" 
            className="w-64 sm:w-80 md:w-96 lg:w-[26rem] xl:w-[28rem] h-auto mx-auto mb-6 max-w-full"
          />
        </div>
        
        {/* Search Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex max-w-lg mx-auto">
            <div className="relative flex-1">
              <input
                type="text"
                className="w-full px-4 py-3 text-lg border border-gray-300 dark:border-gray-600 rounded-l-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder={t('search.placeholder')}
                value={query}
                onChange={handleQueryChange}
                aria-label="Campo de búsqueda"
              />
            </div>
            <Button
              type="submit"
              size="lg"
              disabled={isLoading || !query.trim()}
              loading={isLoading}
              className="rounded-l-none border-l-0"
              aria-label={t('search.button')}
            >
              <Search className="w-5 h-5" />
            </Button>
          </div>
        </form>

        {/* Quick suggestions or additional content can go here */}
        <div className="text-sm text-gray-500 dark:text-gray-400">
          <p>{t('search.description', 'Accede a miles de documentos médicos desde un único punto')}</p>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;