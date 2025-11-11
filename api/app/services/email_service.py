"""
Servicio de envío de emails para ClinicCloud.
Soporta diferentes proveedores SMTP configurables via variables de entorno.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuración SMTP desde variables de entorno
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USER)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'ClinicCloud')

# URL base de la aplicación
APP_URL = os.getenv('APP_URL', 'http://localhost:3000')


class EmailService:
    """Servicio para envío de emails usando SMTP"""

    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Envía un email usando SMTP.

        Args:
            to_email: Dirección de email del destinatario
            subject: Asunto del email
            html_body: Cuerpo del email en HTML
            text_body: Cuerpo del email en texto plano (opcional)

        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Validar configuración
            if not self.smtp_user or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                return False

            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Agregar cuerpo de texto plano (fallback para clientes que no soportan HTML)
            if text_body:
                part1 = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(part1)

            # Agregar cuerpo HTML
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part2)

            # Conectar y enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Habilitar encriptación TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """
        Envía email de recuperación de contraseña.

        Args:
            to_email: Email del usuario
            user_name: Nombre del usuario
            reset_token: Token único para resetear la contraseña

        Returns:
            bool: True si se envió correctamente
        """
        reset_link = f"{APP_URL}/reset-password?token={reset_token}"

        subject = "Recuperación de contraseña - ClinicCloud"

        # Cuerpo en texto plano (fallback)
        text_body = f"""
Hola {user_name},

Hemos recibido una solicitud para restablecer tu contraseña en ClinicCloud.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
{reset_link}

Este enlace es válido por 1 hora.

Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje.

Saludos,
El equipo de ClinicCloud
        """

        # Cuerpo en HTML (diseño atractivo)
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperación de contraseña</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <!-- Contenedor principal -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">
                                🔐 Recuperación de Contraseña
                            </h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Hola <strong>{user_name}</strong>,
                            </p>

                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Hemos recibido una solicitud para restablecer tu contraseña en <strong>ClinicCloud</strong>.
                            </p>

                            <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                                Haz clic en el botón de abajo para crear una nueva contraseña:
                            </p>

                            <!-- Botón CTA -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center">
                                        <a href="{reset_link}"
                                           style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">
                                            Restablecer Contraseña
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 30px 0 20px 0; font-size: 14px; line-height: 1.6; color: #666666;">
                                O copia y pega este enlace en tu navegador:
                            </p>

                            <p style="margin: 0 0 30px 0; padding: 12px; background-color: #f5f5f5; border-radius: 4px; font-size: 13px; color: #667eea; word-break: break-all;">
                                {reset_link}
                            </p>

                            <div style="margin: 30px 0 0 0; padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #856404;">
                                    ⏰ <strong>Este enlace es válido por 1 hora.</strong>
                                </p>
                            </div>

                            <p style="margin: 30px 0 0 0; font-size: 14px; line-height: 1.6; color: #666666;">
                                Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje de forma segura.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 8px 8px; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666666;">
                                Saludos,<br>
                                <strong>El equipo de ClinicCloud</strong>
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999999;">
                                © 2025 ClinicCloud. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

        return self._send_email(to_email, subject, html_body, text_body)

    def send_issue_report(
        self,
        title: str,
        description: str,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        contact_email: Optional[str] = None
    ) -> bool:
        """
        Envía un reporte de problema a cliniccloud.contact@gmail.com.

        Args:
            title: Título del problema
            description: Descripción detallada del problema
            user_email: Email del usuario (si está autenticado)
            user_name: Nombre del usuario (si está autenticado)
            contact_email: Email de contacto (si el usuario no está autenticado)

        Returns:
            bool: True si se envió correctamente
        """
        to_email = "cliniccloud.contact@gmail.com"
        subject = f"ISSUE: {title}"

        # Construir información del usuario
        user_info = ""
        if user_name or user_email:
            user_info = "<div style='margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #667eea; border-radius: 4px;'>"
            user_info += "<p style='margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #333;'>Información del usuario:</p>"
            if user_name:
                user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'><strong>Usuario:</strong> {user_name}</p>"
            if user_email:
                user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'><strong>Email:</strong> {user_email}</p>"
            user_info += "</div>"
        elif contact_email:
            user_info = f"<div style='margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #667eea; border-radius: 4px;'>"
            user_info += "<p style='margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #333;'>Email de contacto:</p>"
            user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'>{contact_email}</p>"
            user_info += "</div>"

        # Cuerpo en texto plano (fallback)
        text_body = f"""
