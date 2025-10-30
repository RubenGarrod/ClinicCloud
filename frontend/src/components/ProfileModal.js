import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { User, Building, Stethoscope, Save, Camera, Lock, Calendar, GraduationCap, Globe, MapPin } from 'lucide-react';
import { CountryDropdown, RegionDropdown } from 'react-country-region-selector';
import Button from './ui/Button';
import Modal from './ui/Modal';
import AvatarSelector from './AvatarSelector';
import { getAvatarIcon, getAvatarColorClass, getDefaultAvatar } from '../utils/avatarUtils';
import authService from '../services/authService';

const ProfileModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const { user, updateProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('personal'); // 'personal' o 'security'
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isAvatarSelectorOpen, setIsAvatarSelectorOpen] = useState(false);

  const [formData, setFormData] = useState({
    name: user?.name || '',
    title: user?.title || '',
    country: user?.country || '',
    region: user?.region || '',
    institution: user?.institution || '',
    specialty: user?.specialty || ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [fieldErrors, setFieldErrors] = useState({
    currentPassword: false,
    newPassword: false,
    confirmPassword: false
  });

  // Pre-fill form when user data changes
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        title: user.title || '',
        country: user.country || '',
        region: user.region || '',
        institution: user.institution || '',
        specialty: user.specialty || ''
      });
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCountryChange = (val) => {
    setFormData(prev => ({
      ...prev,
      country: val,
      region: '' // Clear region when country changes
    }));
  };

  const handleRegionChange = (val) => {
    setFormData(prev => ({
      ...prev,
      region: val
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = authService.getToken();
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/profile`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          title: formData.title,
          country: formData.country,
          region: formData.region,
          institution: formData.institution,
          specialty: formData.specialty
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al actualizar perfil');
      }

      const updatedUser = await response.json();
      updateProfile(updatedUser);
      setSuccess(t('profile.updateSuccess', 'Perfil actualizado correctamente'));
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError(error.message || t('profile.updateError', 'Error al actualizar el perfil'));
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Resetear errores de campos
    const errors = {
      currentPassword: false,
      newPassword: false,
      confirmPassword: false
    };

    // Validaciones con feedback visual
    if (!passwordData.currentPassword) {
      errors.currentPassword = true;
      setError(t('profile.passwordRequired', 'Por favor, rellena la contraseña actual'));
      setFieldErrors(errors);
      setLoading(false);
      return;
    }

    if (!passwordData.newPassword) {
      errors.newPassword = true;
      setError(t('profile.passwordRequired', 'Por favor, rellena la nueva contraseña'));
      setFieldErrors(errors);
      setLoading(false);
      return;
    }

    if (!passwordData.confirmPassword) {
      errors.confirmPassword = true;
      setError(t('profile.passwordRequired', 'Por favor, confirma la nueva contraseña'));
      setFieldErrors(errors);
      setLoading(false);
      return;
    }

    if (passwordData.newPassword.length < 6) {
      errors.newPassword = true;
      setError(t('profile.passwordTooShort', 'La contraseña debe tener al menos 6 caracteres'));
      setFieldErrors(errors);
      setLoading(false);
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      errors.newPassword = true;
      errors.confirmPassword = true;
      setError(t('profile.passwordMismatch', 'Las contraseñas no coinciden'));
      setFieldErrors(errors);
      setLoading(false);
      return;
    }

    // Resetear errores si todo está bien
    setFieldErrors(errors);

    try {
      const token = authService.getToken();
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al cambiar contraseña');
      }

      setSuccess(t('profile.passwordChanged', 'Contraseña cambiada correctamente'));
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      console.error('Error changing password:', error);

      // Check if it's a wrong password error
      if (error.message && (error.message.includes('incorrecta') || error.message.includes('incorrect'))) {
        setFieldErrors({ ...fieldErrors, currentPassword: true });
        setError(t('profile.wrongPassword', 'La contraseña actual es incorrecta'));
      } else {
        setError(error.message || t('profile.passwordChangeFailed', 'Error al cambiar la contraseña'));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      title: user?.title || '',
      country: user?.country || '',
      region: user?.region || '',
      institution: user?.institution || '',
      specialty: user?.specialty || ''
    });
    setError('');
    setSuccess('');
    setIsEditing(false);
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  const handleClose = () => {
    if (isEditing) {
      handleCancel();
    }
    // Limpiar campos de contraseña
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setFieldErrors({
      currentPassword: false,
      newPassword: false,
      confirmPassword: false
    });
    setActiveTab('personal');
    setError('');
    setSuccess('');
    onClose();
  };

  // Limpiar campos de contraseña cuando se cambia de pestaña
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    // Limpiar campos y errores de contraseña al salir de la pestaña de seguridad
    if (tab !== 'security') {
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setFieldErrors({
        currentPassword: false,
        newPassword: false,
        confirmPassword: false
      });
      setError('');
      setSuccess('');
    }
  };

  const handleAvatarSelect = async (avatar) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = authService.getToken();
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/profile`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          avatar_icon: avatar.icon,
          avatar_color: avatar.color
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al actualizar avatar');
      }

      const updatedUser = await response.json();
      updateProfile(updatedUser);
      setSuccess(t('profile.avatarUpdated', 'Avatar actualizado correctamente'));
    } catch (error) {
      console.error('Error updating avatar:', error);
      setError(error.message || t('profile.avatarUpdateError', 'Error al actualizar avatar'));
    } finally {
      setLoading(false);
    }
  };

  const currentAvatar = user?.avatar || getDefaultAvatar();

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        size="lg"
        showCloseButton={true}
      >
        <div className="bg-white dark:bg-gray-800">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center p-3 ${getAvatarColorClass(currentAvatar.color)}`}>
                  <img
                    src={getAvatarIcon(currentAvatar.icon)}
                    alt={user?.name}
                    className="w-full h-full object-contain"
                  />
                </div>
                <button
                  onClick={() => setIsAvatarSelectorOpen(true)}
                  className="absolute -bottom-1 -right-1 w-7 h-7 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center border-2 border-white dark:border-gray-800 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <Camera className="w-3.5 h-3.5 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {user?.name || t('profile.noName', 'Sin nombre')}
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {user?.email}
                </p>
                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <Calendar className="w-3.5 h-3.5 mr-1" />
                  {t('profile.memberSince', 'Miembro desde')} {user?.created_at ? new Date(user.created_at).getFullYear() : new Date().getFullYear()}
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex px-6" aria-label="Tabs">
              <button
                onClick={() => handleTabChange('personal')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'personal'
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                } mr-8`}
              >
                <User className="w-4 h-4 inline mr-2" />
                {t('profile.personalInfo', 'Información Personal')}
              </button>
              <button
                onClick={() => handleTabChange('security')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'security'
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Lock className="w-4 h-4 inline mr-2" />
                {t('profile.security', 'Seguridad')}
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[60vh] overflow-y-auto">
            {/* Mensajes de error/éxito */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 text-sm">
                {success}
              </div>
            )}

            {/* Personal Tab */}
            {activeTab === 'personal' && (
              <div className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <User className="w-4 h-4 inline mr-1" />
                      {t('profile.name', 'Nombre completo')}
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                      placeholder={t('profile.namePlaceholder', 'Ingresa tu nombre completo')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <GraduationCap className="w-4 h-4 inline mr-1" />
                      {t('profile.title', 'Título profesional')}
                    </label>
                    <select
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                    >
                      <option value="">{t('profile.titlePlaceholder', 'Selecciona un título')}</option>
                      <option value="dr">Dr.</option>
                      <option value="dra">Dra.</option>
                      <option value="lic">Lic.</option>
                      <option value="enf">Enf.</option>
                      <option value="estudiante">{t('profile.titleStudent', 'Estudiante')}</option>
                      <option value="otro">{t('profile.titleOther', 'Otro')}</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Globe className="w-4 h-4 inline mr-1" />
                        {t('profile.country', 'País')}
                      </label>
                      <CountryDropdown
                        value={formData.country}
                        onChange={handleCountryChange}
                        disabled={!isEditing}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                        defaultOptionLabel={t('profile.countryPlaceholder', 'Selecciona un país')}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <MapPin className="w-4 h-4 inline mr-1" />
                        {t('profile.region', 'Región/Estado')}
                      </label>
                      <RegionDropdown
                        country={formData.country}
                        value={formData.region}
                        onChange={handleRegionChange}
                        disabled={!isEditing}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                        defaultOptionLabel={t('profile.regionPlaceholder', 'Selecciona una región')}
                        blankOptionLabel={t('profile.regionPlaceholder', 'Selecciona una región')}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Building className="w-4 h-4 inline mr-1" />
                      {t('profile.institution', 'Institución')}
                    </label>
                    <input
                      type="text"
                      name="institution"
                      value={formData.institution}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                      placeholder={t('profile.institutionPlaceholder', 'Hospital, universidad, clínica...')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Stethoscope className="w-4 h-4 inline mr-1" />
                      {t('profile.specialty', 'Especialidad')}
                    </label>
                    <input
                      type="text"
                      name="specialty"
                      value={formData.specialty}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400"
                      placeholder={t('profile.specialtyPlaceholder', 'Cardiología, Neurología...')}
                    />
                  </div>
                </div>

                {/* Botones de acción dentro del contenido */}
                <div className="flex justify-end space-x-3 pt-4">
                  {isEditing ? (
                    <>
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={handleCancel}
                        disabled={loading}
                      >
                        {t('profile.cancel', 'Cancelar')}
                      </Button>
                      <Button
                        type="button"
                        variant="primary"
                        onClick={handleSave}
                        disabled={loading}
                      >
                        <Save className="w-4 h-4 mr-2" />
                        {loading ? t('profile.saving', 'Guardando...') : t('profile.save', 'Guardar cambios')}
                      </Button>
                    </>
                  ) : (
                    <Button
                      type="button"
                      variant="primary"
                      onClick={() => setIsEditing(true)}
                    >
                      {t('profile.edit', 'Editar perfil')}
                    </Button>
                  )}
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('profile.currentPassword', 'Contraseña actual')}
                  </label>
                  <input
                    type="password"
                    name="currentPassword"
                    value={passwordData.currentPassword}
                    onChange={handlePasswordChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      fieldErrors.currentPassword
                        ? 'border-red-500 dark:border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder={t('profile.currentPasswordPlaceholder', 'Tu contraseña actual')}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('profile.newPassword', 'Nueva contraseña')}
                  </label>
                  <input
                    type="password"
                    name="newPassword"
                    value={passwordData.newPassword}
                    onChange={handlePasswordChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      fieldErrors.newPassword
                        ? 'border-red-500 dark:border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder={t('profile.newPasswordPlaceholder', 'Tu nueva contraseña')}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('profile.confirmNewPassword', 'Confirmar nueva contraseña')}
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={passwordData.confirmPassword}
                    onChange={handlePasswordChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      fieldErrors.confirmPassword
                        ? 'border-red-500 dark:border-red-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder={t('profile.confirmNewPasswordPlaceholder', 'Confirma tu nueva contraseña')}
                  />
                </div>

                <div className="flex justify-end pt-4">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loading}
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    {loading ? t('profile.saving', 'Guardando...') : t('profile.changePassword', 'Cambiar contraseña')}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      </Modal>

      {/* Avatar Selector Modal */}
      <AvatarSelector
        isOpen={isAvatarSelectorOpen}
        onClose={() => setIsAvatarSelectorOpen(false)}
        currentAvatar={currentAvatar}
        onSelect={handleAvatarSelect}
      />
    </>
  );
};

export default ProfileModal;
