"""Envío de mensajes por WhatsApp Cloud API."""
import httpx
from app.config import settings

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"

async def send_whatsapp_message(to_phone: str, message: str, message_type: str = "text"):
    """Envía un mensaje de WhatsApp a un número de teléfono."""
    url = f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json"
    }

    # Formatear número (quitar + si existe)
    to_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()

async def send_whatsapp_template(to_phone: str, template_name: str, language_code: str = "es"):
    """Envía una plantilla aprobada de WhatsApp."""
    url = f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json"
    }

    to_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code}
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()
