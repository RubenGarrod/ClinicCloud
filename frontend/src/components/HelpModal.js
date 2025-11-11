import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { HelpCircle, Book, MessageCircle, FileText, Mail, ExternalLink } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import Modal from './ui/Modal';
import ContactModal from './ContactModal';

const HelpModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isDocumentationModalOpen, setIsDocumentationModalOpen] = useState(false);
  const [isGettingStartedModalOpen, setIsGettingStartedModalOpen] = useState(false);
  const [readmeContent, setReadmeContent] = useState('');
  const [readmeLoading, setReadmeLoading] = useState(false);
  const [readmeError, setReadmeError] = useState(false);

  // Fetch README when documentation modal opens
  useEffect(() => {
    const fetchReadme = async () => {
      if (!isDocumentationModalOpen) return;

      setReadmeLoading(true);
      setReadmeError(false);

      try {
        const response = await fetch('https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/README.md');
        if (!response.ok) throw new Error('Failed to fetch README');

        const markdown = await response.text();
        const html = marked.parse(markdown);
        const sanitizedHtml = DOMPurify.sanitize(html);

        // Post-process HTML to fix relative URLs
        const processedHtml = processReadmeHtml(sanitizedHtml);
        setReadmeContent(processedHtml);
      } catch (error) {
        console.error('Error fetching README:', error);
        setReadmeError(true);
      } finally {
        setReadmeLoading(false);
      }
    };

    fetchReadme();
  }, [isDocumentationModalOpen]);

  // Process README HTML to fix relative URLs and links
  const processReadmeHtml = (html) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const baseUrl = 'https://github.com/RubenGarrod/ClinicCloud/blob/main/';
    const rawBaseUrl = 'https://raw.githubusercontent.com/RubenGarrod/ClinicCloud/main/';

    // Fix image URLs
    doc.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src');
      if (src && !src.startsWith('http')) {
        // Use raw URL for images
        img.setAttribute('src', rawBaseUrl + src.replace(/^\.\//, ''));
      }
    });

    // Fix links
    doc.querySelectorAll('a').forEach(link => {
      const href = link.getAttribute('href');
      if (href) {
        // If it's a relative link to another file in the repo
        if (!href.startsWith('http') && !href.startsWith('#')) {
          link.setAttribute('href', baseUrl + href.replace(/^\.\//, ''));
          link.setAttribute('target', '_blank');
          link.setAttribute('rel', 'noopener noreferrer');
        }
        // If it's an anchor link (same page), remove it or make it inert
        else if (href.startsWith('#')) {
          // Remove the link functionality for anchor links since they won't work in our context
          link.removeAttribute('href');
          link.style.cursor = 'default';
          link.style.textDecoration = 'none';
        }
        // External links - ensure they open in new tab
        else if (href.startsWith('http')) {
          link.setAttribute('target', '_blank');
          link.setAttribute('rel', 'noopener noreferrer');
        }
      }
    });

    return doc.body.innerHTML;
  };

  const handleSectionClick = (index) => {
    switch(index) {
      case 0: // Getting Started
        setIsGettingStartedModalOpen(true);
        break;
      case 1: // FAQ
        alert(t('help.faqComingSoon'));
        break;
      case 2: // Documentation
        setIsDocumentationModalOpen(true);
        break;
      case 3: // Contact
        setIsContactModalOpen(true);
        break;
      default:
        // Por ahora, las otras secciones no hacen nada
        break;
    }
  };

  // Definir las secciones directamente en el render para que se actualicen con el idioma
  const helpSections = React.useMemo(() => [
    {
      icon: Book,
      title: t('help.gettingStarted'),
      description: t('help.gettingStartedDesc')
    },
    {
      icon: MessageCircle,
      title: t('help.faq'),
      description: t('help.faqDesc')
    },
    {
      icon: FileText,
      title: t('help.documentation'),
      description: t('help.documentationDesc')
    },
    {
      icon: Mail,
      title: t('help.contact'),
      description: t('help.contactDesc')
    }
  ], [t]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      showCloseButton={true}
    >
      <div className="bg-white dark:bg-gray-800">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <HelpCircle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('help.title')}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('help.subtitle')}
            </p>
          </div>
        </div>

        {/* Help Sections */}
        <div className="space-y-4 max-h-[60vh] overflow-y-auto">
          {helpSections.map((section, index) => {
            const Icon = section.icon;
            return (
              <button
                key={index}
                onClick={() => handleSectionClick(index)}
                className="w-full text-left p-4 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                      {section.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {section.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Getting Started Modal */}
        <Modal
          isOpen={isGettingStartedModalOpen}
          onClose={() => setIsGettingStartedModalOpen(false)}
          size="lg"
          showCloseButton={true}
        >
          <div className="bg-white dark:bg-gray-800">
            {/* Header */}
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <Book className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {t('help.gettingStarted')}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('help.gettingStartedSubtitle')}
                </p>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
              {/* Sección 1: Búsqueda */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">1</span>
                  {t('guide.searchTitle')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.searchDesc')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.searchTip1')}</li>
                  <li>{t('guide.searchTip2')}</li>
                  <li>{t('guide.searchTip3')}</li>
                </ul>
              </div>

              {/* Sección 2: Filtros */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">2</span>
                  {t('guide.filtersTitle')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.filtersDesc')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.filtersTip1')}</li>
                  <li>{t('guide.filtersTip2')}</li>
                  <li>{t('guide.filtersTip3')}</li>
                </ul>
              </div>

              {/* Sección 3: Favoritos */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">3</span>
                  {t('guide.favoritesTitle')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.favoritesDesc')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.favoritesTip1')}</li>
                  <li>{t('guide.favoritesTip2')}</li>
                  <li>{t('guide.favoritesTip3')}</li>
                </ul>
              </div>

              {/* Sección 4: Historial */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">4</span>
                  {t('guide.historyTitle')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.historyDesc')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.historyTip1')}</li>
                  <li>{t('guide.historyTip2')}</li>
                  <li>{t('guide.historyTip3')}</li>
                </ul>
              </div>

              {/* Sección 5: Preferencias */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">5</span>
                  {t('guide.settingsTitle')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.settingsDesc')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.settingsTip1')}</li>
                  <li>{t('guide.settingsTip2')}</li>
                  <li>{t('guide.settingsTip3')}</li>
                </ul>
              </div>
            </div>
          </div>
        </Modal>

        {/* Contact Modal */}
        <ContactModal
          isOpen={isContactModalOpen}
          onClose={() => setIsContactModalOpen(false)}
        />

        {/* Documentation Modal */}
        <Modal
          isOpen={isDocumentationModalOpen}
          onClose={() => setIsDocumentationModalOpen(false)}
          size="lg"
          showCloseButton={true}
        >
          <div className="bg-white dark:bg-gray-800">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {t('help.documentation')}
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {t('help.documentationSubtitle')}
                  </p>
                </div>
              </div>
              <a
                href="https://github.com/RubenGarrod/ClinicCloud#readme"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-primary-600 dark:text-primary-400 hover:underline"
              >
                <span className="text-sm font-medium">{t('help.openInGitHub')}</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* README Content */}
            <div className="w-full h-[70vh] border border-gray-200 dark:border-gray-700 rounded-lg overflow-y-auto bg-white dark:bg-gray-900 p-6">
              {readmeLoading && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">{t('help.loadingDocumentation')}</p>
                  </div>
                </div>
              )}

              {readmeError && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <p className="text-red-600 dark:text-red-400 mb-4">{t('help.documentationError')}</p>
                    <a
                      href="https://github.com/RubenGarrod/ClinicCloud#readme"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      {t('help.viewOnGitHub')}
                    </a>
                  </div>
                </div>
              )}

              {!readmeLoading && !readmeError && readmeContent && (
                <div
                  className="prose prose-sm dark:prose-invert max-w-none
                    prose-headings:text-gray-900 dark:prose-headings:text-white
                    prose-p:text-gray-700 dark:prose-p:text-gray-300
                    prose-a:text-primary-600 dark:prose-a:text-primary-400
                    prose-strong:text-gray-900 dark:prose-strong:text-white
                    prose-code:text-primary-600 dark:prose-code:text-primary-400
                    prose-pre:bg-gray-100 dark:prose-pre:bg-gray-800"
                  dangerouslySetInnerHTML={{ __html: readmeContent }}
                />
              )}
            </div>
          </div>
        </Modal>

        {/* Footer */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
            {t('help.footer')}{' '}
            <button
              onClick={() => setIsContactModalOpen(true)}
              className="text-primary-600 dark:text-primary-400 hover:underline font-medium cursor-pointer bg-transparent border-none p-0"
            >
              {t('help.contactUs')}
            </button>
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default HelpModal;