REPORTE DE PROBLEMA

Título: {title}

Descripción:
{description}

---
"""
        if user_name or user_email:
            text_body += "\nInformación del usuario:\n"
            if user_name:
                text_body += f"Usuario: {user_name}\n"
            if user_email:
                text_body += f"Email: {user_email}\n"
        elif contact_email:
            text_body += f"\nEmail de contacto: {contact_email}\n"

        # Cuerpo en HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Problema</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <!-- Contenedor principal -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">
                                🚨 Reporte de Problema
                            </h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <div style="margin-bottom: 30px;">
                                <h2 style="margin: 0 0 15px 0; font-size: 20px; font-weight: 600; color: #333333;">
                                    {title}
                                </h2>
                                <div style="padding: 20px; background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #dc3545;">
                                    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #333333; white-space: pre-wrap;">
{description}
                                    </p>
                                </div>
                            </div>

                            {user_info}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 8px 8px; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666666;">
                                <strong>ClinicCloud Issue Report System</strong>
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999999;">
                                © 2025 ClinicCloud. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

        return self._send_email(to_email, subject, html_body, text_body)

    def send_contact_message(
        self,
        subject: str,
        message: str,
        email: str,
        name: str,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Envía un mensaje de contacto a cliniccloud.contact@gmail.com.

        Args:
            subject: Asunto del mensaje
            message: Cuerpo del mensaje
            email: Email del remitente
            name: Nombre del remitente
            user_id: ID del usuario (si está autenticado)

        Returns:
            bool: True si se envió correctamente
        """
        to_email = "cliniccloud.contact@gmail.com"
        email_subject = f"CONTACTO: {subject}"

        # Construir información del usuario
        user_info = "<div style='margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #667eea; border-radius: 4px;'>"
        user_info += "<p style='margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #333;'>Información del remitente:</p>"
        user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'><strong>Nombre:</strong> {name}</p>"
        user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'><strong>Email:</strong> {email}</p>"
        if user_id:
            user_info += f"<p style='margin: 5px 0; font-size: 14px; color: #666;'><strong>User ID:</strong> {user_id}</p>"
        user_info += "</div>"

        # Cuerpo en texto plano (fallback)
        text_body = f"""
MENSAJE DE CONTACTO

Asunto: {subject}

De: {name} ({email})
"""
        if user_id:
            text_body += f"User ID: {user_id}\n"

        text_body += f"""
Mensaje:
{message}

---
"""

        # Cuerpo en HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mensaje de Contacto</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <!-- Contenedor principal -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">
                                📧 Mensaje de Contacto
                            </h1>
                        </td>
                    </tr>

                    <!-- Contenido -->
                    <tr>
                        <td style="padding: 40px;">
                            <!-- Información del remitente -->
                            {user_info}

                            <!-- Asunto -->
                            <div style="margin: 20px 0;">
                                <h2 style="margin: 0 0 10px 0; font-size: 20px; font-weight: 600; color: #333;">
                                    {subject}
                                </h2>
                            </div>

                            <!-- Mensaje -->
                            <div style="margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                                <p style="margin: 0; font-size: 14px; color: #666; white-space: pre-wrap; line-height: 1.6;">
                                    {message}
                                </p>
                            </div>

                            <!-- Responder -->
                            <div style="margin: 30px 0; padding: 20px; background-color: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #1976d2;">
                                    Responder a:
                                </p>
                                <p style="margin: 0; font-size: 14px;">
                                    <a href="mailto:{email}" style="color: #2196f3; text-decoration: none;">{email}</a>
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 8px 8px;">
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999999;">
                                © 2025 ClinicCloud. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

        return self._send_email(to_email, email_subject, html_body, text_body)


# Instancia singleton del servicio
email_service = EmailService()
