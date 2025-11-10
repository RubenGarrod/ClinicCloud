"""
Endpoint para mensajes de contacto.
Envía un email a cliniccloud.contact@gmail.com con el mensaje.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from app.services.email_service import email_service
from app.api.endpoints.auth.dependencies import get_current_user_optional
from app.models.user import UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class ContactRequest(BaseModel):
    """Modelo para la solicitud de contacto"""
    subject: str = Field(..., min_length=1, max_length=200, description="Asunto del mensaje")
    message: str = Field(..., min_length=10, max_length=5000, description="Mensaje")
    email: EmailStr = Field(..., description="Email del remitente")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del remitente")
    user_id: Optional[int] = Field(None, description="ID del usuario (si está autenticado)")


class ContactResponse(BaseModel):
    """Modelo para la respuesta del contacto"""
    success: bool
    message: str


@router.post("/contact", response_model=ContactResponse)
async def send_contact_message(
    request: ContactRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional)
):
    """
    Envía un mensaje de contacto a cliniccloud.contact@gmail.com.

    - Puede ser usado por usuarios autenticados o anónimos
    - Requiere nombre, email, asunto y mensaje
    """
    try:
        # Si está autenticado, usar su ID
        user_id = current_user.id if current_user else request.user_id

        # Enviar email
        success = email_service.send_contact_message(
            subject=request.subject,
            message=request.message,
            email=request.email,
            name=request.name,
            user_id=user_id
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el mensaje. Por favor, intenta de nuevo más tarde."
            )

        logger.info(f"Contact message sent from: {request.email} - Subject: {request.subject}")

        return ContactResponse(
            success=True,
            message="Mensaje enviado correctamente. Te responderemos pronto."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending contact message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al enviar el mensaje"
        )
