"""
Endpoint para reportar problemas o sugerencias.
Envía un email a cliniccloud.contact@gmail.com con el reporte.
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


class ReportIssueRequest(BaseModel):
    """Modelo para la solicitud de reporte de problema"""
    title: str = Field(..., min_length=1, max_length=200, description="Título del problema")
    description: str = Field(..., min_length=10, max_length=5000, description="Descripción detallada")
    contact_email: Optional[EmailStr] = Field(None, description="Email de contacto (opcional si no está autenticado)")
    include_user_info: bool = Field(default=False, description="Incluir información del usuario autenticado")


class ReportIssueResponse(BaseModel):
    """Modelo para la respuesta del reporte"""
    success: bool
    message: str


@router.post("/report-issue", response_model=ReportIssueResponse)
async def report_issue(
    request: ReportIssueRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional)
):
    """
    Envía un reporte de problema a cliniccloud.contact@gmail.com.

    - Si el usuario está autenticado y include_user_info=True, incluye su información
    - Si el usuario no está autenticado, puede proporcionar un email de contacto opcional
    """
    try:
        user_email = None
        user_name = None

        # Debug logging
        logger.info(f"Report issue - current_user: {current_user is not None}, include_user_info: {request.include_user_info}")

        # Si está autenticado y quiere incluir su info
        if current_user and request.include_user_info:
            user_email = current_user.email
            user_name = current_user.name
            logger.info(f"Including user info: {user_name} ({user_email})")

        # Enviar email
        success = email_service.send_issue_report(
            title=request.title,
            description=request.description,
            user_email=user_email,
            user_name=user_name,
            contact_email=request.contact_email if not current_user else None
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el reporte. Por favor, intenta de nuevo más tarde."
            )

        logger.info(f"Issue report sent: {request.title}")

        return ReportIssueResponse(
            success=True,
            message="Reporte enviado correctamente. Gracias por tu feedback."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending issue report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al enviar el reporte"
        )
