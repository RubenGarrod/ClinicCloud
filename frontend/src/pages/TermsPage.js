import React from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Shield, AlertTriangle, Cpu, Database, Search, Copyright, Edit, XCircle, Scale, Mail } from 'lucide-react';

const TermsPage = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <FileText className="w-8 h-8 text-primary-600 dark:text-primary-400" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('terms.title', 'Términos y Condiciones de Uso')}
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          {t('terms.lastUpdated', 'Última actualización')}: {new Date().toLocaleDateString()}
        </p>
      </div>

      <div className="prose prose-slate dark:prose-invert max-w-none">
        {/* 1. Aceptación */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Shield className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.acceptance.title', '1. Aceptación de los Términos')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('terms.acceptance.text1', 'Al acceder y utilizar ClinicCloud, aceptas estar vinculado por estos Términos y Condiciones. Si no estás de acuerdo con alguna parte de estos términos, no debes utilizar nuestro servicio.')}
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.acceptance.text2', 'Este servicio está destinado únicamente a profesionales de la salud, investigadores y estudiantes con fines educativos e informativos.')}
          </p>
        </section>

        {/* 2. Descripción del Servicio */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Search className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.service.title', '2. Descripción del Servicio')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('terms.service.description', 'ClinicCloud es una plataforma de búsqueda inteligente de documentación médica y científica que utiliza:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('terms.service.item1', 'Búsqueda semántica mediante embeddings y modelos de inteligencia artificial')}</li>
            <li>{t('terms.service.item2', 'Indexación de literatura científica de fuentes públicas (PubMed, journals médicos)')}</li>
            <li>{t('terms.service.item3', 'Recomendaciones automatizadas basadas en similitud semántica')}</li>
            <li>{t('terms.service.item4', 'Historial de búsquedas y gestión de favoritos')}</li>
          </ul>
        </section>

        {/* 3. Uso de Inteligencia Artificial */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Cpu className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.ai.title', '3. Uso de Inteligencia Artificial')}
          </h2>
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-4">
            <p className="text-amber-900 dark:text-amber-200 text-sm">
              <strong>{t('terms.ai.important', 'IMPORTANTE')}:</strong> {t('terms.ai.warning', 'Este servicio utiliza modelos de inteligencia artificial para procesar y analizar contenido médico.')}
            </p>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.ai.models', '3.1. Modelos utilizados')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li><strong>S-PubMedBert-MS-MARCO</strong>: {t('terms.ai.model1', 'Para búsqueda semántica y generación de embeddings')}</li>
            <li><strong>PostgreSQL pgvector</strong>: {t('terms.ai.model2', 'Para almacenamiento y comparación de vectores')}</li>
            <li><strong>Modelos de traducción (MyMemory API)</strong>: {t('terms.ai.model3', 'Para traducción automática de contenido')}</li>
          </ul>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.ai.processing', '3.2. Procesamiento de datos')}
          </h3>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('terms.ai.processingText', 'Tus búsquedas son procesadas por modelos de IA para:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
            <li>{t('terms.ai.purpose1', 'Convertir tu consulta en representaciones vectoriales (embeddings)')}</li>
            <li>{t('terms.ai.purpose2', 'Comparar semánticamente con documentos indexados')}</li>
            <li>{t('terms.ai.purpose3', 'Mejorar la relevancia de los resultados')}</li>
            <li>{t('terms.ai.purpose4', 'Generar recomendaciones personalizadas')}</li>
          </ul>
        </section>

        {/* 4. Limitaciones y Exclusión de Responsabilidad */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <AlertTriangle className="w-6 h-6 mr-2 text-red-600 dark:text-red-400" />
            {t('terms.disclaimer.title', '4. Limitaciones y Exclusión de Responsabilidad')}
          </h2>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <p className="text-red-900 dark:text-red-200 text-sm font-semibold mb-2">
              {t('terms.disclaimer.medical', 'ADVERTENCIA MÉDICA')}
            </p>
            <p className="text-red-900 dark:text-red-200 text-sm">
              {t('terms.disclaimer.medicalText', 'ClinicCloud NO proporciona asesoramiento médico profesional, diagnósticos ni tratamientos. La información es exclusivamente para fines educativos e informativos. Siempre consulta a un profesional de la salud cualificado para cualquier decisión médica.')}
            </p>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.disclaimer.accuracy', '4.1. Precisión de la información')}
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li>{t('terms.disclaimer.accuracy1', 'Los resultados son generados automáticamente por sistemas de IA')}</li>
            <li>{t('terms.disclaimer.accuracy2', 'No garantizamos la exactitud, integridad o actualidad de la información')}</li>
            <li>{t('terms.disclaimer.accuracy3', 'Los modelos de IA pueden generar resultados incorrectos o sesgados')}</li>
            <li>{t('terms.disclaimer.accuracy4', 'Las traducciones automáticas pueden contener errores')}</li>
          </ul>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.disclaimer.liability', '4.2. Limitación de responsabilidad')}
          </h3>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.disclaimer.liabilityText', 'En ningún caso seremos responsables de daños directos, indirectos, incidentales, especiales o consecuentes que resulten del uso o la imposibilidad de usar este servicio.')}
          </p>
        </section>

        {/* 5. Cuenta de Usuario */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Database className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.account.title', '5. Cuenta de Usuario')}
          </h2>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.account.registration', '5.1. Registro')}
          </h3>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('terms.account.registrationText', 'Para acceder a todas las funcionalidades, debes crear una cuenta proporcionando:')}
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4 mb-4">
            <li>{t('terms.account.data1', 'Dirección de email válida')}</li>
            <li>{t('terms.account.data2', 'Nombre completo')}</li>
            <li>{t('terms.account.data3', 'Contraseña segura')}</li>
          </ul>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {t('terms.account.responsibility', '5.2. Responsabilidad')}
          </h3>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.account.responsibilityText', 'Eres responsable de mantener la confidencialidad de tu cuenta y contraseña, y de todas las actividades que ocurran bajo tu cuenta.')}
          </p>
        </section>

        {/* 6. Propiedad Intelectual */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Copyright className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.ip.title', '6. Propiedad Intelectual')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-3">
            {t('terms.ip.content', 'El contenido indexado proviene de fuentes públicas y pertenece a sus respectivos autores y editoriales. ClinicCloud no reclama propiedad sobre el contenido científico original.')}
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.ip.platform', 'El código, diseño y funcionalidad de la plataforma ClinicCloud están protegidos por derechos de autor.')}
          </p>
        </section>

        {/* 7. Modificaciones */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Edit className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.modifications.title', '7. Modificaciones del Servicio y Términos')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.modifications.text', 'Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios entrarán en vigor inmediatamente después de su publicación. Es tu responsabilidad revisar periódicamente estos términos.')}
          </p>
        </section>

        {/* 8. Terminación */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <XCircle className="w-6 h-6 mr-2 text-red-600 dark:text-red-400" />
            {t('terms.termination.title', '8. Terminación')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.termination.text', 'Podemos suspender o cancelar tu cuenta en cualquier momento si violas estos términos. Puedes cancelar tu cuenta en cualquier momento desde la configuración de tu perfil.')}
          </p>
        </section>

        {/* 9. Ley Aplicable */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Scale className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.law.title', '9. Ley Aplicable y Jurisdicción')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.law.text', 'Estos términos se regirán e interpretarán de acuerdo con las leyes de España y la normativa europea (GDPR). Cualquier disputa se resolverá en los tribunales competentes de España.')}
          </p>
        </section>

        {/* 10. Contacto */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Mail className="w-6 h-6 mr-2 text-primary-600 dark:text-primary-400" />
            {t('terms.contact.title', '10. Contacto')}
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            {t('terms.contact.text', 'Si tienes preguntas sobre estos términos, puedes contactarnos en:')}
          </p>
          <p className="text-primary-600 dark:text-primary-400 mt-2">
            cliniccloud.contact@gmail.com
          </p>
        </section>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-6 mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            {t('terms.footer', 'Al utilizar ClinicCloud, confirmas que has leído, comprendido y aceptado estos Términos y Condiciones.')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;
