import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Mail, ArrowLeft } from 'lucide-react';
import Modal from './ui/Modal';
import Button from './ui/Button';

const ForgotPasswordModal = ({ isOpen, onClose, onBack }) => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Reset del formulario al cerrar o abrir
  React.useEffect(() => {
    if (isOpen) {
      setEmail('');
      setError('');
      setSuccess(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validación básica
    if (!email || !email.includes('@')) {
      setError(t('auth.errors.emailInvalid', 'Email inválido'));
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
          onClose();
        }, 5000);
      } else {
        setError(data.detail || t('forgotPassword.error', 'Error al enviar email'));
      }
    } catch (error) {
      console.error('Error sending reset email:', error);
      setError(t('forgotPassword.errorNetwork', 'Error de conexión. Inténtalo de nuevo.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="sm"
      showCloseButton={true}
    >
      <div className="p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('forgotPassword.title', '¿Olvidaste tu contraseña?')}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {t('forgotPassword.subtitle', 'Ingresa tu email y te enviaremos un link para recuperarla')}
          </p>
        </div>

        {/* Formulario o mensaje de éxito */}
        {success ? (
          <div className="text-center py-4">
            <div className="mb-4">
              <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {t('forgotPassword.checkEmail', '¡Revisa tu email!')}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {t('forgotPassword.emailSent', 'Si el email existe, recibirás un link de recuperación en breve.')}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              {t('forgotPassword.autoClose', 'Esta ventana se cerrará automáticamente...')}
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {/* Campo de email */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('auth.email', 'Email')}
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('auth.emailPlaceholder', 'tu@email.com')}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                disabled={isLoading}
                autoFocus
              />
            </div>

            {/* Mensajes de error */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* Botones */}
            <div className="flex flex-col gap-3">
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                disabled={isLoading}
                loading={isLoading}
              >
                {t('forgotPassword.sendEmail', 'Enviar link de recuperación')}
              </Button>

              <Button
                type="button"
                variant="ghost"
                className="w-full flex items-center justify-center gap-2"
                onClick={onBack}
                disabled={isLoading}
              >
                <ArrowLeft className="w-4 h-4" />
                {t('forgotPassword.backToLogin', 'Volver al inicio de sesión')}
              </Button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
};

export default ForgotPasswordModal;
