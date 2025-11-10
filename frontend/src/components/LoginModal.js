import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import Modal from './ui/Modal';
import Button from './ui/Button';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import clsx from 'clsx';
import ForgotPasswordModal from './ForgotPasswordModal';
import ComingSoonModal from './ComingSoonModal';
import { sanitizeInput, validateEmail, validatePassword } from '../utils/sanitization';

const LoginModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showComingSoon, setShowComingSoon] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    // No sanitizar mientras escribe, solo al validar/enviar
    // Esto permite espacios, tildes y otros caracteres válidos
    let processedValue = value;
    if (name === 'email') {
      // Solo convertir a minúsculas para email
      processedValue = value.toLowerCase();
    }
    // Nombre y contraseñas no se modifican mientras se escribe

    setFormData(prev => ({
      ...prev,
      [name]: processedValue
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validar email con función de sanitización
    if (!formData.email) {
      newErrors.email = t('auth.errors.emailRequired', 'El email es requerido');
    } else {
      const emailValidation = validateEmail(formData.email);
      if (!emailValidation.valid) {
        newErrors.email = t('auth.errors.emailInvalid', emailValidation.error || 'Email inválido');
      }
    }

    // Validar contraseña
    if (!formData.password) {
      newErrors.password = t('auth.errors.passwordRequired', 'La contraseña es requerida');
    } else if (!isLogin) {
      // En registro, validar fortaleza de contraseña
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) {
        newErrors.password = passwordValidation.errors[0]; // Mostrar primer error
      }
    } else if (formData.password.length < 6) {
      // En login, solo verificar longitud mínima
      newErrors.password = t('auth.errors.passwordMinLength', 'La contraseña debe tener al menos 6 caracteres');
    }

    if (!isLogin) {
      if (!formData.name) {
        newErrors.name = t('auth.errors.nameRequired', 'El nombre es requerido');
      } else if (formData.name.length < 2) {
        newErrors.name = t('auth.errors.nameMinLength', 'El nombre debe tener al menos 2 caracteres');
      }
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = t('auth.errors.confirmPasswordRequired', 'Confirma tu contraseña');
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = t('auth.errors.passwordsNotMatch', 'Las contraseñas no coinciden');
      }
      if (!acceptedTerms) {
        newErrors.terms = t('auth.errors.termsRequired', 'Debes aceptar los términos y condiciones');
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      let response;

      // Sanitizar antes de enviar al backend
      const sanitizedData = {
        email: sanitizeInput(formData.email).toLowerCase(),
        password: formData.password, // Las contraseñas NO se sanitizan
        name: isLogin ? undefined : sanitizeInput(formData.name)
      };

      if (isLogin) {
        response = await login(sanitizedData.email, sanitizedData.password);
      } else {
        response = await register(sanitizedData.name, sanitizedData.email, sanitizedData.password);
      }
      
      // Success - close modal
      onClose();
      resetForm();
      
      // Optional: Show success message
      console.log(`${isLogin ? 'Login' : 'Registro'} exitoso:`, response.user);
      
    } catch (error) {
      console.error('Auth error:', error);
      
      // Manejar diferentes tipos de errores
      let errorMessage = t('auth.errors.generic', 'Ha ocurrido un error. Inténtalo de nuevo.');
      
      if (error.message) {
        // Mapear errores específicos del backend
        if (error.message.includes('Email o contraseña incorrectos')) {
          errorMessage = t('auth.errors.invalidCredentials', 'Email o contraseña incorrectos');
        } else if (error.message.includes('ya está registrado')) {
          errorMessage = t('auth.errors.emailExists', 'Este email ya está registrado');
        } else if (error.message.includes('Cuenta desactivada')) {
          errorMessage = t('auth.errors.accountDisabled', 'Cuenta desactivada');
        } else {
          errorMessage = error.message;
        }
      }
      
      setErrors({ submit: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    setShowComingSoon(true);
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      name: '',
      confirmPassword: ''
    });
    setErrors({});
    setAcceptedTerms(false);
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  const handleModalClose = () => {
    resetForm();
    onClose();
  };

  return (
    <>
    <Modal
      isOpen={isOpen}
      onClose={handleModalClose}
      title={isLogin ? t('auth.login', 'Iniciar Sesión') : t('auth.register', 'Registrarse')}
      size="md"
    >
      <div className="space-y-6">
        {/* Toggle between Login/Register */}
        <div className="flex bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
          <button
            onClick={() => setIsLogin(true)}
            className={clsx(
              'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors',
              isLogin
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            {t('auth.login', 'Iniciar Sesión')}
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={clsx(
              'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors',
              !isLogin
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            {t('auth.register', 'Registrarse')}
          </button>
        </div>

        {/* Social Login Buttons */}
        <div className="space-y-3">
          <Button
            variant="outline"
            onClick={() => handleSocialLogin('google')}
            className="w-full"
            disabled={isLoading}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            {isLogin ? t('auth.loginWithGoogle', 'Continuar con Google') : t('auth.registerWithGoogle', 'Registrarse con Google')}
          </Button>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200 dark:border-gray-600" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                {t('auth.or', 'o')}
              </span>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name field (only for register) */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('auth.name', 'Nombre completo')}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={clsx(
                    'w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  )}
                  placeholder={t('auth.namePlaceholder', 'Tu nombre completo')}
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
              )}
            </div>
          )}

          {/* Email field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('auth.email', 'Email')}
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={clsx(
                  'w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                  errors.email ? 'border-red-500' : 'border-gray-300'
                )}
                placeholder={t('auth.emailPlaceholder', 'tu@email.com')}
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email}</p>
            )}
          </div>

          {/* Password field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('auth.password', 'Contraseña')}
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={clsx(
                  'w-full pl-10 pr-10 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                  errors.password ? 'border-red-500' : 'border-gray-300'
                )}
                placeholder={t('auth.passwordPlaceholder', 'Tu contraseña')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.password}</p>
            )}
            {/* Forgot password link - solo en modo login */}
            {isLogin && (
              <div className="flex justify-end mt-1">
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(true);
                    onClose();
                  }}
                  className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
                >
                  {t('auth.forgotPassword', '¿Olvidaste tu contraseña?')}
                </button>
              </div>
            )}
          </div>

          {/* Confirm Password field (only for register) */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('auth.confirmPassword', 'Confirmar contraseña')}
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className={clsx(
                    'w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                    errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                  )}
                  placeholder={t('auth.confirmPasswordPlaceholder', 'Confirma tu contraseña')}
                />
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.confirmPassword}</p>
              )}
            </div>
          )}

          {/* Terms and Conditions Checkbox */}
          {!isLogin && (
            <div>
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(e) => {
                    setAcceptedTerms(e.target.checked);
                    if (errors.terms) {
                      setErrors(prev => ({ ...prev, terms: '' }));
                    }
                  }}
                  className={clsx(
                    "mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer",
                    errors.terms && "border-red-500"
                  )}
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {t('auth.acceptTerms', 'Acepto los')}{' '}
                  <Link
                    to="/terms"
                    onClick={(e) => {
                      e.preventDefault();
                      window.open('/terms', '_blank');
                    }}
                    className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                  >
                    {t('auth.termsLink', 'Términos y Condiciones')}
                  </Link>
                  {' '}{t('auth.and', 'y la')}{' '}
                  <Link
                    to="/privacy"
                    onClick={(e) => {
                      e.preventDefault();
                      window.open('/privacy', '_blank');
                    }}
                    className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                  >
                    {t('auth.privacyLink', 'Política de Privacidad')}
                  </Link>
                </span>
              </label>
              {errors.terms && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.terms}</p>
              )}
            </div>
          )}

          {/* Submit Error */}
          {errors.submit && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{errors.submit}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            className="w-full"
            loading={isLoading}
            disabled={isLoading}
          >
            {isLogin ? t('auth.login', 'Iniciar Sesión') : t('auth.register', 'Registrarse')}
          </Button>
        </form>

      </div>
    </Modal>

    {/* Forgot Password Modal */}
    <ForgotPasswordModal
      isOpen={showForgotPassword}
      onClose={() => setShowForgotPassword(false)}
      onBack={() => {
        setShowForgotPassword(false);
        // Re-abrir el modal de login
        setTimeout(() => onClose(), 100);
      }}
    />

    {/* Coming Soon Modal */}
    <ComingSoonModal
      isOpen={showComingSoon}
      onClose={() => setShowComingSoon(false)}
      feature={t('auth.googleLogin', 'inicio de sesión con Google')}
    />
  </>
  );
};

export default LoginModal;