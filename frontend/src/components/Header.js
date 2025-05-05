// Header.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';
import logo from '../assets/clinic-cloud-logo.png';

const Header = () => {
  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="header-logo-container">
          <img src={logo} alt="Clinic Cloud Logo" className="header-logo" />
          <span className="header-title">Clinic Cloud</span>
        </Link>
        <nav className="header-nav">
          <a href="https://github.com/yourusername/clinic-cloud" target="_blank" rel="noopener noreferrer">
            Código Fuente
          </a>
          <a href="#about">Acerca de</a>
          <a href="#help">Ayuda</a>
        </nav>
      </div>
    </header>
  );
};

export default Header;
