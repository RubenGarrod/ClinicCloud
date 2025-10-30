import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';
import Button from './ui/Button';

const ResetPasswordPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Verificar token al cargar
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenValid(false);
        setIsVerifying(false);
        setError(t('resetPassword.noToken', 'Link inválido. No se encontró el token.'));
        return;
      }

      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/verify-reset-token`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
          }
        );

        if (response.ok) {
          setTokenValid(true);
        } else {
          setTokenValid(false);
          const data = await response.json();
          setError(data.detail || t('resetPassword.tokenExpired', 'El link ha expirado o es inválido'));
        }
      } catch (error) {
        console.error('Error verifying token:', error);
        setTokenValid(false);
        setError(t('resetPassword.errorNetwork', 'Error de conexión. Inténtalo de nuevo.'));
      } finally {
        setIsVerifying(false);
      }
    };

    verifyToken();
  }, [token, t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validaciones
    if (!newPassword || newPassword.length < 6) {
      setError(t('auth.errors.passwordMinLength', 'La contraseña debe tener al menos 6 caracteres'));
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(t('auth.errors.passwordsNotMatch', 'Las contraseñas no coinciden'));
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/reset-password`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token,
            new_password: newPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Redirigir al login después de 3 segundos
        setTimeout(() => {
          navigate('/');
        }, 3000);
      } else {
        setError(data.detail || t('resetPassword.error', 'Error al restablecer contraseña'));
      }
    } catch (error) {
      console.error('Error resetting password:', error);
      setError(t('resetPassword.errorNetwork', 'Error de conexión. Inténtalo de nuevo.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {/* Loading state */}
          {isVerifying && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">
                {t('resetPassword.verifying', 'Verificando link...')}
              </p>
            </div>
          )}

          {/* Token inválido */}
          {!isVerifying && !tokenValid && (
            <div className="text-center py-4">
              <div className="mx-auto w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mb-4">
                <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {t('resetPassword.invalidTitle', 'Link inválido')}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                {error}
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/')}
                className="w-full"
              >
                {t('resetPassword.goToLogin', 'Ir al inicio de sesión')}
              </Button>
            </div>
          )}

          {/* Formulario de nueva contraseña */}
          {!isVerifying && tokenValid && !success && (
            <>
              {/* Header */}
              <div className="text-center mb-6">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mb-4">
                  <Lock className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {t('resetPassword.title', 'Nueva contraseña')}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('resetPassword.subtitle', 'Ingresa tu nueva contraseña a continuación')}
                </p>
              </div>

              <form onSubmit={handleSubmit}>
                {/* Nueva contraseña */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('resetPassword.newPassword', 'Nueva contraseña')}
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder={t('resetPassword.newPasswordPlaceholder', 'Mínimo 6 caracteres')}
                      className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                      disabled={isLoading}
                      autoFocus
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      tabIndex={-1}
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Confirmar contraseña */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('resetPassword.confirmPassword', 'Confirmar contraseña')}
                  </label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder={t('resetPassword.confirmPasswordPlaceholder', 'Repite tu contraseña')}
                      className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      tabIndex={-1}
                    >
                      {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Mensajes de error */}
                {error && (
                  <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                    {error}
                  </div>
                )}

                {/* Botón */}
                <Button
                  type="submit"
                  variant="primary"
                  className="w-full"
                  disabled={isLoading}
                  loading={isLoading}
                >
                  {t('resetPassword.submit', 'Restablecer contraseña')}
                </Button>
              </form>
            </>
          )}

          {/* Success */}
          {success && (
            <div className="text-center py-4">
              <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {t('resetPassword.successTitle', '¡Contraseña actualizada!')}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {t('resetPassword.successMessage', 'Tu contraseña ha sido actualizada correctamente.')}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                {t('resetPassword.redirecting', 'Redirigiendo al inicio de sesión...')}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            © 2025 ClinicCloud. {t('common.allRightsReserved', 'Todos los derechos reservados')}.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
