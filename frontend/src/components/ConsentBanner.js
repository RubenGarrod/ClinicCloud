import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Cookie, X, Check, Settings as SettingsIcon } from 'lucide-react';
import Button from './ui/Button';

const ConsentBanner = () => {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);

  useEffect(() => {
    // Verificar si el usuario ya dio su consentimiento
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      // Mostrar el banner después de 1 segundo
      const timer = setTimeout(() => setIsVisible(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAcceptAll = () => {
    localStorage.setItem('cookieConsent', JSON.stringify({
      necessary: true,
      functional: true,
      analytics: false, // No usamos analytics por ahora
      timestamp: new Date().toISOString()
    }));
    setIsVisible(false);
  };

  const handleRejectOptional = () => {
    localStorage.setItem('cookieConsent', JSON.stringify({
      necessary: true,
      functional: false,
      analytics: false,
      timestamp: new Date().toISOString()
    }));
    setIsVisible(false);
  };

  const handleSavePreferences = () => {
    // Guardar solo las necesarias
    handleRejectOptional();
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] p-4 sm:p-6 pointer-events-none">
      <div className="max-w-6xl mx-auto pointer-events-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Cookie className="w-6 h-6 text-white" />
                <h3 className="text-lg font-semibold text-white">
                  {t('consent.title', 'Configuración de Privacidad')}
                </h3>
              </div>
              <button
                onClick={() => setIsVisible(false)}
                className="text-white hover:bg-white/20 rounded-lg p-1 transition-colors"
                aria-label="Cerrar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {!showPreferences ? (
              <>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  {t('consent.message', 'Utilizamos localStorage (similar a cookies) para mejorar tu experiencia. Estos datos se almacenan localmente en tu navegador y nos ayudan a recordar tus preferencias y mantener tu sesión.')}
                </p>

                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2 text-sm">
                    {t('consent.whatWeStore', '¿Qué almacenamos?')}
                  </h4>
                  <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                    <li>• <strong>{t('consent.necessary', 'Esenciales')}:</strong> {t('consent.necessaryDesc', 'Token de autenticación, datos básicos de usuario')}</li>
                    <li>• <strong>{t('consent.functional', 'Funcionales')}:</strong> {t('consent.functionalDesc', 'Preferencias de idioma, tema, configuración de interfaz')}</li>
                    <li>• <strong>{t('consent.search', 'Historial')}:</strong> {t('consent.searchDesc', 'Tus búsquedas (solo si tienes cuenta)')}</li>
                  </ul>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  {t('consent.learnMore', 'Lee nuestra')}{' '}
                  <Link to="/privacy" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
                    {t('consent.privacyPolicy', 'Política de Privacidad')}
                  </Link>
                  {' '}{t('consent.and', 'y')}{' '}
                  <Link to="/terms" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
                    {t('consent.terms', 'Términos de Uso')}
                  </Link>
                  {' '}{t('consent.forMore', 'para más información.')}.
                </p>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={handleAcceptAll}
                    variant="primary"
                    className="flex-1 sm:flex-none"
                  >
                    <Check className="w-4 h-4 mr-2" />
                    {t('consent.acceptAll', 'Aceptar todo')}
                  </Button>
                  <Button
                    onClick={handleRejectOptional}
                    variant="outline"
                    className="flex-1 sm:flex-none"
                  >
                    {t('consent.onlyNecessary', 'Solo necesarias')}
                  </Button>
                  <Button
                    onClick={() => setShowPreferences(true)}
                    variant="ghost"
                    className="flex-1 sm:flex-none"
                  >
                    <SettingsIcon className="w-4 h-4 mr-2" />
                    {t('consent.preferences', 'Preferencias')}
                  </Button>
                </div>
              </>
            ) : (
              <>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-4">
                  {t('consent.customizeSettings', 'Personalizar configuración')}
                </h4>

                <div className="space-y-4 mb-6">
                  {/* Necesarias (siempre activas) */}
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <h5 className="font-medium text-gray-900 dark:text-white">
                          {t('consent.necessaryTitle', 'Necesarias')}
                        </h5>
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded">
                          {t('consent.alwaysActive', 'Siempre activas')}
                        </span>
                      </div>
                      <div className="w-10 h-6 bg-green-500 rounded-full flex items-center justify-end px-1">
                        <div className="w-4 h-4 bg-white rounded-full"></div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {t('consent.necessaryText', 'Esenciales para que el sitio funcione. Incluyen autenticación y preferencias básicas.')}
                    </p>
                  </div>

                  {/* Funcionales */}
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-gray-900 dark:text-white">
                        {t('consent.functionalTitle', 'Funcionales')}
                      </h5>
                      <div className="w-10 h-6 bg-green-500 rounded-full flex items-center justify-end px-1">
                        <div className="w-4 h-4 bg-white rounded-full"></div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {t('consent.functionalText', 'Permiten recordar tus preferencias de idioma, tema y otras configuraciones de interfaz.')}
                    </p>
                  </div>

                  {/* Analytics (desactivado) */}
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 opacity-50">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-gray-900 dark:text-white">
                        {t('consent.analyticsTitle', 'Analíticas')}
                      </h5>
                      <div className="w-10 h-6 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center px-1">
                        <div className="w-4 h-4 bg-white rounded-full"></div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {t('consent.analyticsText', 'No utilizamos cookies de analíticas ni tracking de terceros.')}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={handleSavePreferences}
                    variant="primary"
                    className="flex-1"
                  >
                    {t('consent.savePreferences', 'Guardar preferencias')}
                  </Button>
                  <Button
                    onClick={() => setShowPreferences(false)}
                    variant="outline"
                    className="flex-1"
                  >
                    {t('consent.back', 'Volver')}
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsentBanner;
