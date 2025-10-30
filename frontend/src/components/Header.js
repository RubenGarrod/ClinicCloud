import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import './Header.css';
import logo from '../assets/clinic-cloud-icon.png';

const Header = () => {
  const { t } = useTranslation();
  
  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="header-logo-container">
          <img src={logo} alt="Clinic Cloud Logo" className="header-logo" />
          <span className="header-title">Clinic Cloud</span>
        </Link>
        
        <div className="header-right">
          <nav className="header-nav">
            <a href="https://github.com/RubenGarrod/ClinicCloud" target="_blank" rel="noopener noreferrer">
              {t('header.source')}
            </a>
            <a href="#about">{t('header.about')}</a>
            <a href="#help">{t('header.help')}</a>
          </nav>
          
          {/* El selector de idiomas ahora está fuera del nav para evitar que se oculte en móvil */}
          <LanguageSelector />
        </div>
      </div>
    </header>
  );
};

export default Header;