import React from 'react';
import './Footer.css';
import miniLogo from '../assets/clinic-cloud-icon.png';

const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-section footer-logo-section">
          <img src={miniLogo} alt="Clinic Cloud Icon" className="footer-logo" />
          <p className="footer-tagline">
            Democratizando el acceso a la información médica
          </p>
        </div>
        
        <div className="footer-section footer-links">
          <h4>Enlaces</h4>
          <ul>
            <li><a href="#about">Acerca de</a></li>
            <li><a href="#terms">Términos de uso</a></li>
            <li><a href="#privacy">Política de privacidad</a></li>
            <li><a href="https://github.com/yourusername/clinic-cloud" target="_blank" rel="noopener noreferrer">GitHub</a></li>
          </ul>
        </div>
        
        <div className="footer-section footer-contact">
          <h4>Contacto</h4>
          <ul>
            <li><a href="mailto:contacto@cliniccloud.org">contacto@cliniccloud.org</a></li>
            <li><a href="https://github.com/yourusername/clinic-cloud/issues" target="_blank" rel="noopener noreferrer">Reportar un problema</a></li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} Clinic Cloud. Código abierto bajo licencia GPL v3.</p>
      </div>
    </footer>
  );
};

export default Footer;