import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Github, Mail, AlertCircle, FileText, Shield, Info } from 'lucide-react';
import AboutModal from './AboutModal';
import ReportIssueModal from './ReportIssueModal';
import miniLogo from '../assets/clinic-cloud-icon.png';

const Footer = () => {
  const { t } = useTranslation();
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
  const [isReportIssueModalOpen, setIsReportIssueModalOpen] = useState(false);

  return (
    <>
      <footer className="bg-transparent mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
            {/* Links */}
            <div className="flex flex-wrap items-center space-x-6">
              <button
                onClick={() => setIsAboutModalOpen(true)}
                className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <Info className="w-3 h-3 mr-1" />
                {t('footer.links.about', 'Acerca de')}
              </button>
              <Link
                to="/terms"
                className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <FileText className="w-3 h-3 mr-1" />
                {t('footer.links.terms', 'Términos')}
              </Link>
              <Link
                to="/privacy"
                className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <Shield className="w-3 h-3 mr-1" />
                {t('footer.links.privacy', 'Privacidad')}
              </Link>
          </div>
          
          {/* Contact Links */}
          <div className="flex items-center space-x-4">
            <a
              href="mailto:cliniccloud.contact@gmail.com"
              className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
            >
              <Mail className="w-4 h-4 mr-1" />
              {t('footer.links.contact', 'Contacto')}
            </a>
            <a 
              href="https://github.com/RubenGarrod/ClinicCloud" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
            >
              <Github className="w-4 h-4 mr-1" />
              {t('footer.links.github', 'GitHub')}
            </a>
            <button
              onClick={() => setIsReportIssueModalOpen(true)}
              className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {t('footer.links.report', 'Reportar problema')}
            </button>
          </div>
        </div>
        
        <div className="mt-4 pt-4">
          <p className="text-center text-xs text-gray-500 dark:text-gray-400">
            © {new Date().getFullYear()} Clinic Cloud. {t('footer.rights', 'Todos los derechos reservados.')}
          </p>
        </div>
      </div>
    </footer>

    {/* About Modal */}
    <AboutModal
      isOpen={isAboutModalOpen}
      onClose={() => setIsAboutModalOpen(false)}
    />

    {/* Report Issue Modal */}
    <ReportIssueModal
      isOpen={isReportIssueModalOpen}
      onClose={() => setIsReportIssueModalOpen(false)}
    />
    </>
  );
};

export default Footer;