import React from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Database, Lock, Eye, UserX, Download, AlertCircle, User, Share2, ShieldCheck, Clock, Cookie, Globe, Baby, FileEdit, Landmark, Mail } from 'lucide-react';

const PrivacyPage = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="w-8 h-8 text-primary-600 dark:text-primary-400" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('privacy.title', 'Política de Privacidad')}
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          {t('privacy.lastUpdated', 'Última actualización')}: {new Date().toLocaleDateString()}
        </p>
        <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-blue-900 dark:text-blue-200 text-sm">
            <strong>GDPR Compliant:</strong> {t('privacy.gdprNote', 'Esta política cumple con el Reglamento General de Protección de Datos (RGPD/GDPR) de la Unión Europea.')}
          </p>
        </div>
      </div>

      <div className="prose prose-slate dark:prose-invert max-w-none">
        {/* 1. Responsable del Tratamiento */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <User className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.controller.title', '1. Responsable del Tratamiento de Datos')}
          </h2>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              <strong>{t('privacy.controller.name', 'Proyecto')}:</strong> ClinicCloud
            </p>
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              <strong>{t('privacy.controller.contact', 'Contacto')}:</strong> cliniccloud.contact@gmail.com
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <strong>{t('privacy.controller.location', 'Ubicación')}:</strong> España (Unión Europea)
            </p>
          </div>
        </section>

        {/* 2. Datos que Recopilamos */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Database className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.data.title', '2. Datos que Recopilamos')}
          </h2>

          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('privacy.data.account', '2.1. Datos de cuenta')}
          </h3>
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            {t('privacy.data.accountText', 'Cuando creas una cuenta, recopilamos:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>{t('privacy.data.email', 'Email')}:</strong> {t('privacy.data.emailPurpose', 'Para autenticación y comunicaciones')}</li>
            <li><strong>{t('privacy.data.name', 'Nombre')}:</strong> {t('privacy.data.namePurpose', 'Para personalizar tu experiencia')}</li>
            <li><strong>{t('privacy.data.password', 'Contraseña')}:</strong> {t('privacy.data.passwordPurpose', 'Hasheada con bcrypt (nunca almacenamos contraseñas en texto plano)')}</li>
            <li><strong>{t('privacy.data.profile', 'Datos de perfil opcionales')}:</strong> {t('privacy.data.profilePurpose', 'Institución, especialidad, país, región')}</li>
          </ul>

          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('privacy.data.usage', '2.2. Datos de uso')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>{t('privacy.data.searches', 'Historial de búsquedas')}:</strong> {t('privacy.data.searchesPurpose', 'Queries, fechas, número de resultados')}</li>
            <li><strong>{t('privacy.data.favorites', 'Documentos favoritos')}:</strong> {t('privacy.data.favoritesPurpose', 'Artículos guardados y notas personales')}</li>
            <li><strong>{t('privacy.data.preferences', 'Preferencias')}:</strong> {t('privacy.data.preferencesPurpose', 'Idioma, tema, configuración de avatar')}</li>
            <li><strong>{t('privacy.data.timestamps', 'Marcas temporales')}:</strong> {t('privacy.data.timestampsPurpose', 'Fecha de registro, último login')}</li>
          </ul>

          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('privacy.data.technical', '2.3. Datos técnicos')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>{t('privacy.data.ip', 'Dirección IP')}:</strong> {t('privacy.data.ipPurpose', 'Para seguridad y prevención de fraude (tokens de reset)')}</li>
            <li><strong>{t('privacy.data.userAgent', 'User Agent')}:</strong> {t('privacy.data.userAgentPurpose', 'Para detectar múltiples dispositivos')}</li>
            <li><strong>LocalStorage:</strong> {t('privacy.data.localStoragePurpose', 'auth_token, user_data, preferencias de idioma (almacenados localmente en tu navegador)')}</li>
          </ul>

          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
            <p className="text-amber-900 dark:text-amber-200 text-sm flex items-start">
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
              <span>
                <strong>{t('privacy.data.aiNote', 'Procesamiento con IA')}:</strong> {t('privacy.data.aiNoteText', 'Tus búsquedas son procesadas por modelos de IA (embeddings) para mejorar los resultados. No compartimos estos datos con terceros.')}
              </span>
            </p>
          </div>
        </section>

        {/* 3. Base Legal y Finalidad */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Lock className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.legal.title', '3. Base Legal y Finalidad del Tratamiento')}
          </h2>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    {t('privacy.legal.dataType', 'Tipo de Dato')}
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    {t('privacy.legal.purpose', 'Finalidad')}
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    {t('privacy.legal.basis', 'Base Legal (GDPR)')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                <tr>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.accountData', 'Datos de cuenta')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.accountPurpose', 'Gestión del servicio')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.accountBasis', 'Ejecución del contrato (Art. 6.1.b)')}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.searchHistory', 'Historial de búsquedas')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.searchPurpose', 'Mejorar experiencia del usuario')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.searchBasis', 'Consentimiento (Art. 6.1.a)')}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.ipData', 'IP / User Agent')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.ipPurpose', 'Seguridad y prevención de fraude')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {t('privacy.legal.ipBasis', 'Interés legítimo (Art. 6.1.f)')}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* 4. Cómo Usamos tus Datos */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Eye className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.usage.title', '4. Cómo Usamos tus Datos')}
          </h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('privacy.usage.item1', 'Proporcionar y mantener el servicio de búsqueda')}</li>
            <li>{t('privacy.usage.item2', 'Personalizar tu experiencia (historial, favoritos, preferencias)')}</li>
            <li>{t('privacy.usage.item3', 'Procesar búsquedas con modelos de IA para mejorar relevancia')}</li>
            <li>{t('privacy.usage.item4', 'Enviar emails relacionados con el servicio (recuperación de contraseña, notificaciones importantes)')}</li>
            <li>{t('privacy.usage.item5', 'Analizar patrones de uso para mejorar la plataforma')}</li>
            <li>{t('privacy.usage.item6', 'Garantizar la seguridad y prevenir abuso del servicio')}</li>
          </ul>
          <p className="text-gray-700 dark:text-gray-300 mt-4">
            <strong>{t('privacy.usage.noSelling', 'NO vendemos ni compartimos tus datos personales con terceros para marketing.')}</strong>
          </p>
        </section>

        {/* 5. Compartir Datos con Terceros */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Share2 className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.sharing.title', '5. Compartir Datos con Terceros')}
          </h2>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('privacy.sharing.services', '5.1. Servicios que utilizamos')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>MyMemory API:</strong> {t('privacy.sharing.mymemory', 'Para traducción automática de contenido (solo texto de documentos públicos)')}</li>
            <li><strong>Servidor de email (SMTP):</strong> {t('privacy.sharing.smtp', 'Para enviar emails de recuperación de contraseña')}</li>
            <li><strong>Hosting/Base de datos:</strong> {t('privacy.sharing.hosting', 'Datos almacenados en servidores seguros (PostgreSQL)')}</li>
          </ul>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('privacy.sharing.noThirdParty', '5.2. No compartimos con')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('privacy.sharing.noItem1', 'Empresas de publicidad o marketing')}</li>
            <li>{t('privacy.sharing.noItem2', 'Redes sociales para tracking')}</li>
            <li>{t('privacy.sharing.noItem3', 'Brokers de datos')}</li>
            <li>{t('privacy.sharing.noItem4', 'Cualquier entidad con fines comerciales')}</li>
          </ul>
        </section>

        {/* 6. Tus Derechos (GDPR) */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <UserX className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.rights.title', '6. Tus Derechos (GDPR)')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            {t('privacy.rights.intro', 'Bajo el GDPR, tienes los siguientes derechos sobre tus datos personales:')}
          </p>

          <div className="space-y-4">
            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.access', '📋 Derecho de Acceso')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.accessText', 'Puedes solicitar una copia de todos tus datos personales.')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.rectification', '✏️ Derecho de Rectificación')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.rectificationText', 'Puedes corregir datos inexactos o incompletos desde tu perfil.')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.erasure', '🗑️ Derecho al Olvido (Supresión)')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.erasureText', 'Puedes eliminar tu cuenta y todos tus datos desde Configuración > Eliminar Cuenta.')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.portability', '📤 Derecho a la Portabilidad')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.portabilityText', 'Puedes exportar tus datos en formato estructurado (JSON).')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.restriction', '⏸️ Derecho a la Limitación del Tratamiento')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.restrictionText', 'Puedes solicitar que limitemos el procesamiento de tus datos.')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.objection', '🚫 Derecho de Oposición')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.objectionText', 'Puedes oponerte al procesamiento basado en interés legítimo.')}
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {t('privacy.rights.withdraw', '⏹️ Retirar Consentimiento')}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                {t('privacy.rights.withdrawText', 'Puedes retirar tu consentimiento en cualquier momento sin afectar la legalidad del tratamiento previo.')}
              </p>
            </div>
          </div>

          <div className="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <p className="text-green-900 dark:text-green-200 text-sm">
              <strong>{t('privacy.rights.exercise', 'Para ejercer tus derechos')}:</strong> {t('privacy.rights.exerciseText', 'Contacta con nosotros en cliniccloud.contact@gmail.com. Responderemos en un plazo máximo de 30 días.')}
            </p>
          </div>
        </section>

        {/* 7. Seguridad */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <ShieldCheck className="w-6 h-6 mr-2 text-green-600 dark:text-green-400" />
            {t('privacy.security.title', '7. Seguridad de los Datos')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('privacy.security.intro', 'Implementamos medidas técnicas y organizativas para proteger tus datos:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('privacy.security.item1', 'Contraseñas hasheadas con bcrypt (no almacenamos contraseñas en texto plano)')}</li>
            <li>{t('privacy.security.item2', 'Autenticación mediante tokens JWT con expiración')}</li>
            <li>{t('privacy.security.item3', 'Conexiones HTTPS cifradas')}</li>
            <li>{t('privacy.security.item4', 'Tokens de reset de contraseña de un solo uso con expiración de 1 hora')}</li>
            <li>{t('privacy.security.item5', 'Base de datos con acceso restringido')}</li>
            <li>{t('privacy.security.item6', 'Registro de accesos para prevención de fraude')}</li>
          </ul>
        </section>

        {/* 8. Retención de Datos */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Clock className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.retention.title', '8. Retención de Datos')}
          </h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('privacy.retention.item1', 'Datos de cuenta: Mientras tu cuenta esté activa')}</li>
            <li>{t('privacy.retention.item2', 'Historial de búsquedas: Hasta que los elimines manualmente o cierres tu cuenta')}</li>
            <li>{t('privacy.retention.item3', 'Tokens de reset: 1 hora después de su creación (eliminación automática)')}</li>
            <li>{t('privacy.retention.item4', 'Datos de backup: Hasta 30 días después de la eliminación de cuenta')}</li>
          </ul>
        </section>

        {/* 9. Cookies y LocalStorage */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Cookie className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.cookies.title', '9. Cookies y LocalStorage')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('privacy.cookies.intro', 'ClinicCloud NO utiliza cookies tradicionales. En su lugar, usamos LocalStorage del navegador para:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>auth_token:</strong> {t('privacy.cookies.authToken', 'Token de autenticación (esencial)')}</li>
            <li><strong>user_data:</strong> {t('privacy.cookies.userData', 'Información básica del perfil (esencial)')}</li>
            <li><strong>i18nextLng:</strong> {t('privacy.cookies.language', 'Preferencia de idioma (funcional)')}</li>
          </ul>
          <p className="text-gray-700 dark:text-gray-300">
            {t('privacy.cookies.control', 'Puedes eliminar estos datos desde las herramientas de desarrollo de tu navegador (Application > Local Storage). Al cerrar sesión, auth_token y user_data se eliminan automáticamente.')}
          </p>
        </section>

        {/* 10. Transferencias Internacionales */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Globe className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.transfers.title', '10. Transferencias Internacionales')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('privacy.transfers.text', 'Tus datos se almacenan en servidores ubicados en la Unión Europea. Si en el futuro utilizamos proveedores fuera de la UE, implementaremos las salvaguardias adecuadas (Cláusulas Contractuales Tipo de la UE) según lo requiere el GDPR.')}
          </p>
        </section>

        {/* 11. Menores de Edad */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Baby className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.minors.title', '11. Menores de Edad')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('privacy.minors.text', 'ClinicCloud está destinado a profesionales de la salud y estudiantes mayores de 16 años. No recopilamos intencionalmente datos de menores de 16 años. Si eres padre/tutor y crees que tu hijo ha proporcionado datos, contáctanos para eliminarlos.')}
          </p>
        </section>

        {/* 12. Cambios en la Política */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <FileEdit className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.changes.title', '12. Cambios en esta Política')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('privacy.changes.text', 'Podemos actualizar esta política ocasionalmente. Te notificaremos de cambios significativos mediante un aviso en la plataforma o por email. La fecha de última actualización siempre aparece al inicio de este documento.')}
          </p>
        </section>

        {/* 13. Autoridad de Control */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Landmark className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.authority.title', '13. Autoridad de Control')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('privacy.authority.text', 'Si consideras que no hemos tratado tus datos correctamente, tienes derecho a presentar una reclamación ante la autoridad de control competente:')}
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              <strong>{t('privacy.authority.spain', 'España')}:</strong> Agencia Española de Protección de Datos (AEPD)
            </p>
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              {t('privacy.authority.website', 'Web')}: <a href="https://www.aepd.es" target="_blank" rel="noopener noreferrer" className="text-primary-600 dark:text-primary-400 hover:underline">www.aepd.es</a>
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              {t('privacy.authority.phone', 'Teléfono')}: 901 100 099 / 912 663 517
            </p>
          </div>
        </section>

        {/* 14. Contacto */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Mail className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('privacy.contact.title', '14. Contacto y Solicitudes')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('privacy.contact.text', 'Para cualquier consulta sobre esta política o para ejercer tus derechos GDPR:')}
          </p>
          <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4">
            <p className="text-primary-900 dark:text-primary-200">
              <strong>Email:</strong> cliniccloud.contact@gmail.com
            </p>
            <p className="text-primary-900 dark:text-primary-200 text-sm mt-2">
              {t('privacy.contact.response', 'Responderemos a tu solicitud en un plazo máximo de 30 días.')}
            </p>
          </div>
        </section>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-6 mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            {t('privacy.footer', 'Esta política de privacidad cumple con el Reglamento (UE) 2016/679 (GDPR) y la Ley Orgánica 3/2018 de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;
